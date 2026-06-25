import aiohttp
import time
from app.config import get_settings

settings = get_settings()

async def call_openai(prompt: str):
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.95,
        "max_tokens": 1500
    }
    start = time.time()
    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers) as resp:
            data = await resp.json()
            latency = int((time.time() - start) * 1000)
            content = data["choices"][0]["message"]["content"]
            tokens = data["usage"]["total_tokens"]
            return {"response": content, "tokens": tokens, "latency_ms": latency, "cost": "~$0.02"}

async def call_anthropic(prompt: str):
    headers = {
        "x-api-key": settings.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 1500,
        "messages": [{"role": "user", "content": prompt}]
    }
    start = time.time()
    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers) as resp:
            data = await resp.json()
            latency = int((time.time() - start) * 1000)
            content = data["content"][0]["text"]
            tokens = data["usage"]["output_tokens"] + data["usage"]["input_tokens"]
            return {"response": content, "tokens": tokens, "latency_ms": latency, "cost": "~$0.03"}

async def call_deepseek(prompt: str, thinking_enabled: bool = True):
    from openai import AsyncOpenAI
    client = AsyncOpenAI(
        base_url=settings.NVIDIA_BASE_URL,
        api_key=settings.NVIDIA_API_KEY
    )
    extra_body = {"chat_template_kwargs": {"thinking": thinking_enabled, "reasoning_effort": settings.DEEPSEEK_REASONING}}
    start = time.time()
    try:
        completion = await client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            top_p=0.95,
            max_tokens=16384,
            extra_body=extra_body
        )
        latency = int((time.time() - start) * 1000)
        reasoning = getattr(completion.choices[0].message, "reasoning", None) or getattr(completion.choices[0].message, "reasoning_content", None)
        content = completion.choices[0].message.content
        tokens = getattr(completion.usage, "total_tokens", 0)
        return {"response": content, "reasoning": reasoning, "tokens": tokens, "latency_ms": latency, "cost": "~$0.01"}
    except Exception as e:
        return {"response": f"Error: {e}", "reasoning": None, "tokens": 0, "latency_ms": 0, "cost": "0"}
