import azure.functions as func
import logging

from routes.chat import chat
from routes.check_inbox import check_inbox

# Create a function app
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Define a route for the function
@app.route(route="health_check")
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    return func.HttpResponse(
          "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
          status_code=200
    )

@app.function_name(name="inboxchecker")
@app.timer_trigger(schedule="0 */5 * * * *", arg_name="inboxchecker") 
async def check_inbox_route(inboxchecker: func.TimerRequest) -> None:
    await check_inbox(past_due=inboxchecker.past_due)


@app.route(route="chat", methods=["POST"])
async def chat_route(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Get the request body
    req_body = req.get_json()
    chat_id = req_body.get("chatId")
    message = req_body.get("message")

    res = await chat(chat_id=chat_id, message=message)
    return func.HttpResponse(res, status_code=200)
