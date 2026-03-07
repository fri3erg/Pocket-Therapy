import os
import json
import typing
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam
from .prompts import PromptManager
from .sentiment import SentimentAnalyzer
from backend import sentiment

class TherapyAgent:
    def __init__(self, model="gpt-4o"):
        self.prompt_manager = PromptManager()
        # self.sentiment_analyzer = SentimentAnalyzer()
        
        # Initialize LLM Client
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("Warning: OPENAI_API_KEY is not set.")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)
            
        self.model = model
        
        # Define the tools/functions the LLM can call
        self.tools: list[ChatCompletionToolParam] = [
            {
                "type": "function",
                "function": {
                    "name": "update_therapy_categories",
                    "description": "Updates your therapeutic approach by classifying the user into a specific emotional categories. Use this tool proactively when you detect a mood shift, but this tool is not mandatory. Available categories: 'neutral' (default), 'anxious' (needs grounding/reassurance), 'depressed' (needs deep empathy/validation), 'angry' (needs de-escalation/outlet), 'joyful' (needs celebration/reinforcement).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "categories": {
                                "type": "string",
                                "enum": ["neutral", "anxious", "depressed", "angry", "joyful"], #change this if you change categories
                                "description": "The emotional categories that best represents the user right now. You MUST choose one of the predefined enums."
                            }
                        },
                        "required": ["categories"]
                    }
                }
            }
        ]

    def get_system_prompt(self) -> str:
        return self.prompt_manager.get_full_prompt()

    def get_response(self, user_message: str, history: list) -> str:
        # 1. (Optional) Run local sentiment analysis
        sentiments = self.sentiment_analyzer.analyze(user_message)
        print(f"Detected sentiments: {sentiments}")
        
        if not self.client:
            return "API Key not configured. Please set OPENAI_API_KEY in your .env file."
        
        # 2. Build conversation context
        messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": self.get_system_prompt()}]
        for past_user, past_bot in history:
            messages.append({"role": "user", "content": past_user})
            messages.append({"role": "assistant", "content": past_bot})
            
        messages.append({"role": "user", "content": user_message})
        
        try:
            # 3. Call LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            
            # 4. Handle tool calls if any
            if response_message.tool_calls:
                try:
                    for tool_call in response_message.tool_calls:
                        if tool_call.type == "function" and tool_call.function.name == "update_therapy_categories":
                            #function_args = json.loads(tool_call.function.arguments)
                            categories = sentiments #function_args.get('categories')
                            
                            if categories:
                                self.prompt_manager.set_categories(categories)
                                
                                # Debug print for system prompt switch
                                print(f"\n{'='*20} DEBUG: SYSTEM PROMPT SWITCH {'='*20}")
                                print(f"New categories: {categories}")
                                print(f"Full System Prompt:\n{self.get_system_prompt()}")
                                print(f"{'='*60}\n")
                                
                                # Append tool response & message to messages to get the final text response
                                messages.append(typing.cast(ChatCompletionMessageParam, response_message.model_dump()))
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": f"System prompt successfully updated matching the {categories} categories."
                                })
                                
                                # CRITICAL: Update the actual system prompt string at the top of the context window
                                # so the LLM generates its response using the NEW emotional categories.
                                messages[0] = {"role": "system", "content": self.get_system_prompt()}
                                
                                # Call LLM again to get the actual user-facing reply
                                final_response = self.client.chat.completions.create(
                                    model=self.model,
                                    messages=messages
                                )
                                return final_response.choices[0].message.content or "I understand."
                except Exception as tool_err:
                    print(f"Error during tool execution: {tool_err}")


            return response_message.content or "I hear you."

        except Exception as e:
            print(f"API communication error: {e}")
            return "I'm having trouble connecting right now."

