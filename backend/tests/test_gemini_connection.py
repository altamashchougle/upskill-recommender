import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini_connection():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    print(f"GEMINI_API_KEY exists: {bool(api_key)}")
    print(f"Key length: {len(api_key)}")
    
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("Failure: GEMINI_API_KEY not found or invalid in .env")
        return

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        print("CALLING GEMINI MODEL...")
        response = model.generate_content("Return only the word SUCCESS")
        text = response.text.strip()
        if "SUCCESS" in text.upper():
            print(f"Success: {text} response received")
        else:
            print(f"Success: response received ({text})")
    except Exception as e:
        print(f"Failure: {e}")

if __name__ == "__main__":
    test_gemini_connection()
