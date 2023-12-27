from flask import Blueprint, request, jsonify,current_app
from helpers.session import setSession
from langchain.memory import ConversationBufferWindowMemory

chatHistory = Blueprint('api', __name__)

def load_all_messages(self) -> None:
        """Retrieve the messages from Cosmos"""
        if not self._container:
            raise ValueError("Container not initialized")
        try:
            from azure.cosmos.exceptions import (  # pylint: disable=import-outside-toplevel # noqa: E501
                CosmosHttpResponseError,
            )
        except ImportError as exc:
            raise ImportError(
                "You must install the azure-cosmos package to use the CosmosDBChatMessageHistory."  # noqa: E501
                "Please install it with `pip install azure-cosmos`."
            ) from exc
        try:
            datas = []
            items =  self._container.query_items(
                query='SELECT c.id,c.messages FROM c',
                partition_key=self.user_id
            )
            for item in items:
                datas.append(item)
        except CosmosHttpResponseError:
            return
        return datas

@chatHistory.route("/getChatHistory", methods=["GET"])
def getChatHistory():
    cosmos = current_app.config['cosmos']
    messages = load_all_messages(cosmos)
    allMessages = []
    for entries in messages:
        converted_data = []
        msgs = entries['messages']
        for entry in msgs:
            content = entry['data']['content']
            sender = 'user' if entry['type'] == 'human' else 'ai'
            converted_entry = {'text': content, 'sender': sender}
            converted_data.append(converted_entry)
        allEntries = {'sessionId': entries['id'], 'entries': converted_data}
        allMessages.append(allEntries)

    response = {"messages": allMessages}
    return jsonify(response), 200

@chatHistory.route("/clearChat", methods=["DELETE"])
def clearChat():
    cosmos = current_app.config['cosmos']
    data = request.get_json()
    sessionId = data['sessionId']   
    if(sessionId != cosmos.session_id):
        cosmosUpdated = setSession(sessionId)
        print("New session ! ")
    else:
        cosmosUpdated=cosmos
    memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True, k=30, chat_memory=cosmosUpdated)
   
    response = {"Answer": "done"}
        
    memory.chat_memory.clear()

    return jsonify(response), 200