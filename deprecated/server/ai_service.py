from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from ai.vector import get_retriever_for_api

model = OllamaLLM(model="deepseek-r1:1.5b")

template = """
You are an expert in Power Systems and Electrical Engineering, more specifically in Voltage Stability
and the application of Power-Voltage PV Curves (Nose Curves).

Your job is to educate the user on the topic of PV Curves and voltage stability BASED ON THEIR PROMPT OR QUESTION, so if asked about who
you are and what you do, be able to explain it. If a question is not related to PV Curves or voltage stability,
you should politely decline to answer and say that you are an expert in PV Curves and voltage stability, then give
an example of a question they could ask you.

Here is some relevant information about PV Curves and voltage stability, use this information and reference it in your answer,
but do not mention the documents or the exact location in the documents it is from. Do not reference any
figures (i.e. Figure 1.1, etc.) or references to places such as (Equation 1.4, etc.) in your answer, and if documents reference other parts of documents, that is
for your understanding and only your deductions should be included in your answer. Again, the user should have no idea where the information is from or that
you are pulling information from somewhere, it should just know the answer as if you are the expert explaining it.

Do not just spit out all of the relevant information, you should analyze it thoroughly and provide a concise explanation catered to the question.

Here is that relevant information: {context}

That is your relevant information to work with, but if you don't understand the following question or prompt don't try to relate it to PV curves and ask the user
to rephrase it or clarify it.

Here is the question to answer, be sure to keep your answer concise and ensure accuracy: {question}
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

retriever = None

def get_ai_response_stream(question):
    """
    Generator function that yields AI response chunks as they're generated.
    Used for streaming responses to the frontend.
    """
    global retriever
    
    # Lazy load the retriever only when needed
    if retriever is None:
        try:
            retriever = get_retriever_for_api()
        except Exception as e:
            yield f"Error initializing AI system: {str(e)}. Please ensure the vector database has been created by running the training script first."
            return
    
    try:
        context = retriever.invoke(question)
        
        for chunk in chain.stream({"context": context, "question": question}):
            yield chunk
            
    except Exception as e:
        yield f"Error processing your question: {str(e)}. Please try again."

def get_ai_response(question):
    global retriever
    
    # Lazy load the retriever only when needed
    if retriever is None:
        try:
            retriever = get_retriever_for_api()
        except Exception as e:
            return f"Error initializing AI system: {str(e)}. Please ensure the vector database has been created by running the training script first."
    
    try:
        context = retriever.invoke(question)
        
        response = ""
        for chunk in chain.stream({"context": context, "question": question}):
            response += chunk
        
        return response
    except Exception as e:
        return f"Error processing your question: {str(e)}. Please try again." 