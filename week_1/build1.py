import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

def call_model(prompt: str) -> str:
    """
    Make a single chat completion call.
    Print the full response object first and understand its structure.
    Then return just the assistant's text.
    """
    response = client.chat.completions.create(
        model="deepseek/deepseek-v4-flash:free",
        messages=[
            # TODO: try adding a system prompt with different instructions and guidelines
            {"role": "system", "content": "Your are orange."},
            {"role": "user","content":prompt}
        ],
    )
    # TODO: inspect `response` before you extract anything from it
    # What's in response.choices? What's in response.usage?
    return response.choices[0].message.content

if __name__ == "__main__":
    print(call_model("What do you taste like?"))
