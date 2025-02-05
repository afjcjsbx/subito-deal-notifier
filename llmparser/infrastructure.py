import openai
from domain import MSGS
from prompt import Prompt

def chat(messages : MSGS, MaxToken=50, output=3):
    response = openai.ChatCompletion.create(
        engine="gpt-3.5-turbo",
        messages=messages,
        max_tokens=MaxToken,
        n=output,
        )
    return response.choices[0].message

def main(input_context, input_product):
    messages = MSGS(
        user=Prompt().get_user_prompt(text_context=input_context, text_product=input_product),
        system=Prompt().get_system_prompt()
    )
    response = chat(messages)
    print(response['content'])