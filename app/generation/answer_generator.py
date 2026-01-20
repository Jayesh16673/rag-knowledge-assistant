from ctransformers import AutoModelForCausalLM

MODEL_PATH = "models/tinyllama-1.1b-chat-v1.0-q4_k_m.gguf"

llm = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    model_type="llama",
    max_new_tokens=256,
    temperature=0.0,
    context_length=2048,
    gpu_layers=0  # CPU inference (set to 20+ if GPU available)
)

# Cache for identical Q&A pairs
_answer_cache = {}


def generate_answer(question: str, context: str) -> str:
    """
    Generates a grounded answer strictly from provided context.
    Uses caching for identical queries.
    """

    # Cache key: hash of question + first 100 chars of context
    cache_key = hash((question, context[:100]))

    if cache_key in _answer_cache:
        return _answer_cache[cache_key]

    prompt = f"""You are a helpful assistant.
Answer ONLY using the provided context.
If the answer is not in the context, say "I don't know".

Context:
{context}

Question:
{question}

Answer:"""

    response = llm(prompt)
    answer = response.strip()

    # Store in cache
    _answer_cache[cache_key] = answer

    return answer


def clear_answer_cache():
    """Clear the answer cache"""
    global _answer_cache
    _answer_cache.clear()
