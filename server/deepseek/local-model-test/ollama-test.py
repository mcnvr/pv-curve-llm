import ollama

client = ollama.Client()

model = "deepseek-r1:1.5b"
prompt = "What is a PV Curve (Nose Curve) in Power Systems?"

response = client.generate(model=model, prompt=prompt)

print(response.response)