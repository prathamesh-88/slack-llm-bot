import json
import time
import requests
import structlog

from flask import Flask, request, jsonify, redirect
from services.slack_service import SlackService
from utils.llm_utils import LLMUtils
from config.app_config import app_config

LOG = structlog.get_logger()

app = Flask(__name__)
llm_utils = LLMUtils()

# TODO: Move this to a persistent store
installed_workspaces = {}
tasks_under_progress = set()


@app.route("/ping", methods=["GET"])
def ping():
    return "pong"


@app.route("/slack/events", methods=["POST"])
def slack_events():
    thread_ts = None
    start_time = time.time()
    try:
        data = request.json

        # Slack challenge verification
        if "challenge" in data:
            return jsonify({"challenge": data["challenge"]}), 200

        # Process messages when the bot is mentioned
        if "event" in data and data["event"]["type"] == "app_mention":
            LOG.info("Received app_mention event", data=data)
            team_id = data["team_id"]
            event = data["event"]
            channel = event["channel"]
            user_message = event["text"]

            workspace_info = installed_workspaces.get(team_id)
            if not workspace_info:
                return jsonify({"error": "Workspace not found"}), 400
            access_token = workspace_info["access_token"]

            thread_ts = event.get("thread_ts", event["ts"])
            if thread_ts in tasks_under_progress:
                LOG.info("Task already in progress", thread_ts=thread_ts)
                return jsonify({"error": "Task already in progress"}), 200
            tasks_under_progress.add(thread_ts)
            LOG.info(
                "Received message",
                channel=channel,
                message=user_message,
                thread_ts=thread_ts,
            )

            # Get last 5 messages
            slack_service = SlackService(bot_token=access_token)
            history = slack_service.get_last_messages_with_bot_replies(channel)
            LOG.info("Last 5 messages", history=json.dumps(history))
            # TODO: Handle case where no messages are found
            if not history:
                return jsonify({"error": "No messages found"}), 400
            llm_context = llm_utils.generate_context_messages_from_history(history)
            LOG.info("LLM context", context=llm_context)

            # Generate response using AI
            response = llm_utils.generate_response(llm_context)
            LOG.info("Generated response", response=response)

            # Send response back
            slack_service.send_message(channel, response, thread_ts)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        LOG.error("Error processing Slack event", error=str(e))
        return jsonify({"success": False, "error": "Error processing Slack event"}), 500
    finally:
        LOG.info("Processed Slack event", time_taken=time.time() - start_time)
        if thread_ts and thread_ts in tasks_under_progress:
            tasks_under_progress.remove(thread_ts)


@app.route("/slack/install")
def slack_install():
    """Redirects user to Slack OAuth authorization page."""
    try:
        slack_auth_url = (
            f"https://slack.com/oauth/v2/authorize"
            f"?client_id={app_config.SLACK_CLIENT_ID}"
            f"&scope=app_mentions:read,channels:history,channels:join,chat:write"
            f"&redirect_uri={app_config.SLACK_REDIRECT_URI}"
        )
        return redirect(slack_auth_url)

    except Exception as e:
        LOG.error("Error installing Slack app", error=str(e))
        return jsonify({"success": False, "error": "Error installing Slack app"}), 500


@app.route("/slack/oauth/callback")
def slack_oauth_callback():
    try:
        """Handles the OAuth callback and exchanges code for access token."""
        code = request.args.get("code")
        if not code:
            return jsonify({"error": "Authorization code not found"}), 400

        # Exchange code for access token
        token_url = "https://slack.com/api/oauth.v2.access"
        payload = {
            "client_id": app_config.SLACK_CLIENT_ID,
            "client_secret": app_config.SLACK_CLIENT_SECRET,
            "code": code,
            "redirect_uri": app_config.SLACK_REDIRECT_URI,
        }
        response = requests.post(token_url, data=payload)
        data = response.json()

        if not data.get("ok"):
            return jsonify({"error": data.get("error", "OAuth failed")}), 400

        # Store the access token and team info
        team_id = data["team"]["id"]
        installed_workspaces[team_id] = {
            "access_token": data["access_token"],
            "team_name": data["team"]["name"],
        }

        return (
            jsonify({"message": "App installed successfully", "team": data["team"]}),
            200,
        )
    except Exception as e:
        LOG.error("Error installing Slack app", error=str(e))
        return (
            jsonify({"success": False, "error": "Error validating OAuth request"}),
            500,
        )


# TODO: Remove this endpoint when not needed anymore
# @app.route("/slack/workspaces")
# def list_workspaces():
#     return jsonify(installed_workspaces)


if __name__ == "__main__":
    # Development only - Runs with gunicorn in production
    app.run(port=app_config.PORT, debug=app_config.DEBUG_MODE)
