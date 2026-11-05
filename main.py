import os
from openai import OpenAI
from dotenv import load_dotenv
from Utils.util import log

load_dotenv()

base_api = os.getenv("BASE_API")
api_key = os.getenv("API_KEY")
model = os.getenv("MODEL")

clint = OpenAI(
    base_url=base_api,
    api_key=api_key,
)

messages = [{
    "role": "system",
    "content": "You are a helpful assistant. Answer accurately using the entire conversation history and within maximum 20 words only"
}]

while True:
    user_input = input("User: ")

    if user_input.lower() in ["exit", "bye", "goodbye", "quit"]:
        break

    log(f"-> {model}")

    messages.append({
        "role":"user",
        "content":user_input
    })

    log(f"   thinking...")
        
    response = clint.chat.completions.create(
        model=model,
        messages=messages
    )  

    assistant_role = response.choices[0].message.role
    assistant_reply = response.choices[0].message.content

    messages.append({
        "role": assistant_role,
        "content": assistant_reply
    })

    print("LLM-" + assistant_role + ": " + assistant_reply)