
"""
Groq API 
Pricing Constants
Accessed on: 2025-03-27
https://groq.com/pricing/
"""

# Pricing for DeepSeek R1 Distill Llama 70B
GROQ_PRICES = {
    "deepseek-r1-distill-llama-70b": {
        "input": 0.75 / 1000000,  # Per token
        "output": 0.99 / 1000000  # Per token
    },
    "llama-3.3-70b-versatile": {
        "input": 0.59 / 1000000,  # Per token
        "output": 0.79 / 1000000  # Per token
    }
}

