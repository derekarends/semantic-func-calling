import os

from semantic_kernel.functions import kernel_function
from utils.ms_graph import MsGraph
from utils.table_storage import TableStorage

class EmailPlugin:
    @kernel_function(
        name="save_email",
        description="Saves an email with the given email address, subject, and content while waiting for approvals."
    )
    def save_email(self, email_address: str, subject: str, content: str):
        with TableStorage() as ts:
            ts.insert_email(email_address=email_address, subject=subject, content=content)
        return "Email saved, pending approval."
    
    @kernel_function(
        name="get_email",
        description="Get an email based on email address. Returns an subject, content, and email address."
    )
    async def get_email(self, email_address: str):
        with TableStorage() as ts:
            email = ts.get_email(email_address=email_address)
            if email:
                return {
                    "subject": email["Subject"],
                    "content": email["Content"],
                    "to": email["Email"]
                }
            
            return "No email found."
    
    @kernel_function(
        name="send_email",
        description="Send an email for a given email address. Email should be approved before sending."
    )
    def send_email(self, email_address: str):
        with TableStorage() as ts:
            email = ts.get_email(email_address=email_address)
            if not email:
                return "No email found to send"
            
        with MsGraph() as graph:
            data = {
                "message": {
                    "subject": email["Subject"],
                    "body": {
                        "contentType": "Text",
                        "content": email["Content"]
                    },
                    "toRecipients": [
                        {
                            "emailAddress": {
                                "address": email_address
                            }
                        }
                    ]
                }
            }

            application_user = os.getenv("APPLICATION_USER")
            response = graph.post(f"/users/{application_user}/sendMail", data)
            if response:
                with TableStorage() as ts:
                    ts.delete_email(email_address=email_address)
                return "Email sent."
            else:
                return "Error sending email."
            
