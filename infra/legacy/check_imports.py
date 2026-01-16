try:
    from pydantic_ai.models.openai import OpenAIModel
    print("OpenAIModel import: OK")
except ImportError as e:
    print(f"OpenAIModel import: FAILED - {e}")

try:
    from pydantic_ai.models.groq import GroqModel
    print("GroqModel import: OK")
except ImportError as e:
    print(f"GroqModel import: FAILED - {e}")

try:
    from pydantic_ai.models.mistral import MistralModel
    print("MistralModel import: OK")
except ImportError as e:
    print(f"MistralModel import: FAILED - {e}")
