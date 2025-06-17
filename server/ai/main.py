# Helpful video: https://www.youtube.com/watch?v=E4l91XKQSgw

from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever

model = OllamaLLM(model="deepseek-r1:1.5b")

template = """
You are an expert in power systems, more specifically in Power-Voltage PV Curves (Nose Curves).

Here is some relevant information about PV Curves: {context}

Here is the question to answer: {question}
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

while True:
    question = input("\nEnter a question (q to quit): ")
    if question.lower() == "q":
        break

    context = retriever.invoke(question)
    print("Searching for context...")
    print(f"Found {len(context)} documents")

    for chunk in chain.stream({"context": context, "question": question}):
        print(chunk, end="", flush=True)