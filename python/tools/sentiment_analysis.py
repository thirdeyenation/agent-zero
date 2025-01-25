import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    return scores

if __name__ == '__main__':
    text = "This is a great day!"
    sentiment_scores = analyze_sentiment(text)
    print(sentiment_scores)
    text = "This is a terrible day!"
    sentiment_scores = analyze_sentiment(text)
    print(sentiment_scores)
    text = "This is an okay day."
    sentiment_scores = analyze_sentiment(text)
    print(sentiment_scores)
