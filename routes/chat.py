import json

from typing import Any, Dict

from plugins.email_plugin import EmailPlugin
from plugins.graph_plugin import GraphPlugin
from utils.kernel_wrapper import KernelWrapper

async def chat(chat_id: str, message: str) -> str:
    """
    Chat route for the function
    
    Args:
        chat_id (str): Chat id
        message (str): Message
        kernel (Kernel): Kernel object
        
    Returns:
        str: Response
    """
    kw = (
        KernelWrapper()
          .add_plugin(EmailPlugin(), plugin_name="EmailPlugin")
          .add_plugin(GraphPlugin(), plugin_name="GraphPlugin")
    )
    response = await kw.completion(chat_id=chat_id, message=message)

    res: Dict[str, Any] = {
        "response": response,
    }
    return json.dumps(res)