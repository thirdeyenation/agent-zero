from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer


def summarize_text(text, num_sentences=3):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary = summarizer(parser.document, num_sentences)
    return summary

sample_text = """This is a sample document about natural language processing. Natural language processing is a subfield of artificial intelligence. It focuses on enabling computers to understand and process human language. Topic modeling is a technique used in natural language processing to discover the underlying topics in a collection of documents. Text summarization is another important task in NLP. It involves condensing a longer text into a shorter version while retaining the most important information. There are two main approaches to text summarization: extractive and abstractive. Extractive summarization selects the most important sentences from the original text, while abstractive summarization generates new sentences that capture the meaning of the original text."""

summary = summarize_text(sample_text)

for sentence in summary:
    print(sentence)