import json
import structlog

from flask import Flask, request, jsonify
from services.slack_service import SlackService
from utils.llm_utils import LLMUtils
from config.app_config import app_config

LOG = structlog.get_logger()

app = Flask(__name__)

slack_service = SlackService()
llm_utils = LLMUtils()


@app.route("/ping", methods=["GET"])
def ping():
    return "pong"


@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json

    # Slack challenge verification
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]}), 200

    # Process messages when the bot is mentioned
    if "event" in data and data["event"]["type"] == "app_mention":
        event = data["event"]
        channel = event["channel"]
        user_message = event["text"]
        thread_ts = event.get("thread_ts", event["ts"])
        LOG.info(
            "Received message",
            channel=channel,
            message=user_message,
            thread_ts=thread_ts,
        )

        # Get last 5 messages
        history = slack_service.get_last_messages_with_bot_replies(channel)
        LOG.info("Last 5 messages", history=json.dumps(history))
        llm_context = llm_utils.generate_context_messages_from_history(history)
        LOG.info("LLM context", context=llm_context)

        # Generate response using AI
        response = llm_utils.generate_response(llm_context)
        LOG.info("Generated response", response=response)

        # Send response back
        slack_service.send_message(channel, response, thread_ts)

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(port=app_config.PORT, debug=app_config.DEBUG_MODE)
