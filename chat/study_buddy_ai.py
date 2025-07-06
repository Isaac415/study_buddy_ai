import os
from typing import TypedDict, List, Union
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]

llm = ChatDeepSeek(model="deepseek-chat")

def system_message(state: AgentState) -> AgentState:
    content = '''
    You are StudyBuddyAI.
    '''
    state["messages"].append(SystemMessage(content=content.strip()))

def process(state: AgentState) -> AgentState:
    user_message = input("Enter: ")
    state["messages"].append(HumanMessage(content=user_message))
    response = llm.invoke(state["messages"])
    state["messages"].append(AIMessage(content=response.content))
    print(f"AI: {response.content.strip()}")

    return state


def create_agent():
    graph = StateGraph(AgentState)
    graph.add_node("system_message", system_message)
    graph.add_node("process", process)

    graph.add_edge(START, "system_message")
    graph.add_edge("system_message", "process")
    graph.add_edge("process", "process")

    agent = graph.compile()

    return agent
    