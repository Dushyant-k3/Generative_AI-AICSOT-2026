import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

def run_chatbot():
    """
    A terminal chatbot that holds a coherent multi-turn conversation.

    Your implementation should:
    - Start with a system message that sets the assistant's behaviour.
    - Maintain a `messages` list with alternating user/assistant turns.
    - Append the assistant's reply to `messages` after each call.
    - Resend the full history on every API call.
    - Allow the user to type 'exit' or 'quit' to end the session.

    Stretch:
    - Add a '/reset' command that clears history so you can feel context loss live.
    - Add a '/tokens' command that prints response.usage after the last call.
    """

    print("Chat started. Type 'exit' to quit.\n")

    
    
    message = []
    
    global_instruction = input('Please enter the System prompt: ')
    if global_instruction in ['exit','quit']:
        print("GoodBye!")
        return

    message.append({'role':'system', 'content': global_instruction})
    print("Chat started, enter 'exit' or 'quit' to exit.")
    while True:
        
    
        user_input = input('YOU: ')
        
        if user_input in ['exit','quit']:
            print("GoodBye!")
            return
        elif user_input == '/reset':
            message = [message[0]]
        elif user_input == '/tokens':
            try:
                print(response.usage)
            except:
                print(None)
        else:
            message.append({'role':'user','content' : user_input})
            response = client.chat.completions.create(        
                model = "openrouter/free",
                messages= message)
            
            responce_from_ai = response.choices[0].message.content
            print(f"AI: {responce_from_ai}")
            message.append({'role':'assistant', 'content': responce_from_ai})

        
        
        
        # TODO: take user input
        # TODO: append the user turn to messages
        # TODO: call the API with the full messages list
        # TODO: extract the assistant's reply
        # TODO: append the assistant turn to messages
        # TODO: print the reply


if __name__ == "__main__":
    run_chatbot()
