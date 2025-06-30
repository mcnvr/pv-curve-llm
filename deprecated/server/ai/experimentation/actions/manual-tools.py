import ollama
import json

client = ollama.Client()

model = "deepseek-r1:1.5b"

prompt = """

You will be shown a series of commands as well as a request. The commands are actions the user will take, and your goal is to specify the commands that will be taken
based on the request. For now, the commands will be simple and be related to modifying an input. Your available commands are as follows, and be sure to include them in
a comma separated list, only putting spaces between each part within a command.

PART ONE OF COMMAND:
"DELETE", or "MODIFY"

PART TWO OF COMMAND:
"INPUT_1", "INPUT_2", "INPUT_3", "INPUT_4", "INPUT_5", "ALL"

PART THREE OF COMMAND:
VALUE

EXAMPLE COMMANDS:
"DELETE INPUT_2"
"MODIFY INPUT_3 7"
"DELETE ALL"

Note that delete never needs a part 3, and that delete all is a valid command.

You must determine the appropriate command based on the user's request, such as changing the value of input 3 to 7, changing the value of the input with the value of 5 to 8,
modifying input 4 to have 9, modifying all inputs to have the value of 10, deleting all inputs, etc.

All responses should be in the following format (Everything betwen the single quotes is your format, and in the brackets is what I will describe afterward): 
'
COMMANDS:
[Your commands here]

RESPONSE:
[Your formatted response to the user]
'

Here is the current list of inputs so that you know how to modify them appropriately:
{inputs}

Based on the following user input, please generate the appropriate commands and response. Your response should be an extremely simple and concise summary casually explaining to the user what your commands were:
{request}
"""

with open("inputs.json", "r") as f:
    inputs = json.load(f)

user_request = input("Enter your request: ")

response = client.generate(model=model, prompt=prompt.format(inputs=json.dumps(inputs), request=user_request))

lines = response.response.split('\n')
commands_section = False
commands = []

for line in lines:
    if line.strip() == "COMMANDS:":
        commands_section = True
        continue
    elif line.strip() == "RESPONSE:":
        commands_section = False
        continue
    elif commands_section and line.strip():
        commands.extend([cmd.strip() for cmd in line.split(',')])

for command in commands:
    parts = command.split()
    if len(parts) >= 2:
        action = parts[0]
        target = parts[1]
        value = " ".join(parts[2:]) if len(parts) > 2 else ""
        
        if action == "DELETE":
            if target == "ALL":
                inputs = {"INPUT_1": "", "INPUT_2": "", "INPUT_3": "", "INPUT_4": "", "INPUT_5": ""}
            elif target in inputs:
                inputs[target] = ""
        elif action == "MODIFY" and target in inputs:
            inputs[target] = value

with open("inputs.json", "w") as f:
    json.dump(inputs, f, indent=2)

print(response.response)