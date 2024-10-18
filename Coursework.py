# Imports
import random
import re
import nltk

from nltk import word_tokenize, ngrams
from nltk.corpus import stopwords
from datetime import datetime, timedelta
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

# Downloads
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('punkt')

# Response dictionary for variations
responses = {
    "origin": [
        "Got it, you're flying from {origin}.",
        "Okay, I have your origin as {origin}.",
        "Noted, departing from {origin}."
    ],
    "destination": [
        "Great, you're flying to {destination}.",
        "Destination set to {destination}.",
        "Got it, flying to {destination}."
    ],
    "departure_date": [
        "Your departure date is set to {departure_date}.",
        "Departure date noted as {departure_date}.",
        "Okay, leaving on {departure_date}."
    ],
    "return_date": [
        "Return date set to {return_date}.",
        "Got it, returning on {return_date}.",
        "Return date noted as {return_date}."
    ],
    "travel_class": [
        "Travel class set to {travel_class}.",
        "Noted, {travel_class} class.",
        "{travel_class.capitalize()} class selected. Let me see what's available."
    ],
    "greeting": [
        "Hello {name}, how can I assist you today?",
        "Hi {name}! What can I do for you today?",
        "Hey {name}, how can I help you?",
        "Greetings {name}, what do you need today?"
    ],
    "thanks": [
        "You're welcome! Happy to help.",
        "No problem at all!",
        "Glad I could assist!",
        "Anytime, {name}!"
    ],
    "farewell": [
        "Goodbye {name}, have a great day!",
        "Bye {name}, take care!",
        "See you later, {name}!",
        "Farewell, {name}! Stay safe."
    ],
    "how_are_you": [
        "I'm good, but I'm here to help you!",
        "I'm doing great, thanks for asking! How can I assist you?",
        "I don't have feelings, but I'm ready to help you!",
        "I'm here and ready to assist you!"
    ],
    "capabilities": [
        "I can help you book a flight, tell you your name, and answer simple questions.",
        "I can assist with booking flights, reminding you of your name, and answering basic questions.",
        "I can book flights, tell you your name, or answer simple queries.",
        "Booking flights, answering questions, and keeping track of your name is what I do best!"
    ],
    "user_name": [
        "Your name is {name}.",
        "You told me your name is {name}.",
        "If I remember correctly, your name is {name}.",
        "You're {name}, right?"
    ],
    "one_way": [
        "You have selected a one-way trip.",
        "Noted, this is a one-way trip.",
        "One-way trip confirmed."
    ],
    "flight_check": [
        "Let me check available flights from {origin} to {destination} on {departure_date} in {travel_class} class.",
        "Checking flights from {origin} to {destination} on {departure_date} in {travel_class} class.",
        "Let me find flights for you from {origin} to {destination} on {departure_date} in {travel_class} class."
    ],
    "booking_confirmed": [
        "Your flight has been booked successfully!",
        "All done! Your flight is booked.",
        "Great! Your flight is confirmed and booked."
    ]
}

# Get a random response based on the intent and optional parameters
# Parameters:
#   intent: str - The intent or scenario for which a response is needed, used to fetch responses from the responses dictionary.
#   name: str (optional) - The user's name, used to personalize the response if applicable.
#   **kwargs: dict (optional) - Additional variables to format into the response, such as origin, destination, or dates.
def get_response(intent, name=None, **kwargs):
    response = random.choice(responses[intent])
    if name:
        response = response.format(name=name)
    if kwargs:
        response = response.format(**kwargs)
    return f"Bot: {response}"

# Identity management
def get_user_name():
    print("Bot: Hi, let's get started with your name: ")
    return input("Enter your name: ")

lemmatizer = WordNetLemmatizer()

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
    elif 'how are you' in user_input or 'how are' in bigram_strings or 'whats up' in bigram_strings or 'how is it' in trigram_strings or 'how do you' in trigram_strings:
        return "how_are_you"
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

# Extract Location Function
def extract_location(user_input):
    tokens = preprocess_input(user_input)
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token not in stop_words and token.isalpha()]

    # Heuristic: Assume the last meaningful word is the location
    if filtered_tokens:
        return filtered_tokens[-1].capitalize()
    
    # Fallback: return the full input as a guess
    return user_input

# Date Parsing Function
def parse_date(input_date, reference_date=None):
    input_date = input_date.lower()
    if not reference_date:
        reference_date = datetime.now()
    if input_date == "tomorrow":
        return reference_date + timedelta(days=1)
    elif "in" in input_date and "days" in input_date:
        try:
            days = int(re.search(r"\d+", input_date).group())
            return reference_date + timedelta(days=days)
        except AttributeError:
            return None
    elif "days later" in input_date:
        try:
            days = int(re.search(r"\d+", input_date).group())
            return reference_date + timedelta(days=days)
        except AttributeError:
            return None
    elif "next week" in input_date or "week later" in input_date:
        return reference_date + timedelta(weeks=1)
    else:
        try:
            return datetime.strptime(input_date, '%d-%m-%Y')
        except ValueError:
            return None

# Booking Flow
def booking_flow(name):
    booking_details = {
        "origin": None,
        "destination": None,
        "departure_date": None,
        "return_date": None,
        "travel_class": None,
    }
    
    print("Bot: Let's get the details for your flight booking.")
    
    # Step 1: Get Origin
    while not booking_details["origin"]:
        print(f"Bot: Please provide the origin: ")
        user_input = input(f"{name}: ")
        location = extract_location(user_input)
        if location:
            booking_details["origin"] = location
            print(get_response("origin", origin=booking_details['origin']))
        else:
            print("Bot: I couldn't understand the origin. Please try again.")
    
    # Step 2: Get Destination
    while not booking_details["destination"]:
        print("Bot: Please provide the destination")
        user_input = input(f"{name}: ")
        location = extract_location(user_input)
        if location:
            booking_details["destination"] = location
            print(get_response("destination", destination=booking_details['destination']))
        else:
            print("Bot: I couldn't understand the destination. Please try again.")
    
    # Step 3: Get Departure Date
    while not booking_details["departure_date"]:
        print("Bot: When would you like to depart?")
        user_input = input(f"{name}: ")
        departure_date_obj = parse_date(user_input)
        if departure_date_obj:
            booking_details["departure_date"] = departure_date_obj
            print(get_response("departure_date", departure_date=booking_details['departure_date'].strftime('%d-%m-%Y')))
        else:
            print("Bot: That doesn't seem like a valid date. Please try again.")
    
    # Step 4: Get Return Date (Optional)
    while booking_details["return_date"] is None:
        print("Bot: Would you like to add a return date? You can say 'one-way' if it's a one-way trip: ")
        user_input = input(f"{name}: ")
        if user_input.lower() == 'one-way':
            booking_details["return_date"] = 'one-way'
            print(random.choice(["Bot: You have selected a one-way trip.", "Bot: Noted, this is a one-way trip.", "Bot: One-way trip confirmed."]))
        else:
            return_date_obj = parse_date(user_input, reference_date=booking_details.get("departure_date"))
            if return_date_obj:
                booking_details["return_date"] = return_date_obj
                print(get_response("return_date", return_date=booking_details['return_date'].strftime('%d-%m-%Y')))
            else:
                print("Bot: That doesn't seem like a valid date. Please try again or say 'one-way'.")
    
    # Step 5: Get Travel Class
    while not booking_details["travel_class"]:
        print("Bot: What class would you like to travel in? (economy, business, first): ")
        user_input = input(f"{name}: ")
        travel_class = user_input.lower()
        if travel_class in ['economy', 'business', 'first']:
            booking_details["travel_class"] = travel_class
            print(get_response("travel_class", travel_class=booking_details['travel_class']))
        else:
            print("Bot: Please choose a valid class (economy, business, first).")
    
    # Once all booking details are collected
    print(get_response("flight_check", origin=booking_details['origin'], destination=booking_details['destination'], departure_date=booking_details['departure_date'].strftime('%d-%m-%Y'), travel_class=booking_details['travel_class']))
    print("Bot: I found a flight for you, would you like to confirm the booking?")
    confirm = input(f"{name}: ")
    if confirm.lower() in ['yes', 'y']:
        print(get_response("booking_confirmed"))
    else:
        print("Bot: No problem, let me know if you need anything else.")

# Chatbot Main Loop
def chatbot():
    print("Bot: Hello! Welcome to the Travel Booking Assistant.")
    name = get_user_name()
    print("Bot: You can ask me to book a flight, say hello, thank me, or say goodbye.")
    while True:
        user_input = input(f"{name}: ")
        intent = match_intent(user_input)
        
        if intent == "greeting":
            print(get_response("greeting", name=name))
        elif intent == "booking":
            booking_flow(name)
        elif intent == "thanks":
            print(get_response("thanks", name=name))
        elif intent == "farewell":
            print(get_response("farewell", name=name))
            break
        elif intent == "how_are_you":
            print(get_response("how_are_you"))
        elif intent == "capabilities":
            print(get_response("capabilities"))
        elif intent == "user_name":
            print(get_response("user_name", name=name))
        else:
            print("Bot: I'm not sure I understand. Could you please clarify?")

# Run the chatbot
if __name__ == "__main__":
    chatbot()
