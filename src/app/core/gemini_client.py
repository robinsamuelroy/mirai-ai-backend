import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

gemini_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config={
        "temperature": 0.3,
        "max_output_tokens": 2048,
        "top_p": 0.8,
    }
)


def get_gemini_response(prompt: str) -> str:
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")
