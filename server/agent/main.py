from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field
from typing_extensions import TypedDict, Annotated, Literal
import json

llm = ChatOllama(
    model="llama3.2:1b",
    base_url="http://localhost:11434"
)

class MessageClassifier(BaseModel):
    message_type: Literal["question", "command"] = Field(
        ...,
        description="Classify if the message requires a tool call/command or a question/request that requires a knowledge response."
    )

class InputModifier(BaseModel):
    parameter: str = Field(..., description="The parameter to modify")
    value: float = Field(..., description="The new value for the parameter")

class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str | None

def classify_message(state: State):
    last_message = state["messages"][-1]
    classifier_llm = llm.with_structured_output(MessageClassifier)

    result = classifier_llm.invoke([
        {
            "role": "system",
            "content": """Classify the user message as either a question or a command:
            - Question: A question about the system or a request for information.
            - Command: A command to modify the system or perform an action.
            """
        },
        {
            "role": "user",
            "content": last_message.content
        }
    ])

    return {"message_type": result.message_type}

def router(state: State):
    message_type = state.get("message_type", "question")

    if message_type == "command":
        return {"next": "command"}
    
    return {"next": "response"}

def response_agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {"role": "system", "content": "You are a helpful assistant that answers questions about Power Systems."},
        {"role": "user", "content": last_message.content}
    ]

    reply = llm.invoke(messages)
    return {"messages": [reply]}

def command_agent(state: State):
    last_message = state["messages"][-1]
    modifier_llm = llm.with_structured_output(InputModifier)
    
    with open("./inputs.json", "r") as f:
        current_inputs = json.load(f)
    
    result = modifier_llm.invoke([
        {
            "role": "system",
            "content": f"Extract the parameter and new value from the user request. Current inputs: {current_inputs}"
        },
        {
            "role": "user",
            "content": last_message.content
        }
    ])
    
    current_inputs[result.parameter] = result.value
    
    with open("./inputs.json", "w") as f:
        json.dump(current_inputs, f, indent=2)
    
    reply_content = f"Updated {result.parameter} to {result.value}"
    reply = AIMessage(content=reply_content)
    
    return {"messages": [reply]}

graph_builder = StateGraph(State)

graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("router", router)
graph_builder.add_node("response", response_agent)
graph_builder.add_node("command", command_agent)

graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")

graph_builder.add_conditional_edges(
    "router",
    lambda state: state.get("next"),
    {
        "response": "response",
        "command": "command"
    }
)

graph_builder.add_edge("response", END)
graph_builder.add_edge("command", END)

graph = graph_builder.compile()

def run_agent():
    state = {"messages": [], "message_type": None}

    while True:
        user_input = input("Message: ")
        if user_input == "exit":
            print("Exiting...")
            break

        state["messages"] = state.get("messages", []) + [
            HumanMessage(content=user_input)
        ]

        state = graph.invoke(state)

        if state.get("messages") and len(state["messages"]) > 0:
            last_message = state["messages"][-1]
            print(f"Assistant: {last_message.content}")

if __name__ == "__main__":
    run_agent()