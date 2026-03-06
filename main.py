import os
from dotenv import load_dotenv
from backend.chat import TherapyAgent

# Load environment variables (e.g., OPENAI_API_KEY)
load_dotenv()

def run_terminal_chat():
    print("--------------------------------------------------")
    print("Initializing Pocket Therapy...")
    agent = TherapyAgent()
    history = []
    
    print("Pocket Therapy Chatbot is ready!")
    print("Type 'quit' or 'exit' to end the session.")
    print("--------------------------------------------------\n")
    
    while True:
        try:
            if not history:
                # Add a standard welcome message on the first run
                welcome_msg = "Hello! I'm your Pocket Therapist. How can I support you today?"
                print(f"\nTherapist: {welcome_msg}\n")
                # We do not strictly need to add this to the LLM's history immediately unless the user replies,
                # but appending it as a starting assistant message can set a good context.
                history.append(("Hi", welcome_msg))

            user_input = input("You: ")
            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
                
            if not user_input.strip():
                continue
                
            response = agent.get_response(user_input, history)
            print(f"\nTherapist: {response}\n")
            
            # Optionally print the current system prompt state to track function calling changes
            # print(f"[Debug] Current System Prompt: {agent.get_system_prompt()}\\n")
            
            history.append((user_input, response))
            
        except KeyboardInterrupt:
            print("\nSession ended. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}\n")

if __name__ == "__main__":
    run_terminal_chat()
