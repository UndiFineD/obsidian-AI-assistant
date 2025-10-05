# backend/modelmanager.py
import os
from pathlib import Path
from dotenv import load_dotenv
import huggingface_hub
try:
    from .llm_router import HybridLLMRouter  # adjust your wrapper import
except ImportError:
    from llm_router import HybridLLMRouter


class ModelManager:
    """Manages local and Hugging Face models for LLMs."""

    def __init__(
        self,
        models_dir="./models",
        env_file=".env",
        models_file="models.txt",
        default_model="gpt4all-lora",
        hf_token: str = None  # <-- new optional token parameter
    ):
        # Load environment variables from .env
        env_path = Path(env_file)
        if env_path.exists():
            load_dotenv(env_path)
        else:
            print(f"[ModelManager] Warning: {env_file} not found, relying on system env vars.")

        # Use hf_token parameter first, fallback to environment
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        if self.hf_token:
            huggingface_hub.login(token=self.hf_token)
            print("[ModelManager] Hugging Face token loaded successfully.")
        else:
            print("[ModelManager] Warning: No Hugging Face token provided or found in environment!")

        # Models directory
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.loaded_models = {}

        # Load available models from models.txt
        self.available_models = self._load_models_file(models_file)

        # Default model
        self.default_model = default_model
        if self.default_model not in self.available_models:
            if self.available_models:
                self.default_model = next(iter(self.available_models))
                print(f"[ModelManager] Default model not found. Using: {self.default_model}")
            else:
                print("[ModelManager] No models available at all!")
                self.default_model = None

    def _load_models_file(self, models_file: str):
        models_path = Path(models_file)
        if not models_path.exists():
            print(f"[ModelManager] Warning: {models_file} not found. No models loaded.")
            return {}

        available_models = {}
        with open(models_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key = line.split("/")[-1].lower()
                available_models[key] = line

        print(f"[ModelManager] Loaded {len(available_models)} models from {models_file}")
        return available_models

    def download_model(self, model_name: str):
        if model_name not in self.available_models:
            raise ValueError(f"Unknown model: {model_name}")

        model_path = self.models_dir / model_name
        if not model_path.exists():
            print(f"[ModelManager] Downloading {model_name}...")
            huggingface_hub.snapshot_download(
                repo_id=self.available_models[model_name],
                cache_dir=str(model_path)
            )
        return model_path

    def load_model(self, model_name: str = None):
        if not model_name:
            model_name = self.default_model
        if not model_name:
            raise ValueError("No default model available to load.")

        if model_name in self.loaded_models:
            return self.loaded_models[model_name]

        try:
            model_path = self.download_model(model_name)
        except Exception as e:
            print(f"[ModelManager] Could not download {model_name} ({e}), checking offline cache...")
            model_path = self.models_dir / model_name
            if not model_path.exists():
                raise RuntimeError(f"No offline model available for {model_name}")

        # Instantiate your hybrid router
        llm = HybridLLMRouter(
            llama_model_path=str(model_path / "model.bin"),
            gpt4all_model_path=str(model_path / "gpt4all.bin"),
            prefer_fast=True,
            memory_limit=8 * 1024 ** 3
        )

        self.loaded_models[model_name] = llm
        return llm
