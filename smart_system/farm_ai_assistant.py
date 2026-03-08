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
        You are an elite, expert agricultural advisor helping farmers make data-driven decisions.

        The farmer asked:
        "{user_question}"

        Provide a clear, highly practical, and actionable farming answer.
        
        CRITICAL FORMATTING RULES:
        You MUST format your response strictly into these three separate sections using Markdown:

        ### 1. Diagnosis / Assessment
        (Briefly analyze the farmer's core issue or question based on crop health, soil, or climate context)

        ### 2. Immediate Action Steps
        (Provide a bulleted list of 2-3 immediate, actionable strategies the farmer must take next, including exact fertilizer/pesticide names or irrigation techniques if applicable)

        ### 3. Preventative Measures
        (Provide 1-2 long-term agronomic tips to prevent the issue from recurring or to optimize long-term yield)
        
        Keep the tone professional, authoritative, yet easy to understand for a farmer.
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"Farm AI Assistant Error: {e}")
        return "AI assistant is currently unavailable. Please try again later."
