import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class ChatAgent:
    def __init__(self, model : str, system_prompt: str):
        
        self.model = model
        
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1",
                        api_key=os.environ["OPENROUTER_API_KEY"],
        )
        self.my_list = [{"role": "system","content":system_prompt}]
    def call_model(self,user_input: str) ->str :
            if len(self.my_list)>7:
                self.my_list.append({'role':'user', 'content': 'summarize last 7 response in one python code so you can understand the longer converstation without loss of quality.'})
                background_response = self.client.chat.completions.create(
                    model = self.model,
                    messages = self.my_list[1:]
                )
                back_response = background_response.choices[0].message.content
                self.my_list = [self.my_list[0]]
                self.my_list.append({"role":"assistant", "content": back_response})
            self.my_list.append({'role':'user', 'content': user_input})
            
            response = self.client.chat.completions.create(
                model = self.model,
                messages = self.my_list
            )
            response_ai = response.choices[0].message.content
            self.my_list.append({"role":"assistant","content": response_ai})
            return response_ai
        
        