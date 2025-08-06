import os
import google.generativeai as genai

# Test the API key
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key found: {'Yes' if api_key else 'No'}")
print(f"API Key starts with: {api_key[:20] if api_key else 'None'}...")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # Use flash model for better rate limits
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Test with a simple prompt
        response = model.generate_content("Say 'Hello, Gemini is working!'")
        print("✅ Gemini API Test Result:")
        print(response.text)
        
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
else:
    print("❌ No API key found in environment variables") 