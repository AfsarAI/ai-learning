from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()

base_api = os.getenv("BASE_API")
api_key = os.getenv("API_KEY")
model = os.getenv("MODEL")

clint = OpenAI(
    base_url=base_api,
    api_key=api_key,
)

while True:
    user_input = input("User: ")

    if user_input.lower() in ["exit", "bye", "goodbye", "quit"]:
        break

    response = clint.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    print("LLM-" + response.choices[0].message.role + ": " + response.choices[0].message.content)