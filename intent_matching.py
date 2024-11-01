import json
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from preprocessing import preprocess_input

# Load intents from JSON file
def load_intents(json_file='intents.json'):
    # Opens the JSON file containing all intents and associated phrases
    with open(json_file, 'r') as f:
        intents_data = json.load(f)
    # Extracts only the "intents" section to get phrases and their respective intent categories
    intents = intents_data["intents"]
    return intents

# Build the term-document matrix and intent labels
def build_intent_corpus(intents):
    # corpus will hold all phrases as a list, each representing a sample for an intent
    # labels will hold corresponding intent labels for each phrase in corpus
    corpus = []
    labels = []
    for intent, phrases in intents.items():
        # Extend corpus with all phrases under the current intent
        corpus.extend(phrases)
        # Append the intent label for each phrase in corpus
        labels.extend([intent] * len(phrases))
    return corpus, labels

# Load intents and build corpus from the JSON data
intents = load_intents()
corpus, labels = build_intent_corpus(intents)

# Initialise vectoriser and transformer with the corpus (using unigrams, bigrams and trigrams)
vectorizer = CountVectorizer(ngram_range=(1, 3), stop_words='english')
# Transform the text data into a term-document matrix
X_counts = vectorizer.fit_transform(corpus)

# TF-IDF transformation on the feature counts to adjust importance of terms
tfidf_transformer = TfidfTransformer()
X_tfidf = tfidf_transformer.fit_transform(X_counts)

# Intent matching function
def match_intent(user_input):
    # Preprocess and vectorise user input 
    tokens = preprocess_input(user_input)
    # Vectorise the processed input using the same TF-IDF transformation the corpus
    # 'user_input_tfidf' is now in the same vector space as our corpus phrases, ready for comparison
    user_input_tfidf = tfidf_transformer.transform(vectorizer.transform([" ".join(tokens)]))
    
    # Calculate cosine similarity between the vectorized user input and each intent phrase
    similarities = cosine_similarity(user_input_tfidf, X_tfidf).flatten()
    # Find the index of the phrase in corpus with the highest similarity to the user input
    best_match_idx = similarities.argmax()
    
    # Apply threshold to determine if a match is confident enough
    # If the highest similarity score is below the threshold, return "unknown" as intent is unclear
    if similarities[best_match_idx] < 0.3:  # Adjustable threshold
        return "unknown"
    
    # Return the intent label corresponding to the best match
    return labels[best_match_idx]
