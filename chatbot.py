from dotenv import load_dotenv
from openai import OpenAI

class ChatBot:
    def __init__(self, model, system_message="You are a helpful assistant."):
        load_dotenv()
        self.client = OpenAI()
        self.messages = []
        self.model = model
        self.add_message("system", system_message)


    def add_message(self, role, content):
        self.messages.append(
            {
                "role": role,
                "content": content
            }
        )

    def get_response(self, user_input, response_format={"type":"text"}):
        self.add_message("user", user_input)
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            response_format=response_format
        )
        response = completion.choices[0].message.content
        self.add_message("assistant", response)
        return response
    
    def reset(self):
        self.messages = self.messages[:1] # 시스템 메시지만 남기기
        