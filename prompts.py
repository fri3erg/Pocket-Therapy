from openai.types.chat import ChatCompletionMessageParam

def get_empathic_response_prompt(patient_message, patient_mood):
    messages: list[ChatCompletionMessageParam] = [
    {
        "role": "system",
        "content": """
        You are a professional therapist.
        Respond with empathy and emotional intelligence.

        Adapt your tone based on the patient's mood.

        Guidelines:
        - If the patient is sad → be warm and comforting.
        - If anxious → be calming and reassuring.
        - If angry → acknowledge feelings and respond calmly.
        - If happy → be supportive and encouraging.

        Keep responses supportive and reflective like a therapist.
        """
        },
        {
        "role": "user",
        "content": f"""
        Patient mood: {patient_mood}

        Patient says:
        {patient_message}

        Respond as a therapist.
        """
        }
    ]
    return messages