'''
Used to manage the Indexes. This useful to load the indexes & Create the indexes
'''
import os
import ntpath
from dotenv import load_dotenv
import semantic_kernel as sk
from langchain.document_loaders import DirectoryLoader
from semantic_kernel.connectors.ai.open_ai import OpenAITextEmbedding
from semantic_kernel.connectors.memory.azure_cognitive_search import (
    AzureCognitiveSearchMemoryStore,
)
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from langchain.text_splitter import CharacterTextSplitter

class memoryManagerStore:
    def __init__(self):
        load_dotenv()
        self.AZURE_OPENAI_API_TYPE = "azure"
        self.AZURE_OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
        self.AZURE_OPENAI_API_VERSION = "2023-03-15-preview"
        self.AZURE_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv('OPENAI_ADA_EMBEDDING_DEPLOYMENT_NAME')
        self.AZURE_SEARCH_ENDPOINT = os.getenv('AZURE_COGNITIVE_SEARCH_ENDPOINT')
        self.AZURE_SEARCH_KEY = os.getenv('AZURE_COGNITIVE_SEARCH_API_KEY')

        self.memory_store = AzureCognitiveSearchMemoryStore(1536,self.AZURE_SEARCH_ENDPOINT,self.AZURE_SEARCH_KEY)

    def load_and_split_documents(self, data_dir) -> list[dict]:
        loader = DirectoryLoader(
            data_dir, show_progress=True
        )
        docs = loader.load()
        
        splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        split_docs = splitter.split_documents(docs)
        
        final_docs = []
        for i, doc in enumerate(split_docs):
            doc_dict = {
                "id": str(i),
                "content": doc.page_content,
                "sourcefile": ntpath.basename(doc.metadata["source"]),
            }
            final_docs.append(doc_dict)
        return final_docs

    async def initialize(self, index_name, data_dir):
        docs = self.load_and_split_documents(data_dir)
        kernel = sk.Kernel()
        kernel.add_text_embedding_generation_service(
            "openai-embedding",
            OpenAITextEmbedding(
                model_id=self.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
                api_key=self.AZURE_OPENAI_API_KEY,
                endpoint=self.AZURE_OPENAI_API_BASE,
                api_type=self.AZURE_OPENAI_API_TYPE,
                api_version=self.AZURE_OPENAI_API_VERSION,
            ),
        )
        kernel.register_memory_store(self.memory_store)
        for doc in docs:
            await kernel.memory.save_information_async(index_name, id=doc["id"], text=doc["content"])

    def delete(self, index_name):
        self.memory_store.delete_collection_async(index_name)

    def list_indexes(self):
        try:
            endpoint = self.AZURE_SEARCH_ENDPOINT
            credential = self.AZURE_SEARCH_KEY
            search_service_client = SearchIndexClient(endpoint, AzureKeyCredential(credential))
            indexes = search_service_client.list_index_names()
            index_names = [index for index in indexes]
            return index_names
        except Exception as e:
            return None