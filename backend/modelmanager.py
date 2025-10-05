# backend/modelmanager.py
import os
from pathlib import Path
from dotenv import load_dotenv
import huggingface_hub
try:
    from .llm_router import HybridLLMRouter  # adjust your wrapper import
    from .utils import safe_call
except ImportError:
    try:
        from llm_router import HybridLLMRouter
        from utils import safe_call
    except ImportError:
        from llm_router import HybridLLMRouter
        # Define safe_call locally if utils not found
        def safe_call(fn, *args, error_msg=None, default=None, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                print(error_msg or f"Error in {fn.__name__}: {e}")
                return default


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

        self.available_models = self._load_models_file(models_file)
        # Add local installed models (directories) to available_models
        local_model_dirs = ["claude", "gemini", "gpt4all", "merlin", "perplexity", "vosk-model-small-en-us-0.15"]
        for local_model in local_model_dirs:
            if (self.models_dir / local_model).exists():
                self.available_models[local_model] = f"local:{local_model}"

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
        def do_load():
            with open(models_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    key = line.split("/")[-1].lower()
                    available_models[key] = line
            print(f"[ModelManager] Loaded {len(available_models)} models from {models_file}")
            return available_models
        return safe_call(do_load, error_msg=f"[ModelManager] Error loading models from {models_file}", default={})

    def download_model(self, model_name: str, revision: str = "main", max_retries: int = 3):
        if model_name not in self.available_models:
            raise ValueError(f"Unknown model: {model_name}")

        model_path = self.models_dir / model_name
        # If local model, skip download
        if str(self.available_models[model_name]).startswith("local:"):
            if not model_path.exists():
                raise RuntimeError(f"Local model directory missing: {model_path}")
            print(f"[ModelManager] Using local model: {model_name} at {model_path}")
            return model_path

        if not model_path.exists():
            print(f"[ModelManager] Downloading {model_name}...")
            last_err = None
            for attempt in range(1, max_retries + 1):
                try:
                    huggingface_hub.snapshot_download(
                        repo_id=self.available_models[model_name],
                        cache_dir=str(model_path),
                        revision=revision
                    )
                    print(f"[ModelManager] Downloaded {model_name} (revision: {revision}) on attempt {attempt}")
                    break
                except Exception as e:
                    print(f"[ModelManager] Download attempt {attempt} for {model_name} failed: {e}")
                    last_err = e
            else:
                raise RuntimeError(f"Failed to download {model_name} after {max_retries} attempts") from last_err
        return model_path

    def load_model(self, model_name: str = None):
        if not model_name:
            model_name = self.default_model
        if not model_name:
            raise ValueError("No default model available to load.")

        if model_name in self.loaded_models:
            return self.loaded_models[model_name]

        def do_download():
            return self.download_model(model_name)
        model_path = safe_call(do_download, error_msg=f"[ModelManager] Could not download {model_name}, checking offline cache...", default=self.models_dir / model_name)
        if not model_path.exists():
            raise RuntimeError(f"No offline model available for {model_name}")

        # Robust error boundary for model instantiation
        def do_instantiate():
            return HybridLLMRouter(
                llama_model_path=str(model_path / "model.bin"),
                gpt4all_model_path=str(model_path / "gpt4all.bin"),
                prefer_fast=True,
                memory_limit=8 * 1024 ** 3
            )
        llm = safe_call(do_instantiate, error_msg=f"[ModelManager] Error instantiating HybridLLMRouter for {model_name}", default=None)
        if llm is None:
            raise RuntimeError(f"Failed to instantiate model router for {model_name}")
        self.loaded_models[model_name] = llm
        return llm
