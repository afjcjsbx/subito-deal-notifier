import openai
from domain import MSGS

def chat(messages : MSGS, MaxToken=50, output=3):
    response = openai.ChatCompletion.create(
        engine="gpt-3.5-turbo",
        messages=MSGS,
        max_tokens=MaxToken,
        n=output,
        )
    return response.choices[0].message