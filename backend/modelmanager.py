import os
from pathlib import Path
from llm_router import HybridLLMRouter  # or your LLM wrapper
import huggingface_hub

class ModelManager:
    def __init__(self, models_dir="./models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.loaded_models = {}

        # Dictionary of known small LLMs
        self.available_models = {
            "llama-7b": "TheBloke/llama-7b-hf",
            "gpt4all-lora": "nomic-ai/gpt4all-lora",
            "mpt-7b-instruct": "mosaicml/mpt-7b-instruct",
            "vicuna-7b": "lmsys/vicuna-7b-v1.5"
        }

    def download_model(self, model_name):
        if model_name not in self.available_models:
            raise ValueError(f"Unknown model: {model_name}")

        model_path = self.models_dir / model_name
        if not model_path.exists():
            print(f"Downloading {model_name}...")
            # Hugging Face hub download
            huggingface_hub.snapshot_download(
                repo_id=self.available_models[model_name],
                cache_dir=str(model_path)
            )
        return model_path

    def load_model(self, model_name):
        if model_name in self.loaded_models:
            return self.loaded_models[model_name]

        model_path = self.download_model(model_name)
        llm = HybridLLMRouter(
            llama_model_path=str(model_path / "model.bin"),  # adjust per model
            gpt4all_model_path=str(model_path / "gpt4all.bin"),
            prefer_fast=True,
            memory_limit=8 * 1024 ** 3
        )
        self.loaded_models[model_name] = llm
        return llm
