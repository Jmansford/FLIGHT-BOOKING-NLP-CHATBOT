import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk import ngrams
import re

lemmatizer = WordNetLemmatizer()

nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('punkt')

# Load the QA dataset
qa_data = pd.read_csv('Deliverable1/qadataset.csv')

# Initialize stop words
stop_words = set(stopwords.words('english'))

# Preprocess questions and answers from the dataset
def preprocess(text):
    tokens = word_tokenize(text.lower())
    filtered_tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
    return ' '.join(filtered_tokens)

qa_data['Processed_Question'] = qa_data['Question'].apply(preprocess)

# Initialize TF-IDF Vectorizer and fit it on the questions
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(qa_data['Processed_Question'])

# Function to find the most similar answer based on cosine similarity
def find_answer(question):
    # Preprocess the user question
    processed_question = preprocess(question)
    user_tfidf = vectorizer.transform([processed_question])
    
    # Calculate cosine similarities between the user question and all dataset questions
    similarities = cosine_similarity(user_tfidf, tfidf_matrix)
    
    # Find the index of the most similar question
    max_similarity_index = similarities.argmax()
    max_similarity_score = similarities[0, max_similarity_index]
    
    # Set a similarity threshold to ensure relevance
    if max_similarity_score > 0.6:  # Alterable threshold
        return qa_data.iloc[max_similarity_index]['Answer']
    else:
        return None  # Return None if no relevant answer is found

# Variables to store user's name
user_name = None

# Function to preprocess user input
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

# Function to match intent
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

# Greeting and interaction loop
def chatbot():
    global user_name
    print("Hello! Please start by telling me your name: ")
    user_name = input("You: ").strip()
    


    while True:
        user_input = input((f"{user_name}: ")).strip()
        
        # First, try to find an answer from the QA dataset
        answer = find_answer(user_input)
        
        if answer:
            # If an answer was found in the QA dataset, use it
            print(f"Chatbot: {answer}")
        else:
            # If no answer was found in the QA dataset, use match_intent
            intent = match_intent(user_input)
            
            if intent == "greeting":
                response = "Hello! What is your name?"
            
            elif intent == "user_name":
                response = f"Your name is {user_name}." if user_name else "I don't know your name yet. Please tell me by saying 'My name is...'"
            
            elif intent == "how_are_you":
                response = "I'm just a computer program, but I'm functioning as expected! How about you?"
            
            elif intent == "capabilities":
                response = "I can remember your name, have simple conversations, and answer specific questions like 'What are stocks and bonds?'"
            
            elif intent == "thanks":
                response = "You're welcome!"
            
            elif intent == "farewell":
                print("Chatbot: Goodbye! Have a great day!")
                break
            
            else:
                response = "I'm not sure how to answer that. You can ask me about stocks, bonds, or try a different question."

            print(f"Chatbot: {response}")

# Run the chatbot
if __name__ == "__main__":
    chatbot()
