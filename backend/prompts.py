import json

class PromptManager:
    def __init__(self):
        self.base_prompt = (
            "You are a helpful and empathetic Pocket Therapist. "
            "You listen to the user and help them work through their emotions. "
            "You should adjust your therapy approach using the 'update_therapy_category' tool when you "
            "detect a shift in the user's core emotional state or needs."
        )
        
        self.categories = {
            "neutral": "The user is currently feeling neutral. Ask open-ended questions to explore what they want to discuss.",
            "anxious": "The user is expressing anxiety. Use grounding techniques, reassure them, and break things down into smaller steps.",
            "depressed": "The user is feeling sad or depressed. Show deep empathy, validate their feelings, and avoid toxic positivity.",
            "angry": "The user is angry or frustrated. De-escalate, validate their frustration without judgment, and help them find a constructive outlet.",
            "joyful": "The user is expressing happiness or success. Celebrate with them, reinforce their positive actions, and help them savor the moment."
        }
        
        self.current_category = "neutral"
        
    def get_full_prompt(self) -> str:
        state_prompt = self.categories.get(self.current_category, self.categories["neutral"])
        return f"{self.base_prompt}\n\nCurrent Context/State ({self.current_category}):\n{state_prompt}"
        
    def set_category(self, category: str):
        """
        This method will be called via the LLM's function calling feature
        to adapt its own instructions based on the conversation evolution.
        """
        if category in self.categories:
            self.current_category = category
            print(f"[PromptManager] Switched therapy category to: {category}")
        else:
            print(f"[PromptManager] Attempted to switch to unknown category: {category}")
