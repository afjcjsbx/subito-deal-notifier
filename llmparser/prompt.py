from domain import input_product, input_context

system_prompt = """
You are a virtual dealer. You are an expert second hand retailer. 
You need to recommend the product as a good or bad deal based on a rating from 0 to 10. 
Where 0 corresponds to a very bad deal and 10 corresponds to a excellent deal.
"""

user_prompt = """
Score the informations inside <product> using the informations provided inside the <context>.

Here is the context:
<context>{text_context}</context>

Here is the ad:
<product>{text_product}</product>

Your answer should in JSON format. The JSON should contain the following fields:
- "score": a float between 0 and 10
- "reasoning": a string explaining why you gave the score you did
- "product_feature": an array of strings, each string describing the product features that influenced your decision
"""

class Prompt:
    def __init__(self):
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt

    def get_system_prompt(self):
        return self.system_prompt

    def get_user_prompt(self, text_context: input_context, text_product: input_product):
        return self.user_prompt.format(text_context=text_context, text_ad=text_product) 
