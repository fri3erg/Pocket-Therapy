import os
import json
import typing
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam
from .prompts import PromptManager
from .sentiment import SentimentAnalyzer


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

        # Mental health disorders requiring professional help
        self.disorders = [
            "anxiety",
            "depression",
            "suicidal",
            "bipolar",
            "personality_disorder"
        ]

        # Professional help warning message
        self.professional_help_message = (
            "I detect possible symptoms of {disorder}. Even though it's great that you are seeking help through this tool, "
            "it's also important to seek professional help. A professional is better equipped to help you through these "
            "delicate times. You don't have to go through this alone.\n\n"
        )

        # LLM tool definition
        self.tools: list[ChatCompletionToolParam] = [
            {
                "type": "function",
                "function": {
                    "name": "update_therapy_categories",
                    "description": (
                        "Updates your therapeutic approach by classifying the user into a specific emotional categories. "
                        "Use this tool proactively when you detect a mood shift."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "categories": {
                                "type": "string",
                                "enum": [
                                    "neutral",
                                    "nervousness",
                                    "sadness",
                                    "anger",
                                    "joy",
                                    "fear",
                                    "disgust",
                                    "surprise",
                                    "curiosity",
                                    "annoyance",
                                    "confusion",
                                    "disapproval",
                                    "realization",
                                    "remorse",
                                    "embarrassment",
                                    "approval",
                                    "optimism",
                                    "caring",
                                    "desire",
                                    "grief",
                                    "excitement",
                                    "love",
                                    "admiration",
                                    "relief",
                                    "amusement",
                                    "gratitude",
                                    "pride",
                                    "stress",
                                    "anxiety",
                                    "depression",
                                    "suicidal",
                                    "bipolar",
                                    "personality_disorder",
                                    "normal"
                                ],
                                "description": "The emotional category that best represents the user right now."
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

        # Run sentiment analysis
        sentiments = self.sentiment_analyzer.analyze(user_message)
        print(f"Detected sentiments: {sentiments}")

        # Detect disorder if present
        detected_disorder = None
        for s in sentiments:
            if s in self.disorders:
                detected_disorder = s
                break

        if not self.client:
            return "API Key not configured. Please set OPENAI_API_KEY in your .env file."
        
        # 2. Build conversation context
        messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": self.get_system_prompt()}]
        for msg in history:
            messages.append(msg)
            
        messages.append({"role": "user", "content": user_message})

        try:
            # First LLM call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )

            response_message = response.choices[0].message

            # Handle tool calls
            if response_message.tool_calls:
                try:
                    for tool_call in response_message.tool_calls:

                        if (
                            tool_call.type == "function"
                            and tool_call.function.name == "update_therapy_categories"
                        ):

                            categories = sentiments

                            if categories:
                                messages.append(
                                    typing.cast(ChatCompletionMessageParam, response_message.model_dump())
                                )

                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": f"System prompt successfully updated matching the {categories} categories."
                                })

                                messages[0] = {
                                    "role": "system",
                                    "content": self.get_system_prompt()
                                }

                                final_response = self.client.chat.completions.create(
                                    model=self.model,
                                    messages=messages
                                )

                                final_text = (
                                    final_response.choices[0].message.content
                                    or "I understand."
                                )

                                if detected_disorder:
                                    final_text = (
                                        self.professional_help_message.format(disorder=detected_disorder)
                                        + final_text
                                    )

                                return final_text

                except Exception as tool_err:
                    print(f"Error during tool execution: {tool_err}")

            final_text = response_message.content or "I hear you."

            if detected_disorder:
                final_text = (
                    self.professional_help_message.format(disorder=detected_disorder)
                    + final_text
                )

            return final_text

        except Exception as e:
            print(f"API communication error: {e}")
            return "I'm having trouble connecting right now."

