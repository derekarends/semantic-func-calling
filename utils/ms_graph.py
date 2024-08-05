import os
import requests
import msal # type: ignore

from typing import Any, Dict, Optional

class MsGraph:
  def __init__(self):
    self.client_id = os.getenv("CLIENT_ID")
    self.client_secret = os.getenv("CLIENT_SECRET")
    self.tenant_id = os.getenv("TENANT_ID")
    self.token: Dict[str, Any] | None = None

  def __enter__(self):
    AUTHORITY = f"https://login.microsoftonline.com/{self.tenant_id}"
    SCOPE = ["https://graph.microsoft.com/.default"]

    app = msal.ConfidentialClientApplication(
        client_id=self.client_id,
        authority=AUTHORITY,
        client_credential=self.client_secret,
    )
    self.token = app.acquire_token_for_client(scopes=SCOPE) # type: ignore
    return self
  
  def __exit__(self, exc_type: str, exc_val: str, exc_tb: str):
    pass

  def get_access_token(self) -> Optional[str]:
      if self.token and "access_token" in self.token:
          return self.token["access_token"]
      return None
  
  def get(self, endpoint: str) -> Optional[Dict[Any, Any]]:
        access_token = self.get_access_token()
        if not access_token:
            return None

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"https://graph.microsoft.com/v1.0{endpoint}", headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.json())
            return None
  

  def post(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[Any, Any]]:
        access_token = self.get_access_token()
        if not access_token:
            return None

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        response = requests.post(f"https://graph.microsoft.com/v1.0{endpoint}", headers=headers, json=data)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 202:
            return {"status": "success"}
        else:
            print(f"Error: {response.status_code}")
            print(response.json())
            return None