from Classes.responses import get_response
from Classes.intent_matching import match_intent
from Classes.booking_flow import booking_flow, display_bookings
from Classes.database_setup import setup_database
from Classes.sentiment_analysis import classify_sentiment
from Classes.greeting import welcome_user

# Identity management

# Chatbot Main Loop
def chatbot():
    setup_database()
    name = None
    while True:
        if(name == None):
            name = welcome_user()

        user_input = input(f"{name}: ")
        intent = match_intent(user_input)
        
        if intent == "greeting":
            print(get_response("greeting", name=name))
        elif intent == "booking":
            booking_flow(name, user_input)
        elif intent == "thanks":
            print(get_response("thanks", name=name))
        elif intent == "farewell":
            print(get_response("farewell", name=name))
            break
        elif intent == "how_are_you":
            print(get_response("how_are_you"))
            user_response = input(f"{name}: ")
            classify_sentiment(user_response, name)
        elif intent == "capabilities":
            print(get_response("capabilities"))
        elif intent == "user_name":
            print(get_response("user_name", name=name))
        elif intent == "edit_view_booking":
            display_bookings(name)
        else:
            print("Bot: I'm not sure I understand. Could you please clarify?")

# Run the chatbot
if __name__ == "__main__":
    chatbot()
