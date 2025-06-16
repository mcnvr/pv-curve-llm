# Helpful video: https://www.youtube.com/watch?v=UtSSMs6ObqY

import requests
import json

url = "http://localhost:11434/api/chat"

payload = {
    "model": "deepseek-r1:1.5b",
    "messages": [
        {
            "role": "user",
            "content": "What is a PV Curve (Nose Curve) in Power Systems?"
        }
    ]
}

response = requests.post(url, json=payload, stream=True)

if response.status_code == 200:
    for line in response.iter_lines(decode_unicode=True):
        if line:
            json_line = json.loads(line)
            if "message" in json_line and "content" in json_line["message"]:
                print(json_line["message"]["content"], end="", flush=True)
            elif "error" in json_line:
                print(f"Error: {json_line['error']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)