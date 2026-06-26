from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPEN_API_KEY")
)

response = client.chat.completions.create(
    model="openai/gpt-4o",
    temperature=0.1,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "2022년 월드컵 우승팀은 어디야?"}
    ]
)


print("--------------------------------")
print(response.choices[0].message.content)
