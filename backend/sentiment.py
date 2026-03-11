from transformers import pipeline 
THRESHOLD = 0.8
class SentimentAnalyzer:   

    def __init__(self):
        # future: self.classifier = pipeline("sentiment-analysis", model="bhadresh-savani/distilbert-base-uncased-emotion")
        # 1) General emotion model
        self.emotion_clf = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            top_k=None
        )

        # 2) Fine-grained emotion model
        self.goemotion_clf = pipeline(
            "text-classification",
            model="SamLowe/roberta-base-go_emotions",
            top_k=None
        )
        
        #3) Menthal ilness detection model
        MODEL_NAME = "dsuram/distilbert-mentalhealth-classifier"

        self.classifier = pipeline("text-classification", model=MODEL_NAME, top_k=None)
        
    def analyze(self, text: str) -> dict:
        emotion_out = self.emotion_clf(text)[0]
        goemotion_out = self.goemotion_clf(text)[0]
        mental_health_out = self.classifier(text)[0]


        top_emotion = max(emotion_out, key=lambda x: x["score"])

        k = 2
        goemotion_filtered = sorted(goemotion_out, key=lambda x: x["score"], reverse=True)[:k]
        
        mental_health_filtered = [e for e in mental_health_out if e["score"] >= THRESHOLD]
        top_mental_health = [max(mental_health_filtered, key=lambda x: x["score"])] if mental_health_filtered else []

        combined = [top_emotion] + goemotion_filtered + top_mental_health


        filtered_emotions = list(dict.fromkeys(e["label"] for e in combined))

        print("Filtered emotions:", filtered_emotions)
        print("Emotion:", emotion_out)
        print("GoEmotions:", goemotion_out)
        print("Mental Health:", mental_health_out)
        return filtered_emotions
