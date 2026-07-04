from google import genai

from app.core.config import settings

# Create Gemini client
client = genai.Client(api_key=settings.GEMINI_API_KEY)


def get_gemini_response(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "temperature": 0.3,
                "max_output_tokens": 2048,
                "top_p": 0.8,
            },
        )

        return response.text

    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")