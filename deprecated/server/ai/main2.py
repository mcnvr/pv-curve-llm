import ollama
import json
from vector import retriever

def modify_pv_input(input_key: str, value) -> str:
    try:
        with open("pv_inputs.json", "r") as f:
            inputs = json.load(f)
        
        if input_key not in inputs:
            return f"Error: {input_key} does not exist. Available inputs: {list(inputs.keys())}"
        
        inputs[input_key] = value
        
        with open("pv_inputs.json", "w") as f:
            json.dump(inputs, f, indent=2)
        
        return f"Successfully modified {input_key} to {value}"
    except Exception as e:
        return f"Error: {e}"

def route_to_question_model(user_input: str) -> str:
    """Tool function to route user input to the question-answering model"""
    print("Generating RAG response")
    context = retriever.invoke(user_input)
    
    expert_prompt = f"""You are an expert in Power Systems and Electrical Engineering, specifically in Voltage Stability and Power-Voltage PV Curves (Nose Curves).

Here is relevant information about PV Curves: {context}

Answer the user's question about PV curves and voltage stability using this information. If the question is not related to PV Curves or voltage stability, politely decline and give an example question.

Do not reference figures, equations, or document locations. Answer as the expert explaining from your knowledge.

Question: {user_input}"""
    
    try:
        stream = ollama.chat(
            model="llama3.1:8b",
            messages=[{"role": "user", "content": expert_prompt}],
            stream=True
        )
        
        response_text = ""
        for chunk in stream:
            if "message" in chunk and "content" in chunk["message"]:
                content = chunk["message"]["content"]
                print(content, end="", flush=True)
                response_text += content
        
        return f"Question answered: {response_text[:100]}..."
        
    except Exception as e:
        error_msg = f"Error in question model: {e}"
        print(error_msg)
        return error_msg

def route_to_modification_model(user_input: str) -> str:
    """Tool function to route user input to the parameter modification model"""
    print("Determining input modification")
    try:
        with open("pv_inputs.json", "r") as f:
            current_inputs = json.load(f)
        inputs_info = f"Current PV-Curve inputs: {json.dumps(current_inputs, indent=2)}"
    except Exception as e:
        inputs_info = f"Error reading inputs: {e}"
        current_inputs = {}
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "modify_pv_input",
                "description": f"Modify PV-curve analysis parameters. Available: {list(current_inputs.keys())}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input_key": {
                            "type": "string",
                            "description": f"Parameter to modify: {list(current_inputs.keys())}"
                        },
                        "value": {
                            "description": "New value to set"
                        }
                    },
                    "required": ["input_key", "value"]
                }
            }
        }
    ]
    
    system_prompt = f"""You are configuring PV-curve analysis parameters. {inputs_info}

The user wants to modify a parameter. Use the modify_pv_input tool to make the requested change."""
    
    try:
        stream = ollama.chat(
            model="llama3.1:8b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            tools=tools,
            stream=True
        )
        
        tool_calls = []
        for chunk in stream:
            if "message" in chunk and "tool_calls" in chunk["message"]:
                tool_calls.extend(chunk["message"]["tool_calls"])
        
        if tool_calls:
            results = []
            for tool_call in tool_calls:
                if tool_call["function"]["name"] == "modify_pv_input":
                    args = tool_call["function"]["arguments"]
                    result = modify_pv_input(args["input_key"], args["value"])
                    print(f"🛠️ {result}")
                    results.append(result)
            return f"Modifications completed: {'; '.join(results)}"
        else:
            msg = "I'll help you modify the parameters. Could you specify which parameter and the new value?"
            print(msg)
            return msg
        
    except Exception as e:
        error_msg = f"Error in modification model: {e}"
        print(error_msg)
        return error_msg

def chat_with_pv_tools(user_message: str) -> str:
    """LLM-based classifier with routing tools"""
    print("Classifying response")
    
    # Define tools for routing to different models
    routing_tools = [
        {
            "type": "function",
            "function": {
                "name": "route_to_question_model",
                "description": "Route to question-answering model for educational queries about PV curves, voltage stability, power systems concepts",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_input": {
                            "type": "string",
                            "description": "The user's question to be answered by the expert model"
                        }
                    },
                    "required": ["user_input"]
                }
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "route_to_modification_model",
                "description": "Route to parameter modification model for changing, setting, updating PV-curve analysis parameters",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_input": {
                            "type": "string",
                            "description": "The user's request to modify parameters"
                        }
                    },
                    "required": ["user_input"]
                }
            }
        }
    ]
    
    # Classifier LLM with routing tools
    classifier_prompt = f"""You are a classifier that determines user intent and routes requests appropriately.

Analyze the user input and determine if they want to:
1. Ask questions about PV curves, voltage stability, or power systems concepts → use route_to_question_model
2. Modify, change, set, or update PV-curve analysis parameters → use route_to_modification_model

Examples:
- "What is a PV curve?" → route_to_question_model
- "Change base_mva to 200" → route_to_modification_model  
- "Explain voltage stability" → route_to_question_model
- "Set frequency to 50 Hz" → route_to_modification_model
- "How does voltage collapse work?" → route_to_question_model
- "Update monitor_bus to 15" → route_to_modification_model

User input: {user_message}

Use the appropriate routing tool to handle this request."""
    
    try:
        stream = ollama.chat(
            model="llama3.1:8b",
            messages=[{"role": "user", "content": classifier_prompt}],
            tools=routing_tools,
            stream=True
        )
        
        tool_calls = []
        for chunk in stream:
            if "message" in chunk and "tool_calls" in chunk["message"]:
                tool_calls.extend(chunk["message"]["tool_calls"])
        
        if tool_calls:
            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                args = tool_call["function"]["arguments"]
                
                if function_name == "route_to_question_model":
                    return route_to_question_model(args["user_input"])
                elif function_name == "route_to_modification_model":
                    return route_to_modification_model(args["user_input"])
        else:
            # Fallback if no tool called
            print("I can help you with PV-curve questions or parameter modifications. Could you clarify your request?")
            return "No routing tool called"
            
    except Exception as e:
        print(f"Error in classifier: {e}")
        return f"Classifier error: {e}"

def main():
    print("🤖 PV-Curve Expert with Parameter Control")
    print("Type 'quit' to exit, 'status' to see current parameters")
    print("=" * 60)
    
    while True:
        user_input = input("\n👤 Enter question: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
            
        if user_input.lower() == 'status':
            try:
                with open("pv_inputs.json", "r") as f:
                    inputs = json.load(f)
                print("📊 Current PV-Curve parameters:")
                print(json.dumps(inputs, indent=2))
            except Exception as e:
                print(f"Error reading parameters: {e}")
            continue
            
        if not user_input:
            continue
            
        print("\n🤖 PV Expert: ", end="", flush=True)
        chat_with_pv_tools(user_input)

if __name__ == "__main__":
    main()
