# intent_matching.py

from nltk import ngrams
from nltk.corpus import wordnet
from preprocessing import preprocess_input

# Intent Matching with N-Grams and Query Expansion
def match_intent(user_input):
    tokens = preprocess_input(user_input)

    # Match based on lemmatized tokens for common phrases
    if 'how' in tokens and 'be' in tokens and 'you' in tokens:
        return 'how_are_you'

    # Create bigrams and trigrams from tokens
    bigrams = list(ngrams(tokens, 2))
    trigrams = list(ngrams(tokens, 3))

    # Convert bigrams and trigrams to sets of strings for easier comparison
    bigram_strings = {" ".join(bigram) for bigram in bigrams}
    trigram_strings = {" ".join(trigram) for trigram in trigrams}

    # Define synonym expansion dictionary
    synonym_cache = {}

    def get_synonyms(word):
        if word in synonym_cache:
            return synonym_cache[word]
        synonyms = []
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.append(lemma.name())
        synonyms = list(set(synonyms))
        if word in synonyms:
            synonyms.remove(word)
        synonym_cache[word] = synonyms
        return synonyms

    # Expand tokens with synonyms dynamically using WordNet
    expanded_tokens = set(tokens)
    for token in tokens:
        synonyms = get_synonyms(token)
        if synonyms:
            expanded_tokens.update(synonyms)

    # Check for intents based on tokens, bigrams, and trigrams
    if set(tokens).intersection({'book', 'flight', 'travel', 'reserve', 'ticket', 'fly', 'journey', 'trip'}) or bigram_strings.intersection({'book flight', 'reserve ticket'}) or trigram_strings.intersection({'i want to book', 'can i reserve'}):
        return "booking"
    elif set(expanded_tokens).intersection({'hello', 'hi', 'hey', 'greet', 'howdy'}) or bigram_strings.intersection({'hi there', 'hello bot'}):
        return "greeting"
    elif set(expanded_tokens).intersection({'thank', 'thanks', 'appreciate'}) or bigram_strings.intersection({'thank you', 'much appreciated'}):
        return "thanks"
    elif set(expanded_tokens).intersection({'bye', 'goodbye', 'see', 'later', 'quit', 'exit', 'farewell'}) or bigram_strings.intersection({'see you', 'goodbye bot'}) or trigram_strings.intersection({'talk to you later', 'see you soon'}):
        return "farewell"
    elif bigram_strings.intersection({'what can', 'help me', 'ask help'}) or trigram_strings.intersection({'what can you', 'how can you', 'could you help'}):
        return "capabilities"
    elif set(tokens).intersection({'what', 'be', 'my', 'name', 'who', 'i'}) or bigram_strings.intersection({'my name', 'who be'}) or trigram_strings.intersection({'what is my', 'do you know my'}):
        return "user_name"
    else:
        # Fallback logic using expanded tokens if no direct match is found
        if set(expanded_tokens).intersection({'book', 'flight', 'travel', 'reserve', 'ticket', 'fly', 'schedule', 'journey', 'trip'}):
            return "booking"
        else:
            return "unknown"
