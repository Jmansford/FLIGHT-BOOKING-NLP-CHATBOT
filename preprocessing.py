# preprocessing.py

import re
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('punkt')

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
