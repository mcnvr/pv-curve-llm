from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import json
import re

def modify_input(value: int) -> str:
    with open("inputs.json", "r") as f:
        inputs = json.load(f)
    
    inputs["INPUT_1"] = value
    
    with open("inputs.json", "w") as f:
        json.dump(inputs, f, indent=2)
    
    return f"Modified INPUT_1 to: {value}"

model = ChatOllama(model="deepseek-r1:1.5b")

template = """Extract only the integer from this request: {user_request}

Respond with only the number, nothing else.

Examples:
"change input 1 to 17" → 17
"set it to 42" → 42
"make it 8" → 8

Number:"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

user_input = input("What would you like to modify INPUT_1 to? ")
response = chain.invoke({"user_request": user_input})

try:
    extracted_number = int(re.search(r'\d+', response.content).group())
    result = modify_input(extracted_number)
    print(f"Success: {result}")
except (ValueError, AttributeError):
    print("Could not extract a valid integer from your request") 