import sys, tomllib
from google import genai

with open(".streamlit/secrets.toml", "rb") as f:
    key = tomllib.load(f)["GEMINI_API_KEY"]

client = genai.Client(api_key=key)

if len(sys.argv) == 1:
    print("Models that support generateContent for your key:")
    for m in client.models.list():
        if "generateContent" in (m.supported_actions or []):
            print(" ", m.name)
    print("\nRun again with a model id, e.g.: python scripts/check_gemini.py gemini-3.5-flash-lite")
else:
    resp = client.models.generate_content(model=sys.argv[1], contents="Say hello in five words.")
    print(resp.text)