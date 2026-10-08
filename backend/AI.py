from google import genai
from dotenv import load_dotenv
import os

load_dotenv()


client = genai.Client(api_key=os.getenv("API_key"))


def ask_gemini(prompt):
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )

    return response.text
