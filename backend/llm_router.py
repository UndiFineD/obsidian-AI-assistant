# backend/llm_router.py
import os
from typing import Dict, List, Optional
import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer
from diffusers import StableDiffusionXLPipeline

try:
    from gpt4all import GPT4All
except ImportError:
    GPT4All = None


class HybridLLMRouter:
    """
    Hybrid LLM router that supports both text and image generation models.
    """

    def __init__(
        self,
        gpt4all_model_path: Optional[str] = None,
        transformers_model_path: Optional[str] = None,
        image_model_path: Optional[str] = None,
        prefer_fast: bool = True,
        session_memory: bool = True,
        memory_limit: int = 5,
    ):
        self.prefer_fast = prefer_fast
        self.session_memory = session_memory
        self.memory_limit = memory_limit
        self.memory: List[Dict[str, str]] = []

        # Set up device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load GPT4All
        self.gpt4all = None
        if (gpt4all_model_path and GPT4All and
                os.path.exists(gpt4all_model_path)):
            self.gpt4all = GPT4All(model_name=gpt4all_model_path)

        # Load Transformers
        self.text_model = None
        self.text_tokenizer = None
        if transformers_model_path and os.path.exists(transformers_model_path):
            # Use specific revision hash or tag for consistent behavior
            self.text_tokenizer = AutoTokenizer.from_pretrained(
                transformers_model_path,
                revision="v4.32.0"  # Example stable version tag
            )
            self.text_model = AutoModelForCausalLM.from_pretrained(
                transformers_model_path,
                device_map="auto",
                torch_dtype=torch.bfloat16,
                revision="v4.32.0"  # Example stable version tag
            )

        # Load Image Model
        self.image_pipeline = None
        if image_model_path and os.path.exists(image_model_path):
            # Use specific revision hash or tag for consistent behavior
            self.image_pipeline = StableDiffusionXLPipeline.from_pretrained(
                image_model_path,
                torch_dtype=torch.float16,
                use_safetensors=True,
                variant="fp16",
                revision="refs/pr/123"  # Example commit reference
            ).to(self.device)

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
        memory_str = "\n".join(
            [f"{m['role']}: {m['content']}" for m in self.memory]
        )
        return f"{memory_str}\nUser: {prompt}"

    # -------------------
    # Text Generation
    # -------------------
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 512
    ) -> str:
        context = self.build_context(prompt)
        
        # Try transformers model first
        if self.text_model and self.text_tokenizer:
            inputs = self.text_tokenizer(
                context,
                return_tensors="pt"
            ).to(self.device)
            
            outputs = self.text_model.generate(
                **inputs,
                max_length=max_tokens,
                pad_token_id=self.text_tokenizer.eos_token_id
            )
            text = self.text_tokenizer.decode(
                outputs[0],
                skip_special_tokens=True
            )
        
        # Fall back to GPT4All
        elif self.gpt4all:
            with self.gpt4all.chat_session():
                text = self.gpt4all.generate(context, max_tokens=max_tokens)
        
        else:
            text = "No text generation model available."

        # Update memory
        self.add_to_memory("User", prompt)
        self.add_to_memory("Assistant", text)
        return text

    # -------------------
    # Image Generation
    # -------------------
    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        width: int = 1024,
        height: int = 1024
    ) -> Optional[Image.Image]:
        if not self.image_pipeline:
            return None

        result = self.image_pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            width=width,
            height=height
        )
        
        return result.images[0] if result.images else None
