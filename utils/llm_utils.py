import os
import structlog

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from config.app_config import app_config

LOG = structlog.get_logger()

os.environ["GOOGLE_API_KEY"] = app_config.GOOGLE_API_KEY


class LLMUtils:
    # Ensure your VertexAI credentials are configured
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model=app_config.GEMINI_MODEL, temperature=0.5, max_retries=2
        )

    def generate_response(self, context_messages=[]):
        messages: list[SystemMessage | HumanMessage | AIMessage] = [
            SystemMessage(content="You are a helpful assistant.")
        ] + context_messages
        # messages.append(HumanMessage(content=user_input))

        # Get LLM response
        response = self.model.invoke(messages)

        return response.content

    @staticmethod
    def generate_context_messages_from_history(history: list[dict]):
        context_messages = list()
        for message in history:
            context_messages.append(HumanMessage(content=message["text"]))
            message_replies = message.get("replies", [])
            for reply in message_replies:
                if reply["is_bot"]:
                    context_messages.append(AIMessage(content=reply["text"]))
                else:
                    context_messages.append(HumanMessage(content=reply["text"]))

        return context_messages


# Example usage
if __name__ == "__main__":
    llm_service = LLMUtils()
    context = [
        AIMessage(content="Hello! How can I assist you today?"),
        HumanMessage(content="Can you summarize climate change effects?"),
        AIMessage(
            content="Sure! Climate change leads to rising temperatures, extreme weather, and sea level rise."
        ),
    ]

    user_query = "How can we prevent it?"
    response = llm_service.generate_response(user_query, context)

    LOG.info("Bot response", response=response)
