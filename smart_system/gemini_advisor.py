import os
import google.generativeai as genai

# Setup Gemini API key
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# We use gemini-pro for text tasks
# In newer versions of the SDK, gemini-1.5-pro or gemini-1.0-pro might be available.
def get_model():
    return genai.GenerativeModel('gemini-flash-latest')

def generate_crop_advice(input_data: dict, prediction: dict) -> str:
    """
    Generates agricultural advice using the Gemini AI API.
    
    Args:
        input_data (dict): The soil and weather parameters (N, P, K, temperature, humidity, ph, rainfall).
        prediction (dict): The ML prediction results including top_crop and alternatives.
        
    Returns:
        str: The generated advice text, or a fallback message if the API fails or is not configured.
    """
    if not os.getenv("GEMINI_API_KEY"):
        return "AI advice temporarily unavailable. Please configure the GEMINI_API_KEY."

    try:
        model = get_model()
        
        prompt = f"""
        You are an agricultural expert AI.

        Soil and Climate Data:
        Nitrogen: {input_data.get('N')} kg/ha
        Phosphorus: {input_data.get('P')} kg/ha
        Potassium: {input_data.get('K')} kg/ha
        Temperature: {input_data.get('temperature')} °C
        Humidity: {input_data.get('humidity')} %
        pH: {input_data.get('ph')}
        Rainfall: {input_data.get('rainfall')} mm

        Machine Learning Prediction:
        Recommended Crop: {prediction.get('top_crop')}
        Alternatives: {', '.join(prediction.get('alternatives', []))}

        Explain briefly:
        1. Why the recommended crop fits the soil/climate.
        2. Why the alternatives are viable.
        3. One key action to maximize yield.
        
        CRITICAL: Provide your answer as exactly 3 very short, concise bullet points. Do not include any introductory or concluding text. Maximum 3 sentences total.
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "AI advice temporarily unavailable. (Service Error)"

