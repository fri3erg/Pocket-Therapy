import os
from dotenv import load_dotenv
from backend.chat import TherapyAgent
from frontend.gradio_app import create_ui

# Load environment variables
load_dotenv()

"""
def run_terminal_chat():
    print("--------------------------------------------------")
    print("Initializing Pocket Therapy...")
    agent = TherapyAgent()
    history = []
    
    print("Pocket Therapy Chatbot is ready!")
    print("--------------------------------------------------\n")
    
    while True:
        try:
            if not history:
                # Add a standard welcome message on the first run
                welcome_msg = "Hello! I'm your Pocket Therapist. How can I support you today?"
                print(f"\nTherapist: {welcome_msg}\n")
                # We do not strictly need to add this to the LLM's history
                #history.append(("Hi", welcome_msg))

            user_input = input("You: ")
                
            if not user_input.strip():
                continue
                
            response = agent.get_response(user_input, history)
            print(f"\nTherapist: {response}\n")
            
            history.append((user_input, response))
            
        except KeyboardInterrupt:
            print("\nSession ended. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}\n")

"""

if __name__ == "__main__":
    demo = create_ui()
    demo.launch()
