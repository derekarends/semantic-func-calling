import json
from typing import Any, Dict
import azure.functions as func
import logging
import os

from semantic_kernel import Kernel
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)

from plugins.email_plugin import EmailPlugin
from plugins.graph_plugin import GraphPlugin
from utils.table_storage import TableStorage


# Create a function app
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Create a kernel
kernel = Kernel(
    services=[
        AzureChatCompletion(
          deployment_name=os.getenv("DEPLOYMENT_NAME"),
          api_key=os.getenv("API_KEY"),
          endpoint=os.getenv("ENDPOINT")
      )
    ]
)
kernel.add_plugin(GraphPlugin(), plugin_name="GraphPlugin")
kernel.add_plugin(EmailPlugin(), plugin_name="EmailPlugin")

# Define a route for the function
@app.route(route="health_check")
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    return func.HttpResponse(
          "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
          status_code=200
    )

@app.route(route="chat", methods=["POST"])
async def chat(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Get the request body
    req_body = req.get_json()
    chat_id = req_body.get("chatId")
    message = req_body.get("message")

    chat_completion = kernel.get_service(type=ChatCompletionClientBase)
    
    # Enable planning
    execution_settings = AzureChatPromptExecutionSettings(tool_choice="auto") # type: ignore
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto(auto_invoke=True, filters={}) # type: ignore

    chat_history = ChatHistory()
    chat_history.add_system_message("You are a helpful assistant. If you are uncertain of any action, ask for help.")
    
    with TableStorage() as ts:
      ch = ts.get_chat_history(chat_id=chat_id)
      for entity in ch:
        role = AuthorRole[entity["Role"]]
        if role == AuthorRole.SYSTEM:
            continue
        elif role == AuthorRole.USER:
            chat_history.add_user_message(entity["Message"])
        elif role == AuthorRole.ASSISTANT:
            chat_history.add_assistant_message(entity["Message"])
        elif role == AuthorRole.TOOL:
            chat_history.add_tool_message(entity["Message"])
        else:
            print("Unknown role")

      chat_history.add_user_message(message)
      ts.upsert_chat_history(chat_id=chat_id, role=AuthorRole.USER.name, message=message)

      response: ChatMessageContent = (await chat_completion.get_chat_message_contents( # type: ignore
          kernel=kernel,
          settings=execution_settings,
          chat_history=chat_history,
      ))[0]

      ts.upsert_chat_history(chat_id=chat_id, role=AuthorRole.ASSISTANT.name, message=response.content) # type: ignore

    res: Dict[str, Any] = {
        "response": response.content, # type: ignore
    }
    return func.HttpResponse(json.dumps(res), status_code=200)
