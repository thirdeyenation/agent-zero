import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

sentence = "This is a great and amazing product!"

# NLTK VADER
sia = SentimentIntensityAnalyzer()
vader_score = sia.polarity_scores(sentence)
print(f"VADER Score: {vader_score}")

# TextBlob
tb = TextBlob(sentence)
tb_score = tb.sentiment
print(f"TextBlob Score: {tb_score}")