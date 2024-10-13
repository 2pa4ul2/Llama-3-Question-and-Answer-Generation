#sample usage of the model

from langchain_community.llms import Ollama
llm = Ollama(model="llama3")
input_text = input("Enter your text: ")
result = llm.invoke(input_text)
print(result)