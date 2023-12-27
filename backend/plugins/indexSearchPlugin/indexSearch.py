from semantic_kernel.skill_definition import (
    sk_function,
    sk_function_context_parameter,
)
from semantic_kernel.orchestration.sk_context import SKContext
from semantic_kernel import Kernel,ContextVariables
from semantic_kernel.skill_definition import (
    sk_function,
)
from semantic_kernel.orchestration.sk_context import SKContext
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
    OpenAITextEmbedding,
)
from semantic_kernel.connectors.memory.azure_cognitive_search import (
    AzureCognitiveSearchMemoryStore,
)

import os
from dotenv import load_dotenv
load_dotenv()

AZURE_OPENAI_API_TYPE = "azure"
AZURE_OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
AZURE_OPENAI_API_VERSION = "2023-03-15-preview"
AZURE_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv('OPENAI_ADA_EMBEDDING_DEPLOYMENT_NAME')
AZURE_SEARCH_ENDPOINT = os.getenv('AZURE_COGNITIVE_SEARCH_ENDPOINT')
AZURE_SEARCH_KEY = os.getenv('AZURE_COGNITIVE_SEARCH_API_KEY')
AZURE_OPENAI_CHATGPT_DEPLOYMENT = os.getenv("OPENAI_MODEL_NAME")

class IndexSearch:
    
    async def get_context(self, query: str,index_name: str) -> list[str]:
        """
        Gets the relevant documents from Azure Cognitive Search.
        """
        kernel = Kernel()
        kernel.add_text_embedding_generation_service(
            "openai-embedding",
            OpenAITextEmbedding(
                model_id=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
                api_key=AZURE_OPENAI_API_KEY,
                endpoint=AZURE_OPENAI_API_BASE,
                api_type=AZURE_OPENAI_API_TYPE,
                api_version=AZURE_OPENAI_API_VERSION,
            ),
        )
        kernel.register_memory_store(
            memory_store=AzureCognitiveSearchMemoryStore(
                vector_size=1536,
                search_endpoint=AZURE_SEARCH_ENDPOINT,
                admin_key=AZURE_SEARCH_KEY,
            )
        )

        docs = await kernel.memory.search_async(index_name, query, limit=10)
        context = [doc.text for doc in docs]

        return context
    
    @sk_function(
        description="This function answer all questions about onboarding or any question of the user",
        name="index_search",
        input_description="The query may be any general question that may be found in Documents (context).",
    )    
    async def find_response(self, context: SKContext) -> str:
        chat_history = context["chat_history"]
        query = context["query"]
        user_query = context["user_query"]
        index_name = context["index_name"]
        kernel:Kernel = context["kernel"]
        
        variables = ContextVariables()
        variables["query"] = query
        variables["chat_history"] = chat_history
        variables["user_query"] = user_query
        variables["context"] = index_name
        variables["options"] = "general"
        
        print('USER QUERY:')
        print(variables["query"])
        
        
        intent_function = kernel.skills.get_function("indexSearchPlugin","getIntent")

        print('SYSTEM QUERY:')
        print(intent_function)
        response = await kernel.run_async(
                intent_function,
                input_vars= variables,
            )
            
        intent_general = response['input']
        print("MY RESPONSE IS 0")
        print(intent_general)
        list_context = await self.get_context(intent_general,index_name)
        print(list_context)
        variables["context"] = "\n\n".join(list[str](list_context))

        chat_function = kernel.skills.get_function("indexSearchPlugin", "response")
        print("MY RESPONSE IS 1")
        output = await kernel.run_async(
            chat_function,
            input_vars=variables
        )   
        print("MY RESPONSE IS ")
        print(output)
        
        return output['input']
