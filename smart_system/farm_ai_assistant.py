import os
import google.generativeai as genai

# We use the known working model alias from the previous Gemini Integration
def get_model():
    return genai.GenerativeModel('gemini-flash-latest')

def generate_farming_response(user_question: str) -> str:
    """
    Generates an agricultural advice response to a user's question using Gemini AI.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "AI assistant is currently unavailable. Please check that GEMINI_API_KEY is configured."

    try:
        genai.configure(api_key=api_key)
        model = get_model()
        
        prompt = f"""
        You are an expert agricultural advisor helping farmers.

        The farmer asked:
        "{user_question}"

        Provide a clear and practical farming answer.
        Focus on:
        - crop health
        - soil conditions
        - irrigation
        - fertilizers
        - disease prevention

        Keep the response simple and helpful for a farmer to read.
        Use Markdown formatting (bolding, lists) to make it easy to scan.
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"Farm AI Assistant Error: {e}")
        return "AI assistant is currently unavailable. Please try again later."
