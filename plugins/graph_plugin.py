from typing import List
from semantic_kernel.functions import kernel_function

from utils.ms_graph import MsGraph

class GraphPlugin:
    @kernel_function(
        name="get_email_address",
        description="Get an email address based on a users name. Returns one or many email address based on name."
    )
    async def get_email_address(self, name: str) -> str | List[str]:
      with MsGraph() as graph:
        url = f"/users?$filter=startswith(displayName, '{name}')"
        res = graph.get(url)
        email_addresses: List[str] = []
        if res and "value" in res:
            for user in res["value"]:
                display_name: str | None = user["displayName"]
                if display_name and display_name.lower().startswith(name.lower()):
                    email_addresses.append(user["mail"])

        return email_addresses
