from flask import Blueprint, request, jsonify, current_app
from langchain.chat_models import AzureChatOpenAI
from langchain.chains import RetrievalQA,LLMChain
from langchain.retrievers import AzureCognitiveSearchRetriever
from langchain.prompts import PromptTemplate,StringPromptTemplate
from langchain.agents import AgentType, Tool, initialize_agent,AgentOutputParser,LLMSingleActionAgent,AgentExecutor
from helpers.session import setSession
from langchain import LLMMathChain
from langchain.schema import AgentAction, AgentFinish
import re
from langchain.memory import ConversationBufferWindowMemory



chatGeneration = Blueprint('chatGeneration', __name__)

from typing import Callable,Union


# Set up a prompt template
class CustomPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    ############## NEW ######################
    # The list of tools available
    tools_getter: list

    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        ############## NEW ######################
        tools = self.tools_getter
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join(
            [f"{tool.name}: {tool.description}" for tool in tools]
        )
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in tools])
        return self.template.format(**kwargs)
class CustomOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(
            tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output
        )
        
'''
@chatGeneration.route("/generateAnswer", methods=["GET","POST"])
def generateAnswer():
    cosmos = current_app.config['cosmos']
    data = request.get_json()
    message = data['prompt']
    sessionId = data['sessionId']   
    indexValue = data['indexValue']
    if(sessionId != cosmos.session_id):
        cosmosUpdated = setSession(sessionId)
        print("New session ! ")
   
    
    index_name = indexValue
    retriever = AzureCognitiveSearchRetriever(content_key="content", top_k=5, index_name=index_name)
    llm = AzureChatOpenAI(deployment_name="gpt-35-turbo", temperature=0.1)

    
    template = """You are a super intetelligent bot. You need to have a precise answer. You have documents about the definitions we are deploying.
                  If we ask you about information, just tell them the summary of your documents.

                {tools}

                Use the following format:

                Question: the input question you must answer
                Thought: you should always think about what to do
                Action: the action to take, should be one of [{tool_names}]
                Action Input: the input to the action
                Observation: the result of the action
                ... (this Thought/Action/Action Input/Observation can repeat N times)
                Thought: I now know the final answer
                Final Answer: the final answer to the original input question

                Say thanks for asking at the end.

                Question: {input}
                {agent_scratchpad}"""
                
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=retriever  
    )

    tools = [
        Tool(
            name=index_name,
            func=qa_chain.run,
            description="Useful when you have question about the definitions we are deploying",
        )
    ]       
    
    prompt = CustomPromptTemplate(
        template=template,
        tools_getter=tools,
        # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
        # This includes the `intermediate_steps` variable because that is needed
        input_variables=["input", "intermediate_steps"],
    )
    

    output_parser = CustomOutputParser()

    llm_chain = LLMChain(llm=llm, prompt=prompt)

    tool_names = [tool.name for tool in tools]
    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        output_parser=output_parser,
        stop=["\nObservation:"],
        allowed_tools=tool_names,
    )
    agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent, tools=tools, verbose=True
    )

    answer = agent_executor.run(message)
    print("THE ANSWER") 
    print(answer)
    response = {"Answer": answer}
    return jsonify(response), 200
'''


@chatGeneration.route("/generateAnswer", methods=["GET","POST"])
def generateAnswer():
    cosmos = current_app.config['cosmos']
    data = request.get_json()
    message = data['prompt']
    sessionId = data['sessionId']   
    indexValue = data['indexValue']
    if(sessionId != cosmos.session_id):
        cosmosUpdated = setSession(sessionId)
        print("New session ! ")
    memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True, k=30, chat_memory=cosmosUpdated)
    print(f"memorty {memory.chat_memory.messages}")
    memory.chat_memory.add_user_message(message)
    index_name = indexValue
    
    
    retriever = AzureCognitiveSearchRetriever(content_key="content", top_k=5, index_name=index_name)
    llm = AzureChatOpenAI(deployment_name="gpt-35-turbo", temperature=0.1)
    Docs = retriever.get_relevant_documents(message)
    print(Docs)
    template = """Use the following pieces of contexts to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer. 
    keep the answer as concise as possible.
    Always say "thanks for asking!" at the end of the answer.
    {context}
    Question: {question}
    Helpful Answer:"""

    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
        return_source_documents=True
        
    )

    questions = [
                    message
                ]
    print(indexValue)
    
    chat_history = memory.chat_memory.messages
    for question in questions:
        result = qa_chain({"query": question, "chat_history": chat_history})
        response = {"Answer": result['result']}
        print(response)
    memory.chat_memory.add_ai_message(result['result'])

    return jsonify(response), 200
