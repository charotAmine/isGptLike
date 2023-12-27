from flask import Blueprint, request, jsonify
import tempfile
import shutil
from models.memoryManagerStore import memoryManagerStore

indexManagement = Blueprint('indexManagement', __name__)

memory_manager = memoryManagerStore()

@indexManagement.route('/createIndex', methods=['POST'])
async def upload_files():
    files = request.files.getlist('files')
    index_name = request.form.get('name')
    temp_dir = tempfile.mkdtemp()

    try:
        for file in files:
            file.save(f'{temp_dir}/{file.filename}')

        await memory_manager.initialize(index_name, temp_dir)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        shutil.rmtree(temp_dir)

    return jsonify({'message': 'Files uploaded successfully', 'name': index_name})

@indexManagement.route('/list_indexes', methods=['GET'])
def list_indexes():
    index_names = memory_manager.list_indexes()
    return jsonify(index_names)
