from openai import OpenAI
from dotenv import load_dotenv
import os, json
import re, json


# Load variables from .env file
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"   # <---- VERY IMPORTANT
)

PROMPT_TEMPLATE = """
You are a cybersecurity analyst. Given a structured flow event, answer three things in JSON:
1) attack_type
2) severity (1–10)
3) recommended_action (list)

Event:
{event}

Return JSON only.
"""

# def analyze_event(event: dict):
#     prompt = PROMPT_TEMPLATE.format(event=event)

#     response = client.chat.completions.create(
#         model="deepseek/deepseek-chat-v3.1:free",  # any OpenRouter model
#         messages=[{"role": "user", "content": prompt}],
#         max_tokens=300,
#         temperature=0.0
#     )

#     print(response)

#     out = response.choices[0].message.content

#     try:
#         return json.loads(out)
#     except:
#         return {"raw": out}

# def analyze_event(event: dict):
#     prompt = PROMPT_TEMPLATE.format(event=event)

#     try:
#         response = client.chat.completions.create(
#             model="google/gemma-3n-e2b-it:free",   # or your model
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=300,
#             temperature=0.0
#         )
#     except Exception as e:
#         return {"error": f"API request failed: {e}"}

#     # Debug print to see full response
#     print("\nRAW RESPONSE:", response, "\n")

#     # If API returned an error object
#     if hasattr(response, "error") and response.error is not None:
#         return {"error": f"API error: {response.error}"}

#     # If choices list is missing or empty
#     if not hasattr(response, "choices") or response.choices is None or len(response.choices) == 0:
#         return {"error": "No choices returned from model", "raw": str(response)}

#     # If message is missing
#     if response.choices[0].message is None:
#         return {"error": "Model returned no message content", "raw": str(response)}

#     # Extract assistant content
#     out = response.choices[0].message.content

#     # Try to parse JSON returned by the LLM
#     try:
#         return json.loads(out)
#     except:
#         return {"raw": out}

def analyze_event(event: dict):
    prompt = PROMPT_TEMPLATE.format(event=event)

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",   # stable model
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.0
        )
    except Exception as e:
        return {"error": f"API request failed: {e}"}

    # Debug print (optional)
    print("\nRAW RESPONSE:", response, "\n")

    # Safety checks
    if (not hasattr(response, "choices")
        or response.choices is None
        or len(response.choices) == 0
        or response.choices[0].message is None):
        return {"error": "Model returned no message", "raw_response": str(response)}

    # Extract raw text
    out = response.choices[0].message.content

    # Remove ```json ... ``` wrappers
    clean = re.sub(r"```json|```", "", out).strip()

    # Parse JSON
    try:
        return json.loads(clean)
    except Exception:
        return {"raw": out}
