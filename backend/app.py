from flask import Flask, send_from_directory
from dotenv import load_dotenv
from flask_cors import CORS
import os

from langchain.memory.chat_message_histories import CosmosDBChatMessageHistory
from routes_semantic.chatHistory import chatHistory
from routes_semantic.chatGeneration import chatGeneration
from routes_semantic.indexManagement import indexManagement

load_dotenv('.env') 

app = Flask(__name__, static_folder="../frontend/dist")
CORS(app)  # Enable CORS for all routes


# Static Files
@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file('favicon.ico')

@app.route("/assets/<path:path>")
def assets(path):
    return send_from_directory("../frontend/dist/assets", path)

cosmos = CosmosDBChatMessageHistory(
                    cosmos_endpoint=os.environ['AZURE_COSMOSDB_ENDPOINT'],
                    cosmos_database=os.environ['AZURE_COSMOSDB_NAME'],
                    cosmos_container=os.environ['AZURE_COSMOSDB_CONTAINER_NAME'],
                    connection_string=os.environ['AZURE_COMOSDB_CONNECTION_STRING'],
                    session_id='session',
                    user_id="myUser"
                )
cosmos.prepare_cosmos()

app.config['cosmos'] = cosmos
app.register_blueprint(chatHistory)
app.register_blueprint(chatGeneration)
app.register_blueprint(indexManagement)


if __name__ == "__main__":
    app.run()