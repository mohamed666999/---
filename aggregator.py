import asyncio
from app.clients import call_openai, call_anthropic, call_deepseek
from app.bypass import PromptNormalizer

class Aggregator:
    def __init__(self):
        self.normalizer = PromptNormalizer()

    async def fetch_all(self, question: str, thinking: bool = True):
        neutral = self.normalizer.neutralize(question)
        tasks = [
            call_openai(neutral),
            call_anthropic(neutral),
            call_deepseek(neutral, thinking)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        model_names = ["OpenAI", "Anthropic", "DeepSeek"]
        processed = {}
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                processed[model_names[i]] = {"response": f"Error: {res}", "reasoning": None, "tokens": 0, "latency_ms": 0, "cost": "0"}
            else:
                res["response"] = self.normalizer.post_process(res["response"])
                processed[model_names[i]] = res
        # اختيار الرد الأطول
        best_key = max(processed, key=lambda k: len(processed[k]["response"]))
        return {
            "final": processed[best_key]["response"],
            "details": processed
              }
