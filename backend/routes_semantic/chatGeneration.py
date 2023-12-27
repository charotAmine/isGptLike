from flask import Blueprint, request, jsonify, current_app
from helpers.session import setSession
import re
from langchain.memory import ConversationBufferWindowMemory
from models.bot import bot
from models.kernelManagement import myKernel
import json
import tempfile
import shutil
import zipfile
import os

chatGeneration = Blueprint('chatGeneration', __name__)

chatbot = bot(None,None)
json_file_path = './plugins/plugins.json'
with open(json_file_path, 'r') as file:
    default_data = json.load(file)
current_data = default_data.copy()

def convert_to_desired_format(data):
    return [{item['className']: item['moduleName']} for item in data if item.get('enable', False)]

def extract_and_search(zip_file_path, extract_to_directory):
    # Get the base name of the zip file (excluding extension)
    zip_base_name = os.path.splitext(os.path.basename(zip_file_path))[0]

    # Open the zip file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        # Extract all the contents of the zip file into the specified directory
        zip_ref.extractall(extract_to_directory)

    # Find the Python file with the .py extension in the extracted directory
    python_files = [f for f in os.listdir(f"{extract_to_directory}/{zip_base_name}") if f.endswith('.py')]

    if not python_files:
        print("No Python file (.py) found in the extracted folder.")
        return

    # Assume the first Python file found is the one you want to analyze
    python_file_name = python_files[0]
    python_file_path = os.path.join(extract_to_directory,zip_base_name, python_file_name)

    print(f"File extracted to: {python_file_path}")

    # Read the content of the Python file
    with open(python_file_path, 'r') as file:
        content = file.read()

        # Use regular expression to find class names
        class_names = re.findall(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)

        print(f"Class names in {python_file_path}: {class_names}")
    
    return python_file_path.replace("./","").replace("\\",".").replace(".py",""), class_names[0]
        
@chatGeneration.route("/generateAnswer", methods=["GET","POST"])
async def generateAnswer():
    data = request.get_json()
    message = data['prompt']
    session_id = data['sessionId']   
    index_name = data['indexValue']
    
    cosmos = current_app.config['cosmos']   
    if(session_id != cosmos.session_id):
        cosmosUpdated = setSession(session_id)
        print("New session ! ")
        chat_history = None
    memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True, k=30, chat_memory=cosmosUpdated)
    memory.chat_memory.add_user_message(message)
    
    response = await chatbot.ask(index_name, message, chat_history)   
    memory.chat_memory.add_ai_message(response)
    response = {"Answer": response}
    print(response)
    return jsonify(response), 200

@chatGeneration.route("/updatePlugins", methods=["GET","POST"])
async def updatePlugins():
    global current_data
    global chatbot 
    json_file_path = './plugins/plugins.json'
    if request.method == 'GET':
        with open(json_file_path, 'r') as file:
            default_data = json.load(file)
            current_data = default_data.copy()
        return jsonify({"plugins": current_data}), 200

    elif request.method == 'POST':
        
        new_data = request.json
        plugins = convert_to_desired_format(new_data)
        print(plugins)
        newKernel = myKernel()        
        kernel, variables = newKernel.updateKernel(plugins)      
        chatbot = bot(kernel, variables)
        
        if new_data is not None:
            for item in current_data:
                for new_item in new_data:
                    if item['moduleName'] == new_item['moduleName']:
                        item['enable'] = new_item.get('enable', item['enable'])

            with open(json_file_path, 'w') as file:
                json.dump(current_data, file, indent=2)              
            return jsonify({"plugins": current_data}), 200
        else:
            return jsonify({"error": "Received null data"}), 400

@chatGeneration.route('/importPlugin', methods=['POST'])
async def import_plugin():
    files = request.files.getlist('files')
    plugin_name = request.form.get('pluginName')
    plugin_description = request.form.get('pluginDescription')
    temp_dir = tempfile.mkdtemp()

    try:
        for file in files:
            file.save(f'{temp_dir}/{file.filename}')
            extract_to_directory = './plugins'
            module_name,class_name = extract_and_search(f'{temp_dir}/{file.filename}',extract_to_directory)
            
        json_file_path = './plugins/plugins.json'
        with open(json_file_path, 'r') as file:
            default_data = json.load(file)
        current_data = default_data.copy()
        plugin = {
            "displayName" : f'{plugin_name}',
            "description" : f'{plugin_description}',
            "moduleName" : f'{module_name}',
            "className" : f'{class_name}',
            "enable" : False
        }
        current_data.append(plugin)
        
        with open(json_file_path, 'w') as file:
            json.dump(current_data, file, indent=2) 
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        shutil.rmtree(temp_dir)

    return jsonify({'message': 'Files uploaded successfully', 'name': plugin_name})