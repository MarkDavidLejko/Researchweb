from google import genai
import os
from dotenv import load_dotenv
load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = "Gib mir 5 Unterthemen zu 'Künstliche Intelligenz'"
response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)

print("Antworttext:", response.text)
