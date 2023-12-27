"""
Chatbot with context and memory, using Semantic Kernel.
"""

from semantic_kernel import Kernel,ContextVariables
from semantic_kernel.planning import ActionPlanner

# Chat roles
SYSTEM = "system"
USER = "user"
ASSISTANT = "assistant"

class bot:
    """Create a chatbot with Azure OPENAI LLM."""

    kernel = None
    variables = None

    def __init__(self,kernel : Kernel, variables : ContextVariables):
        self.kernel = kernel
        self.variables = variables


    async def retrieverAugmentedGeneration(self,index_name:str, query: str, chat_history: str) -> str:
        """
         Asks the LLM to answer the user's query with the context provided.
         The index_name may be empty if we are not using Azure Search
        """

        user_template = "{{$chat_history}}" + f"{USER}: " + "{{$query}}\n"
        
        self.variables["user_query"] = user_template
        self.variables["query"] = query
        self.variables["index_name"] = index_name
        self.variables["kernel"] = self.kernel
        self.variables["chat_history"] = ""
        print("KERNEL")
        print(self.kernel.skills)
        planner = ActionPlanner(self.kernel)
        plan = await planner.create_plan_async(goal=query)
        context = self.kernel.create_new_context(self.variables)
        result = await plan.invoke_async(query,context)
        self.variables["chat_history"] += f"{USER}: {query}\n{ASSISTANT}: {result.result}\n"
        return result.result

    async def ask(self,index_name:str, query: str, chat_history: str) -> str:
        """
            Send the request to openAI
        """
        response = await self.retrieverAugmentedGeneration(index_name,query, chat_history)       
        print(
            "*****\n"
            f"QUESTION:\n{query}\n"
            f"RESPONSE:\n{response}\n"
            "*****\n"
        )

        return response