"""
Manage the Kernel, creates a new one and dynamically import plugins
"""
import os

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
)

from dotenv import load_dotenv
import importlib

load_dotenv()

AZURE_OPENAI_API_TYPE = "azure"
AZURE_OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
AZURE_OPENAI_API_VERSION = "2023-03-15-preview"
AZURE_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv('OPENAI_ADA_EMBEDDING_DEPLOYMENT_NAME')
AZURE_SEARCH_ENDPOINT = os.getenv('AZURE_COGNITIVE_SEARCH_ENDPOINT')
AZURE_SEARCH_KEY = os.getenv('AZURE_COGNITIVE_SEARCH_API_KEY')
AZURE_OPENAI_CHATGPT_DEPLOYMENT = os.getenv("OPENAI_MODEL_NAME")


class myKernel:
         
    def class_instanciation(self,module_name:str, class_name:str):
        """Return a class instance from a string reference"""
        try:
            module_ = importlib.import_module(module_name)
            try:
                class_ = getattr(module_, class_name)()
            except AttributeError:
                print('Class does not exist')
        except ImportError:
            print('Module does not exist')
        return class_ or None    
    
    def updateKernel(self,plugins:dict) :    
           
        kernel = sk.Kernel()
        kernel.add_chat_service(
            "azureopenai",
            AzureChatCompletion(
                deployment_name=AZURE_OPENAI_CHATGPT_DEPLOYMENT,
                endpoint=AZURE_OPENAI_API_BASE,
                api_key=AZURE_OPENAI_API_KEY,
            ),
        )

        variables = sk.ContextVariables()
        variables["chat_history"] = ""
        for plugin in plugins:
            for className, module in plugin.items():
                class_instiaton = self.class_instanciation(module,className)
                print(class_instiaton)
                kernel.import_skill(class_instiaton)
                
        plugins_directory = "./plugins"
        kernel.import_semantic_skill_from_directory(plugins_directory, "sherlockPlugin")
        print(kernel._skill_collection.json())
        
        return kernel, variables
        
            
        
