from typing import Any, Dict, List
import uuid
import os

from azure.data.tables import TableServiceClient, UpdateMode
from azure.core.exceptions import ResourceExistsError

class TableStorage:
    def __init__(self) -> None:
        self.connection_string = os.getenv("STORAGE_CONNECTION_STRING")
        assert self.connection_string is not None

        self.table_service_client = TableServiceClient.from_connection_string(conn_str=self.connection_string)
        self.chat_history_client = self.table_service_client.get_table_client(table_name="ChatHistory")
        self.email_client = self.table_service_client.get_table_client(table_name="Emails")
        self.create_table_if_not_exists()

    def __enter__(self) -> 'TableStorage':
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        # Perform any necessary cleanup here
        pass

    def create_table_if_not_exists(self):
        try:
          self.chat_history_client.create_table()  # type: ignore
        except ResourceExistsError as e:
          print(e)

        try:
          self.email_client.create_table()  # type: ignore
        except ResourceExistsError as e:
          print(e)
            
    def upsert_chat_history(self, chat_id: str, role: str, message: str):
        history_count = len(self.get_chat_history(chat_id))
        entity: Dict[str, Any] = {
            "PartitionKey": chat_id,
            "RowKey": str(history_count),
            "Role": role,
            "Message": message
        }

        self.chat_history_client.upsert_entity(entity=entity, mode=UpdateMode.REPLACE) # type: ignore

    def get_chat_history(self, chat_id: str) -> List[Dict[str, Any]]:
        entities = self.chat_history_client.query_entities(query_filter=f"PartitionKey eq '{chat_id}'") # type: ignore
        sorted_entities = sorted(entities, key=lambda entity: entity["RowKey"]) # type: ignore
        return [entity for entity in sorted_entities]


    def insert_email(self, email_address: str, subject: str, content: str):
        entity: Dict[str, Any] = {
            "PartitionKey": "email",
            "RowKey": str(uuid.uuid4()),
            "Email": email_address,
            "Subject": subject,
            "Content": content
        }

        self.email_client.upsert_entity(entity=entity, mode=UpdateMode.REPLACE) # type: ignore


    def get_email(self, email_address: str | None) -> Dict[str, Any] | None:
        if email_address is None:
            return None
        
        query_filter = f"PartitionKey eq 'email' and Email eq '{email_address}'"
        entities = self.email_client.query_entities(query_filter=query_filter) # type: ignore
        for entity in entities:
            if entity["Email"] == email_address:
                return entity
        return None

    def delete_email(self, email_address: str):
        query_filter = f"PartitionKey eq 'email' and Email eq '{email_address}'"
        entities = self.email_client.query_entities(query_filter=query_filter) # type: ignore
        for entity in entities:
            self.email_client.delete_entity(partition_key=entity["PartitionKey"], row_key=entity["RowKey"]) # type: ignore
        return None