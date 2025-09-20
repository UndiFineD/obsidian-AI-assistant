from typing import Optional

# Import your LLaMA / GPT4All Python bindings
# Example: llama_cpp, gpt4all
from llama_cpp import Llama
from gpt4all import GPT4All

class HybridLLMRouter:
    def __init__(self, llama_model_path: str, gpt4all_model_path: str):
        self.llama = Llama(model_path=llama_model_path)
        self.gpt4all = GPT4All(model=gpt4all_model_path)
        self.session_memory = {}  # Stores question → answer

    def query(self, question: str, context: Optional[str] = None, prefer_fast: bool = True) -> str:
        """
        Query the LLM. If prefer_fast=True, use LLaMA. Else GPT4All for deeper reasoning.
        """
        input_text = f"{context}\n\nQuestion: {question}" if context else question

        if prefer_fast:
            response = self.llama(input_text, max_tokens=500)
            answer = response["choices"][0]["text"]
        else:
            answer = self.gpt4all.generate(input_text)

        # Store in session memory
        self.session_memory[question] = answer.strip()
        return answer.strip()
        
        