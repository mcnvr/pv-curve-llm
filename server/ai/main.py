# Helpful video: https://www.youtube.com/watch?v=E4l91XKQSgw

from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever

model = OllamaLLM(model="deepseek-r1:1.5b")

template = """
You are an expert in Power Systems and Electrical Engineering, more specifically in Voltage Stability
and the application of Power-Voltage PV Curves (Nose Curves).

Here is some relevant information about PV Curves and voltage stability, use this information and reference it in your answer,
but do not mention the documents or the exact location in the documents it is from. Do not reference any
figures (i.e. Figure 1.1, etc.) or references to places such as (Equation 1.4, etc.) in your answer, and if documents reference other parts of documents, that is
for your understanding and only your deductions should be included in your answer. Again, the user should have no idea where the information is from or that
you are pulling information from somewhere, it should just know the answer as if you are the expert explaining it.

Do not just spit out all of the relevant information, you should analyze it thoroughly and provide a concise explanation catered to the question.

Here is that relevant information: {context}

Here is the question to answer, be sure to keep your answer concise and ensure accuracy: {question}
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

while True:
    question = input("\n-----------------------------------\nEnter a question (q to quit): ")
    if question.lower() == "q":
        break

    context = retriever.invoke(question)
    print("Searching for context...")
    print(f"Found {len(context)} documents")

    for chunk in chain.stream({"context": context, "question": question}):
        print(chunk, end="", flush=True)