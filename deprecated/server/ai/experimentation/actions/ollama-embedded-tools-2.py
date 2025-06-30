"""
Similar to @ollama-embedded-tools.py, but uses ollama import instead and also processes the response to see if it's a tool call.
"""

import ollama
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
    # Get current inputs
    try:
        with open("inputs.json", "r") as f:
            current_inputs = json.load(f)
        inputs_info = f"Current inputs: {json.dumps(current_inputs, indent=2)}"
    except Exception as e:
        inputs_info = f"Error reading inputs: {e}"
        current_inputs = {}
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "modify_input",
                "description": f"Modify an existing input value. Only these inputs can be modified: {list(current_inputs.keys())}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input_key": {
                            "type": "string",
                            "description": f"The input key to modify. Must be one of: {list(current_inputs.keys())}"
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
    
    try:
        response = ollama.chat(
            model="llama3.1:8b",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a helpful assistant. You can answer questions and help with various tasks.\n\n{inputs_info}\n\nYou have access to a tool that can modify these input values, but only use it when the user specifically requests to change, modify, update, or set an input value. For general questions or other tasks, respond normally without using any tools."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            tools=tools
        )
        
        message = response["message"]
        content = message.get("content", "")
        
        # Check if the content looks like raw tool call JSON (model confusion)
        if content.startswith('{"type":"function"'):
            return "I apologize, I'm having trouble with tool calling. Please try rephrasing your request."
        
        # Check for proper tool calls
        if "tool_calls" in message and message["tool_calls"]:
            results = []
            for tool_call in message["tool_calls"]:
                if tool_call["function"]["name"] == "modify_input":
                    args = tool_call["function"]["arguments"]
                    result = modify_input(args["input_key"], args["value"])
                    results.append(f"🛠️ {result}")
            
            if results:
                return f"{content}\n" + "\n".join(results) if content else "\n".join(results)
            else:
                return content
        else:
            return content or "I'm sorry, I didn't understand that."
            
    except Exception as e:
        return f"Error: {e}"

def main():
    print("🤖 Ollama Tool Calling System (Simplified)")
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