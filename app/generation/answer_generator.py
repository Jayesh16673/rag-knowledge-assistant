from ctransformers import AutoModelForCausalLM

MODEL_PATH = "models/tinyllama-1.1b-chat-v1.0-q4_k_m.gguf"

llm = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    model_type="llama",
    max_new_tokens=256,
    temperature=0.0,
    context_length=2048
)


def generate_answer(question: str, context: str) -> str:
    """
    Generates a grounded answer strictly from provided context
    """

    prompt = f"""
You are a helpful assistant.
Answer ONLY using the provided context.
If the answer is not in the context, say "I don’t know".

Context:
{context}

Question:
{question}

Answer:
"""

    response = llm(prompt)
    return response.strip()
