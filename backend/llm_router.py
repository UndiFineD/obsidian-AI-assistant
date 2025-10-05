# backend/llm_router.py
import os
from typing import Dict, List
from .utils import safe_call

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

        # Load LLaMA with error boundary
        def do_load_llama():
            if Llama and os.path.exists(llama_model_path):
                return Llama(model_path=llama_model_path, n_ctx=2048, n_threads=4)
            return None
        self.llama = safe_call(do_load_llama, error_msg="[HybridLLMRouter] Error loading LLaMA model", default=None)

        # Load GPT4All with error boundary
        def do_load_gpt4all():
            if GPT4All and os.path.exists(gpt4all_model_path):
                return GPT4All(model_name=gpt4all_model_path)
            return None
        self.gpt4all = safe_call(do_load_gpt4all, error_msg="[HybridLLMRouter] Error loading GPT4All model", default=None)

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
        text = "No model available."
        def do_generate():
            if model_choice == "llama" and self.llama:
                output = self.llama(prompt=context, max_tokens=max_tokens, stop=["User:", "Assistant:"])
                return output["choices"][0]["text"].strip()
            elif model_choice == "gpt4all" and self.gpt4all:
                with self.gpt4all.chat_session():
                    return self.gpt4all.generate(context, max_tokens=max_tokens)
            return text
        text = safe_call(do_generate, error_msg="[HybridLLMRouter] Error during generation", default=text)
        # Update memory
        self.add_to_memory("User", prompt)
        self.add_to_memory("Assistant", text)
        return text
