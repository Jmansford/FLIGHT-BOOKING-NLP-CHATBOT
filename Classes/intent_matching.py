import json, re, nltk
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import wordnet
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer

nltk.download('wordnet', quiet = True)
nltk.download('averaged_perceptron_tagger', quiet = True)
nltk.download('punkt', quiet = True)


lemmatizer = WordNetLemmatizer()

# Preprocess user input
def preprocess_input(user_input):
    # Convert to lowercase
    user_input = user_input.lower()
    # Remove punctuation
    user_input = re.sub(r"['\.,!?]", "", user_input)
    # Remove newline characters
    user_input = user_input.replace("\n", " ")
    # Tokenize input
    tokens = word_tokenize(user_input)
    # POS tagging
    pos_tags = nltk.pos_tag(tokens)

    # Function to convert POS tag to a format that WordNetLemmatizer can understand
    def get_wordnet_pos(tag):
        if tag.startswith('J'):
            return wordnet.ADJ
        elif tag.startswith('V'):
            return wordnet.VERB
        elif tag.startswith('N'):
            return wordnet.NOUN
        elif tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN

    # Lemmatize tokens with POS tags
    tokens = [lemmatizer.lemmatize(token, get_wordnet_pos(tag)) for token, tag in pos_tags]
    return tokens

# Load intents from JSON file
def load_intents(json_file='Resources/intents.json'):
    with open(json_file, 'r') as f:
        intents_data = json.load(f)
    intents = intents_data["intents"]
    return intents

# Build the term-document matrix and intent labels
def build_intent_corpus(intents):
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

# Function to get synonyms for a given word
def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().replace("_", " "))
    return synonyms

# Expand input with synonyms
def expand_with_synonyms(tokens):
    expanded_tokens = set(tokens)  # Start with original tokens
    for token in tokens:
        expanded_tokens.update(get_synonyms(token))  # Add synonyms
    return list(expanded_tokens)

# Intent matching function with synonym-based fallback
def match_intent(user_input):
    # Preprocess and vectorise user input
    tokens = preprocess_input(user_input)
    user_input_tfidf = tfidf_transformer.transform(vectorizer.transform([" ".join(tokens)]))
    
    # Calculate cosine similarity between the vectorized user input and each intent phrase
    similarities = cosine_similarity(user_input_tfidf, X_tfidf).flatten()
    best_match_idx = similarities.argmax()
    
    # Apply threshold to determine if a match is confident enough
    if similarities[best_match_idx] >= 0.5:
        return labels[best_match_idx]

    # Fallback: try expanding with synonyms if no confident match is found
    expanded_tokens = expand_with_synonyms(tokens)
    expanded_user_input = " ".join(expanded_tokens)
    expanded_user_input_tfidf = tfidf_transformer.transform(vectorizer.transform([expanded_user_input]))

    # Recalculate similarity with expanded input and apply a lower threshold
    expanded_similarities = cosine_similarity(expanded_user_input_tfidf, X_tfidf).flatten()
    expanded_best_match_idx = expanded_similarities.argmax()

    # Use a lower threshold for synonym-based fallback matching
    if expanded_similarities[expanded_best_match_idx] >= 0.3:
        return labels[expanded_best_match_idx]
    
    return "unknown"
