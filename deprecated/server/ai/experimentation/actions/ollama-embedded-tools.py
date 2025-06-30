import requests
import json

def modify_input(input_key: str, value: int) -> str:
    """Modify an existing input in inputs.json to a new integer value"""
    try:
        with open("inputs.json", "r") as f:
            inputs = json.load(f)
        
        if input_key not in inputs:
            return f"Error: {input_key} does not exist. Available inputs: {list(inputs.keys())}"
        
        inputs[input_key] = value
        
        with open("inputs.json", "w") as f:
            json.dump(inputs, f, indent=2)
        
        return f"Successfully modified {input_key} to {value}"
    except Exception as e:
        return f"Error: {e}"

def chat_with_tools(user_message: str) -> str:
    url = "http://localhost:11434/api/chat"
    
    # Get current inputs to show the model what's available
    try:
        with open("inputs.json", "r") as f:
            current_inputs = json.load(f)
        inputs_info = f"Current inputs: {json.dumps(current_inputs, indent=2)}"
    except Exception as e:
        inputs_info = f"Error reading inputs: {e}"
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "modify_input",
                "description": f"Modify an existing input value. Only these inputs can be modified: {list(current_inputs.keys()) if 'current_inputs' in locals() else 'unknown'}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input_key": {
                            "type": "string",
                            "description": f"The input key to modify. Must be one of: {list(current_inputs.keys()) if 'current_inputs' in locals() else 'unknown'}"
                        },
                        "value": {
                            "type": "integer", 
                            "description": "The new integer value"
                        }
                    },
                    "required": ["input_key", "value"]
                }
            }
        }
    ]
    
    payload = {
        "model": "llama3.2:1b",
        "messages": [
            {
                "role": "system",
                "content": f"You can modify input values in a configuration file. {inputs_info}\n\nYou can only modify existing inputs, not create new ones."
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        "tools": tools,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            response_data = response.json()
            message = response_data["message"]
            
            # Check for tool calls
            if "tool_calls" in message:
                results = []
                for tool_call in message["tool_calls"]:
                    if tool_call["function"]["name"] == "modify_input":
                        args = tool_call["function"]["arguments"]
                        if isinstance(args, str):
                            args = json.loads(args)
                        
                        result = modify_input(args["input_key"], args["value"])
                        results.append(f"🛠️ {result}")
                
                ai_content = message.get("content", "")
                return f"{ai_content}\n" + "\n".join(results)
            else:
                return message["content"]
                
        else:
            return f"Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Error: {e}"

def main():
    print("🤖 Ollama Tool Calling System")
    print("Type 'quit' to exit")
    print("=" * 50)
    
    while True:
        user_input = input("\n👤 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
            
        if not user_input:
            continue
            
        print("\n🤖 AI:", end=" ")
        response = chat_with_tools(user_input)
        print(response)

if __name__ == "__main__":
    main()
