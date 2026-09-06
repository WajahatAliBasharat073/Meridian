"""Real, currently-active Groq-hosted chat models — confirmed against
console.groq.com's live model picker (not the deprecated llama-3.1-8b-instant
/ llama-3.3-70b-versatile IDs still hardcoded as an old default elsewhere).
Speech-to-text (whisper), TTS (canopylabs) and safety-classifier
(prompt-guard, gpt-oss-safeguard) models are omitted — this list is for
picking a model for text/chat features, not for those specialized tasks."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GroqModel:
    id: str
    label: str
    description: str


GROQ_MODELS: list[GroqModel] = [
    GroqModel("openai/gpt-oss-120b", "GPT-OSS 120B", "Flagship open-weight model, strongest reasoning."),
    GroqModel("openai/gpt-oss-20b", "GPT-OSS 20B", "Smaller and faster, lower cost per token."),
    GroqModel("groq/compound", "Compound", "Agentic system with built-in web search and code execution."),
    GroqModel("groq/compound-mini", "Compound Mini", "Lighter agentic variant of Compound."),
    GroqModel("qwen/qwen3.6-27b", "Qwen 3.6 27B", "Alibaba's Qwen model, 27B parameters."),
]

DEFAULT_MODEL_ID = "openai/gpt-oss-120b"

_BY_ID = {m.id: m for m in GROQ_MODELS}


def is_known_model(model_id: str) -> bool:
    return model_id in _BY_ID
