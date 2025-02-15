
import structlog

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config.app_config import app_config

LOG = structlog.get_logger()


class SlackService:
    def __init__(self):
        self.slack_client = WebClient(token=app_config.SLACK_BOT_TOKEN)

    def send_message(self, channel: str, text: str, thread_ts: str = None):
        try:
            if not text:
                return
            self.slack_client.chat_postMessage(
                channel=channel, text=text, thread_ts=thread_ts
            )
        except SlackApiError as e:
            LOG.error(f"Error sending message: {e.response['error']}")

    def get_last_messages(self, channel, num_messages=5):
        try:
            response = self.slack_client.conversations_history(
                channel=channel, limit=num_messages
            )
            return response["messages"]
        except SlackApiError as e:
            LOG.error(f"Error fetching messages: {e.response['error']}")
            return []

    def get_last_messages_with_bot_replies(self, channel, num_messages=5):
        final_messages = list()
        try:
            last_messages = self.get_last_messages(
                channel=channel, num_messages=num_messages
            )

            for message in last_messages:
                formatted_message = {
                    "is_bot": message.get("bot_id") is not None,
                    "text": message.get("text", ""),
                    "replies": list(),
                }
                if message.get("thread_ts"):
                    replies = self.slack_client.conversations_replies(
                        channel=channel, ts=message["thread_ts"]
                    ).get("messages", [])
                    for reply in replies:
                        if reply.get("bot_id") is not None:
                            formatted_reply = {
                                "is_bot": reply.get("bot_id") is not None,
                                "text": reply.get("text", ""),
                            }
                            formatted_message["replies"].append(formatted_reply)
                final_messages.append(formatted_message)
            # reverse the list to get the latest messages first
            final_messages.reverse()
            return final_messages
        except SlackApiError as e:
            LOG.error(f"Error fetching messages: {e.response['error']}")
            return []
