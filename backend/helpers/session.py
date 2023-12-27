from langchain.memory.chat_message_histories import CosmosDBChatMessageHistory
import os

def setSession(session):
    cosmos = CosmosDBChatMessageHistory(
                        cosmos_endpoint=os.environ['AZURE_COSMOSDB_ENDPOINT'],
                        cosmos_database=os.environ['AZURE_COSMOSDB_NAME'],
                        cosmos_container=os.environ['AZURE_COSMOSDB_CONTAINER_NAME'],
                        connection_string=os.environ['AZURE_COMOSDB_CONNECTION_STRING'],
                        session_id=session,
                        user_id="myUser"
                    )
    cosmos.prepare_cosmos()
    return cosmos