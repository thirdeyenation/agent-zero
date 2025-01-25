from gensim import corpora
from gensim.models import LdaModel
from gensim.utils import simple_preprocess


def extract_topics(text, num_topics=2):
    processed_text = [simple_preprocess(text)]
    dictionary = corpora.Dictionary(processed_text)
    corpus = [dictionary.doc2bow(text) for text in processed_text]
    lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15)
    topics = lda_model.print_topics()
    return topics

sample_text = """This is a sample document about natural language processing. Natural language processing is a subfield of artificial intelligence. It focuses on enabling computers to understand and process human language. Topic modeling is a technique used in natural language processing to discover the underlying topics in a collection of documents."""

topics = extract_topics(sample_text)

for topic in topics:
    print(topic)