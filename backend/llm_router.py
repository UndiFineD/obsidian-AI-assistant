# backend/llm_router.py
import os
from typing import Dict, List

# LLM backends
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

try:
    from gpt4all import GPT4All
except ImportError:
    GPT4All = None


class HybridLLMRouter:
    """
    Hybrid LLM router that dynamically selects between LLaMA and GPT4All
    based on preferences, prompt length, and model availability.
    """

    def __init__(
        self,
        llama_model_path: str = "models/llama-7b-q4.bin",
        gpt4all_model_path: str = "models/gpt4all-lora-quantized.bin",
        prefer_fast: bool = True,
        session_memory: bool = True,
        memory_limit: int = 5,
    ):
        self.prefer_fast = prefer_fast
        self.session_memory = session_memory
        self.memory_limit = memory_limit
        self.memory: List[Dict[str, str]] = []

        # Load LLaMA
        if Llama and os.path.exists(llama_model_path):
            self.llama = Llama(model_path=llama_model_path, n_ctx=2048, n_threads=4)
        else:
            self.llama = None

        # Load GPT4All
        if GPT4All and os.path.exists(gpt4all_model_path):
            self.gpt4all = GPT4All(model_name=gpt4all_model_path)
        else:
            self.gpt4all = None

    # -------------------
    # Memory Handling
    # -------------------
    def add_to_memory(self, role: str, content: str):
        if not self.session_memory:
            return
        self.memory.append({"role": role, "content": content})
        if len(self.memory) > self.memory_limit:
            self.memory.pop(0)

    def build_context(self, prompt: str) -> str:
        if not self.session_memory or not self.memory:
            return prompt
        memory_str = "\n".join([f"{m['role']}: {m['content']}" for m in self.memory])
        return f"{memory_str}\nUser: {prompt}"

    # -------------------
    # Model Selection
    # -------------------
    def choose_model(self, prompt: str) -> str:
        if self.prefer_fast and self.llama:
            return "llama"
        if len(prompt.split()) > 30 and self.gpt4all:
            return "gpt4all"
        return "llama" if self.llama else "gpt4all"

    # -------------------
    # Generation
    # -------------------
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        context = self.build_context(prompt)
        model_choice = self.choose_model(prompt)

        if model_choice == "llama" and self.llama:
            output = self.llama(prompt=context, max_tokens=max_tokens, stop=["User:", "Assistant:"])
            text = output["choices"][0]["text"].strip()
        elif model_choice == "gpt4all" and self.gpt4all:
            with self.gpt4all.chat_session():
                text = self.gpt4all.generate(context, max_tokens=max_tokens)
        else:
            text = "No model available."

        # Update memory
        self.add_to_memory("User", prompt)
        self.add_to_memory("Assistant", text)
        return text
