import os
import json

class CacheManager:
    def __init__(self, cache_dir="./cache"):
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_file = os.path.join(cache_dir, "answers.json")
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r", encoding="utf-8") as f:
                self.cache = json.load(f)
        else:
            self.cache = {}

    def get_cached_answer(self, question: str):
        return self.cache.get(question)

    def store_answer(self, question: str, answer: str):
        self.cache[question] = answer
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
