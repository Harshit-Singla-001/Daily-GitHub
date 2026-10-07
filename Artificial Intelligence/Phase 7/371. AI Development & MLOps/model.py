import time


class SentimentModel:

    def __init__(
        self,
        name,
        version,
    ):
        self.name = name
        self.version = version

    def predict(self, text):

        start = time.perf_counter()

        normalized = text.lower()

        positive_words = {
            "good",
            "great",
            "excellent",
            "amazing",
            "love",
            "best",
            "happy",
            "awesome",
        }

        negative_words = {
            "bad",
            "terrible",
            "worst",
            "hate",
            "poor",
            "awful",
            "sad",
            "horrible",
        }

        words = set(
            normalized.split()
        )

        positive_score = len(
            words.intersection(
                positive_words
            )
        )

        negative_score = len(
            words.intersection(
                negative_words
            )
        )

        if positive_score > negative_score:
            sentiment = "positive"

        elif negative_score > positive_score:
            sentiment = "negative"

        else:
            sentiment = "neutral"

        latency = (
            time.perf_counter()
            - start
        )

        return {
            "sentiment": sentiment,
            "model_name": self.name,
            "model_version": self.version,
            "inference_latency_ms": round(
                latency * 1000,
                3,
            ),
        }