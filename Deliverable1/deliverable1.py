import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load and preprocess the QA dataset
nltk.download('punkt')
nltk.download('stopwords')

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

# Small talk and interaction responses
def handle_small_talk(user_input):
    global user_name
    
    # Small talk and intent detection
    if user_input.lower() in ['hi', 'hello']:
        return "Hello! What is your name?"
    
    elif 'my name is' in user_input.lower() or 'call me' in user_input.lower():
        user_name = user_input.split()[-1]
        return f"Nice to meet you, {user_name}!"
    
    elif user_input.lower() == 'what is my name' and user_name:
        return f"Your name is {user_name}."
    
    elif user_input.lower() == 'what is my name' and not user_name:
        return "I don't know your name yet. Please tell me by saying 'My name is...'"
    
    elif user_input.lower() == 'how are you':
        return "I'm just a computer program, but I'm functioning as expected! How about you?"
    
    elif user_input.lower() == 'what can you do':
        return "I can remember your name, have simple conversations, and answer specific questions like 'What are stocks and bonds?'"
    
    elif user_input.lower() in ['exit', 'bye', 'quit']:
        return "Goodbye! Have a great day!"
    
    return None  # Return None if no small talk match is found

# Greeting and interaction loop
def chatbot():
    global user_name
    print("Hello! I am your friendly chatbot. How can I assist you today?")
    
    while True:
        user_input = input("You: ").strip()
        
        # First, try to find an answer from the QA dataset
        answer = find_answer(user_input)
        
        if answer:
            # If an answer was found in the QA dataset, use it
            print(f"Chatbot: {answer}")
        else:
            # If no answer was found in the QA dataset, check for small talk
            small_talk_response = handle_small_talk(user_input)
            
            if small_talk_response:
                print(f"Chatbot: {small_talk_response}")
                
                # Exit if the user said goodbye
                if user_input.lower() in ['exit', 'bye', 'quit']:
                    break
            else:
                # Fallback response if no suitable response is found
                print("Chatbot: I'm not sure how to answer that. You can ask me about stocks, bonds, or try a different question.")

# Run the chatbot
if __name__ == "__main__":
    chatbot()
