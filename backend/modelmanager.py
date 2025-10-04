# backend/modelmanager.py
import os
from pathlib import Path
from typing import Dict, Optional, Literal
from dotenv import load_dotenv
import huggingface_hub
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer
from diffusers import StableDiffusionXLPipeline
from .llm_router import HybridLLMRouter

ModelType = Literal["text", "image"]

class ModelManager:
    """Manages local and Hugging Face models for LLMs and image generation."""

    def __init__(
        self,
        models_dir="./models",
        env_file=".env",
        models_file="models.txt",
        default_model="gpt4all-lora",
        hf_token: str = None
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
        self.loaded_models: Dict[str, Dict[str, any]] = {}

        # Load available models from models.txt
        self.text_models, self.image_models = self._load_models_file(models_file)

        # Default model
        self.default_model = default_model
        if self.default_model not in self.text_models:
            if self.text_models:
                self.default_model = next(iter(self.text_models))
                print(f"[ModelManager] Default model not found. Using: {self.default_model}")
            else:
                print("[ModelManager] No text models available!")
                self.default_model = None

        # Device selection
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[ModelManager] Using device: {self.device}")

    def _load_models_file(self, models_file: str):
        models_path = Path(models_file)
        if not models_path.exists():
            print(f"[ModelManager] Warning: {models_file} not found. No models loaded.")
            return {}, {}

        text_models = {}
        image_models = {}
        current_section = None

        with open(models_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith("#"):
                    if "Text Generation" in line:
                        current_section = "text"
                    elif "Image Generation" in line:
                        current_section = "image"
                    continue

                model_info = line.split(":")
                model_id = model_info[0]
                model_name = model_info[-1].split("/")[-1].lower()

                if current_section == "text":
                    text_models[model_name] = model_id
                elif current_section == "image":
                    image_models[model_name] = model_id

        print(f"[ModelManager] Loaded {len(text_models)} text models and {len(image_models)} image models")
        return text_models, image_models

    def download_model(self, model_name: str, model_type: ModelType):
        models = self.text_models if model_type == "text" else self.image_models
        if model_name not in models:
            raise ValueError(f"Unknown {model_type} model: {model_name}")

        model_path = self.models_dir / model_name
        if not model_path.exists():
            print(f"[ModelManager] Downloading {model_name}...")
            huggingface_hub.snapshot_download(
                repo_id=models[model_name],
                cache_dir=str(model_path)
            )
        return model_path

    def load_text_model(self, model_name: Optional[str] = None) -> HybridLLMRouter:
        if not model_name:
            model_name = self.default_model
        if not model_name:
            raise ValueError("No default text model available to load.")

        if model_name in self.loaded_models and "text" in self.loaded_models[model_name]:
            return self.loaded_models[model_name]["text"]

        try:
            model_path = self.download_model(model_name, "text")
        except Exception as e:
            print(f"[ModelManager] Could not download {model_name} ({e}), checking offline cache...")
            model_path = self.models_dir / model_name
            if not model_path.exists():
                raise RuntimeError(f"No offline model available for {model_name}")

        # Check if it's a gpt4all model
        if "gpt4all" in str(model_path):
            llm = HybridLLMRouter(
                gpt4all_model_path=str(model_path / "gpt4all.bin"),
                prefer_fast=True,
                memory_limit=8 * 1024 ** 3
            )
        else:
            # Load Hugging Face transformers model
            tokenizer = AutoTokenizer.from_pretrained(str(model_path))
            model = AutoModelForCausalLM.from_pretrained(
                str(model_path),
                device_map="auto",
                torch_dtype=torch.bfloat16
            )
            llm = {"model": model, "tokenizer": tokenizer}

        if model_name not in self.loaded_models:
            self.loaded_models[model_name] = {}
        self.loaded_models[model_name]["text"] = llm
        return llm

    def load_image_model(self, model_name: Optional[str] = None) -> StableDiffusionXLPipeline:
        if not model_name and self.image_models:
            model_name = next(iter(self.image_models))
        if not model_name:
            raise ValueError("No image model available to load.")

        if model_name in self.loaded_models and "image" in self.loaded_models[model_name]:
            return self.loaded_models[model_name]["image"]

        try:
            model_path = self.download_model(model_name, "image")
        except Exception as e:
            print(f"[ModelManager] Could not download {model_name} ({e}), checking offline cache...")
            model_path = self.models_dir / model_name
            if not model_path.exists():
                raise RuntimeError(f"No offline model available for {model_name}")

        # Load Stable Diffusion XL pipeline
        pipeline = StableDiffusionXLPipeline.from_pretrained(
            str(model_path),
            torch_dtype=torch.float16,
            use_safetensors=True,
            variant="fp16"
        )
        pipeline = pipeline.to(self.device)

        if model_name not in self.loaded_models:
            self.loaded_models[model_name] = {}
        self.loaded_models[model_name]["image"] = pipeline
        return pipeline

    def generate_text(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        max_length: int = 512
    ) -> str:
        model = self.load_text_model(model_name)

        # Handle gpt4all models
        if isinstance(model, HybridLLMRouter):
            return model.generate(prompt, max_tokens=max_length)

        # Handle Hugging Face models
        tokenizer: PreTrainedTokenizer = model["tokenizer"]
        model: PreTrainedModel = model["model"]

        inputs = tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = model.generate(
            **inputs,
            max_length=max_length,
            pad_token_id=tokenizer.eos_token_id
        )
        return tokenizer.decode(outputs[0], skip_special_tokens=True)

    def generate_image(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        negative_prompt: str = None,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        width: int = 1024,
        height: int = 1024
    ):
        pipeline = self.load_image_model(model_name)
        image = pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            width=width,
            height=height
        ).images[0]
        return image
