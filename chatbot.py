from Classes.responses import get_response
from Classes.intent_matching import match_intent
from Classes.booking_flow import booking_flow
from Classes.database_setup import setup_database
from joblib import load  # For loading the sentiment analysis model
from Classes.sentiment_analysis import classify_sentiment


# Identity management
def get_user_name():
    print("Bot: Hi, let's get started with your name: ")
    return input("Enter your name: ")

# Sentiment analysis function
def classify_sentiment(user_input):
    pipeline = load('sentiment_pipeline.joblib')  # Load the saved model
    sentiment = pipeline.predict([user_input])[0]
    return sentiment

# Chatbot Main Loop
def chatbot():
    # Run the flights database setup once at the beginning
    setup_database()
    
    print("\nBot: Hello! Welcome to the Travel Booking Assistant.")
    name = get_user_name()
    print("Bot: You can ask me to book a flight, say hello, thank me, or say goodbye.")
    while True:
        user_input = input(f"{name}: ")
        intent = match_intent(user_input)
        
        if intent == "greeting":
            print(get_response("greeting", name=name))
        elif intent == "booking":
            # Pass both name and user_input to booking_flow
            booking_flow(name, user_input)
        elif intent == "thanks":
            print(get_response("thanks", name=name))
        elif intent == "farewell":
            print(get_response("farewell", name=name))
            break
        elif intent == "how_are_you":
            print(get_response("how_are_you"))
            user_response = input(f"{name}: ")
            
            # Analyse sentiment of the user's response
            sentiment = classify_sentiment(user_response)
            
            # Respond based on sentiment
            if sentiment == "positive":
                print(get_response("positive_feelings", name=name))
            elif sentiment == "negative":
                print(get_response("negative_feelings", name=name))
            else:
                print(get_response("neutral_feelings", name=name))
        elif intent == "capabilities":
            print(get_response("capabilities"))
        elif intent == "user_name":
            print(get_response("user_name", name=name))
        else:
            print("Bot: I'm not sure I understand. Could you please clarify?")

# Run the chatbot
if __name__ == "__main__":
    chatbot()
