from flask import Blueprint, request, jsonify
import os
from langchain.document_loaders import TextLoader
from langchain.document_loaders.json_loader import JSONLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import AzureSearch
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from routes.chatHistory import chatHistory
from routes.chatGeneration import chatGeneration
import tempfile

indexManagement = Blueprint('indexManagement', __name__)

def get_loader(file_path):
    # Determine the file format based on the file extension or content
    file_format = determine_file_format(file_path)

    # Create and return the appropriate loader instance
    if file_format == 'json':
        return JSONLoader(file_path,".",text_content=False)
    elif file_format == 'text':
        print("is text")
        return TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file format: {file_format}")

def determine_file_format(file_path):
    # Implement logic to determine file format based on file extension or content
    # You can use libraries like mimetypes or implement custom logic
    file_extension = file_path.split('.')[-1].lower()

    if file_extension == 'json':
        return 'json'
    elif file_extension in ['txt', 'csv']:
        return 'text'
    else:
        # Add additional formats as needed
        raise ValueError(f"Unsupported file extension: {file_extension}")


@indexManagement.route('/list_indexes', methods=['GET'])
def list_indexes():
    try:
        endpoint = os.getenv('AZURE_COGNITIVE_SEARCH_ENDPOINT')
        credential = os.getenv('AZURE_COGNITIVE_SEARCH_API_KEY')

        search_service_client = SearchIndexClient(endpoint, AzureKeyCredential(credential))
        indexes = search_service_client.list_index_names()

        index_names = [index for index in indexes]
        print(jsonify(index_names))
        return jsonify(index_names)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@indexManagement.route('/createIndex', methods=['POST'])
def upload_files():
    files = request.files.getlist('files')
    index_name = request.form.get('name')
    docs = []
    temp_dir = tempfile.mkdtemp()
    try:
        for file in files:
            file.save(f'{temp_dir}/{file.filename}')
        print(f"Temporary directory {temp_dir} has been created and processed.")
        for dirpath, dirnames, filenames in os.walk(temp_dir):
            for file in filenames:
                try:                    
                    #loader = TextLoader(os.path.join(dirpath, file), encoding="utf-8")
                    loader = get_loader(os.path.join(dirpath, file))
                    docs.extend(loader.load_and_split())
                except Exception as e:
                    print(e)
                    pass
                text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                texts = text_splitter.split_documents(docs)
                embeddings=OpenAIEmbeddings(deployment=os.getenv('OPENAI_ADA_EMBEDDING_DEPLOYMENT_NAME'),
                                                model=os.getenv('OPENAI_ADA_EMBEDDING_MODEL_NAME'),
                                                openai_api_base=os.getenv('OPENAI_API_BASE'),
                                                openai_api_type="azure",
                                                chunk_size=1,
                                                max_retries=20)

                acs = AzureSearch(azure_search_endpoint=os.getenv('AZURE_COGNITIVE_SEARCH_ENDPOINT'),
                                azure_search_key=os.getenv('AZURE_COGNITIVE_SEARCH_API_KEY'),
                                index_name=index_name,
                                embedding_function=embeddings.embed_query)

                acs.add_documents(documents=texts)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up: Remove the temporary directory and its contents
        import shutil
        shutil.rmtree(temp_dir)

    return jsonify({'message': 'Files uploaded successfully', 'name': index_name})