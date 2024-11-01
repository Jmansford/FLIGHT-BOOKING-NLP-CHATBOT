import json
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from preprocessing import preprocess_input

# Load intents from JSON file
def load_intents(json_file='intents.json'):
    with open(json_file, 'r') as f:
        intents_data = json.load(f)
    intents = intents_data["intents"]
    return intents

# Build the term-document matrix and intent labels
def build_intent_corpus(intents):
    # Corpus will hold all preprocessed phrases
    corpus = []
    labels = []
    for intent, phrases in intents.items():
        for phrase in phrases:
            # Preprocess each phrase (including lemmatisation) before adding to corpus
            processed_phrase = " ".join(preprocess_input(phrase))
            corpus.append(processed_phrase)
            labels.append(intent)
    return corpus, labels

# Load intents and build corpus from the JSON data
intents = load_intents()
corpus, labels = build_intent_corpus(intents)

# Initialise vectoriser and transformer with the corpus
vectorizer = CountVectorizer(ngram_range=(1, 3))
X_counts = vectorizer.fit_transform(corpus)

# TF-IDF transformation on the feature counts to adjust importance of terms
tfidf_transformer = TfidfTransformer()
X_tfidf = tfidf_transformer.fit_transform(X_counts)

# Intent matching function
def match_intent(user_input):
    # Preprocess and vectorise user input 
    tokens = preprocess_input(user_input)
    user_input_tfidf = tfidf_transformer.transform(vectorizer.transform([" ".join(tokens)]))
    
    # Calculate cosine similarity between the vectorized user input and each intent phrase
    similarities = cosine_similarity(user_input_tfidf, X_tfidf).flatten()
    best_match_idx = similarities.argmax()
    
    # Apply threshold to determine if a match is confident enough
    if similarities[best_match_idx] < 0.5:  # Adjustable threshold
        return "unknown"
    
    return labels[best_match_idx]
