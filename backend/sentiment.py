from transformers import pipeline
class SentimentAnalyzer:
    def __init__(self):
        # future: self.classifier = pipeline("sentiment-analysis", model="bhadresh-savani/distilbert-base-uncased-emotion")
        pass
        
    def analyze(self, text: str) -> dict:
        # 1) General emotion model
        emotion_clf = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            top_k=None
        )

        # 2) Fine-grained emotion model
        goemotion_clf = pipeline(
            "text-classification",
            model="SamLowe/roberta-base-go_emotions",
            top_k=None
        )
        
        #3) Menthal ilness detection model
        MODEL_NAME = "dsuram/distilbert-mentalhealth-classifier"

        classifier = pipeline("text-classification", model=MODEL_NAME, top_k=None)


        emotion_out = emotion_clf(text)[0]
        goemotion_out = goemotion_clf(text)[0]
        mental_health_out = classifier(text)[0]


        top_emotion = max(emotion_out, key=lambda x: x["score"])

        k = 2
        goemotion_filtered = sorted(goemotion_out, key=lambda x: x["score"], reverse=True)[:k]
        
        top_mental_health = max(mental_health_out, key=lambda x: x["score"])

        combined = [top_emotion] + goemotion_filtered + [top_mental_health]


        filtered_emotions = list(dict.fromkeys(e["label"] for e in combined))

        print("Filtered emotions:", filtered_emotions)
        print("Emotion:", emotion_out)
        print("GoEmotions:", goemotion_out)
        print("Mental Health:", mental_health_out)
        return filtered_emotions
