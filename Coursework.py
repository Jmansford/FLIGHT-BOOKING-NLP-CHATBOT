import random
import re
from nltk import word_tokenize, ngrams
from nltk.corpus import stopwords
from datetime import datetime, timedelta

# Download stopwords from nltk if not already available
import nltk
nltk.download('stopwords')
nltk.download('punkt')

# Identity management
def get_user_name():
    print("Bot: Hi, let's get started with your name: ")
    name = input()
    print(f"Bot: Nice to meet you, {name}!")
    return name

# Pre-processing user input
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

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

    # Create bigrams and trigrams from tokens
    bigrams = list(ngrams(tokens, 2))
    trigrams = list(ngrams(tokens, 3))

    # Convert bigrams and trigrams to sets of strings for easier comparison
    bigram_strings = {" ".join(bigram) for bigram in bigrams}
    trigram_strings = {" ".join(trigram) for trigram in trigrams}

    # Define synonym expansion dictionary
    synonym_dict = {
        "book": ["reserve", "schedule"],
        "flight": ["ticket", "air travel"],
        "travel": ["journey", "trip"],
        "hello": ["hi", "hey", "greetings"],
        "goodbye": ["bye", "farewell", "see you"]
    }

    # Expand tokens with synonyms
    expanded_tokens = set(tokens)
    for token in tokens:
        if token in synonym_dict:
            expanded_tokens.update(synonym_dict[token])

    # Check for intents based on tokens, bigrams, and trigrams
    if set(tokens).intersection({'book', 'flight', 'travel', 'reserve', 'ticket', 'fly'}) or bigram_strings.intersection({'book flight', 'reserve ticket'}) or trigram_strings.intersection({'i want to book', 'can i reserve'}):
        return "booking"
    elif set(expanded_tokens).intersection({'hello', 'hi', 'hey', 'greetings', 'howdy'}) or bigram_strings.intersection({'hi there', 'hello bot'}):
        return "greeting"
    elif set(expanded_tokens).intersection({'thank', 'thanks', 'appreciate'}) or bigram_strings.intersection({'thank you', 'much appreciated'}):
        return "thanks"
    elif set(expanded_tokens).intersection({'bye', 'goodbye', 'see', 'later', 'quit', 'exit'}) or bigram_strings.intersection({'see you', 'goodbye bot'}) or trigram_strings.intersection({'talk to you later', 'see you soon'}):
        return "farewell"
    elif bigram_strings.intersection({'how are', 'whats up'}) or trigram_strings.intersection({'how is it', 'how do you'}):
        return "how_are_you"
    elif bigram_strings.intersection({'what can', 'help me'}) or trigram_strings.intersection({'what can you', 'how can you'}):
        return "capabilities"
    elif set(tokens).intersection({'what', 'is', 'my', 'name', 'who', 'am', 'i'}) or bigram_strings.intersection({'my name', 'who am'}) or trigram_strings.intersection({'what is my', 'do you know my'}):
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
            print(random.choice([f"Bot: Got it, you're flying from {booking_details['origin']}.", f"Bot: Okay, I have your origin as {booking_details['origin']}.", f"Bot: Noted, departing from {booking_details['origin']}."]))
        else:
            print("Bot: I couldn't understand the origin. Please try again.")
    
    # Step 2: Get Destination
    while not booking_details["destination"]:
        print("Bot: Please provide the destination")
        user_input = input(f"{name}: ")
        location = extract_location(user_input)
        if location:
            booking_details["destination"] = location
            print(random.choice([f"Bot: Great, you're flying to {booking_details['destination']}.", f"Bot: Destination set to {booking_details['destination']}.", f"Bot: Got it, flying to {booking_details['destination']}."]))
        else:
            print("Bot: I couldn't understand the destination. Please try again.")
    
    # Step 3: Get Departure Date
    while not booking_details["departure_date"]:
        print("Bot: When would you like to depart?")
        user_input = input(f"{name}: ")
        departure_date_obj = parse_date(user_input)
        if departure_date_obj:
            booking_details["departure_date"] = departure_date_obj
            print(random.choice([f"Bot: Your departure date is set to {booking_details['departure_date'].strftime('%d-%m-%Y')}.", f"Bot: Departure date noted as {booking_details['departure_date'].strftime('%d-%m-%Y')}.", f"Bot: Okay, leaving on {booking_details['departure_date'].strftime('%d-%m-%Y')}."]))
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
                print(random.choice([f"Bot: Return date set to {booking_details['return_date'].strftime('%d-%m-%Y')}.", f"Bot: Got it, returning on {booking_details['return_date'].strftime('%d-%m-%Y')}.", f"Bot: Return date noted as {booking_details['return_date'].strftime('%d-%m-%Y')}."]))
            else:
                print("Bot: That doesn't seem like a valid date. Please try again or say 'one-way'.")
    
    # Step 5: Get Travel Class
    while not booking_details["travel_class"]:
        print("Bot: What class would you like to travel in? (economy, business, first): ")
        user_input = input(f"{name}: ")
        travel_class = user_input.lower()
        if travel_class in ['economy', 'business', 'first']:
            booking_details["travel_class"] = travel_class
            print(random.choice([f"Bot: Travel class set to {booking_details['travel_class']}.", f"Bot: Noted, {booking_details['travel_class']} class.", f"Bot: {booking_details['travel_class'].capitalize()} class selected. Let me see what's available."]))
        else:
            print("Bot: Please choose a valid class (economy, business, first).")
    
    # Once all booking details are collected
    print(random.choice([
        f"Bot: Let me check available flights from {booking_details['origin']} to {booking_details['destination']} on {booking_details['departure_date'].strftime('%d-%m-%Y')} in {booking_details['travel_class']} class.",
        f"Bot: Checking flights from {booking_details['origin']} to {booking_details['destination']} on {booking_details['departure_date'].strftime('%d-%m-%Y')} in {booking_details['travel_class']} class.",
        f"Bot: Let me find flights for you from {booking_details['origin']} to {booking_details['destination']} on {booking_details['departure_date'].strftime('%d-%m-%Y')} in {booking_details['travel_class']} class."
    ]))
    print("Bot: I found a flight for you, would you like to confirm the booking?")
    confirm = input(f"{name}: ")
    if confirm.lower() in ['yes', 'y']:
        print(random.choice(["Bot: Your flight has been booked successfully!", "Bot: All done! Your flight is booked.", "Bot: Great! Your flight is confirmed and booked."]))
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
            print(random.choice([f"Bot: Hello {name}, how can I assist you today?", f"Bot: Hi {name}! What can I do for you today?", f"Bot: Hey {name}, how can I help you?", f"Bot: Greetings {name}, what do you need today?"]))
        elif intent == "booking":
            booking_flow(name)
        elif intent == "thanks":
            print(random.choice(["Bot: You're welcome! Happy to help.", "Bot: No problem at all!", "Bot: Glad I could assist!", "Bot: Anytime, {name}!"]))
        elif intent == "farewell":
            print(random.choice([f"Bot: Goodbye {name}, have a great day!", f"Bot: Bye {name}, take care!", f"Bot: See you later, {name}!", f"Bot: Farewell, {name}! Stay safe."]))
            break
        elif intent == "how_are_you":
            print(random.choice(["Bot: I'm just a bot, but I'm here to help you!", "Bot: I'm doing great, thanks for asking! How can I assist you?", "Bot: I don't have feelings, but I'm ready to help you!", "Bot: I'm here and ready to assist you!"]))
        elif intent == "capabilities":
            print(random.choice(["Bot: I can help you book a flight, tell you your name, and answer simple questions.", "Bot: I can assist with booking flights, reminding you of your name, and answering basic questions.", "Bot: I can book flights, tell you your name, or answer simple queries.", "Bot: Booking flights, answering questions, and keeping track of your name is what I do best!"]))
        elif intent == "user_name":
            print(random.choice([f"Bot: Your name is {name}.", f"Bot: You told me your name is {name}.", f"Bot: If I remember correctly, your name is {name}.", f"Bot: You're {name}, right?"]))
        else:
            print("Bot: I'm not sure I understand. Could you please clarify?")

# Run the chatbot
if __name__ == "__main__":
    chatbot()
