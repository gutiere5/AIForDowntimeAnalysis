# Central place to define which LLMs are allowed in the app.
# Option A: only allow models that support the HF "conversational" (chat-completions) task.

DEFAULT_MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"

ALLOWED_MODEL_IDS = {
    "meta-llama/Llama-3.1-8B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "google/gemma-7b-it",
    "dphn/Dolphin-Mistral-24B-Venice-Edition",
}
