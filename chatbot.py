from Classes.responses import get_response
from Classes.intent_matching import match_intent
from Classes.booking_flow import booking_flow
from Classes.database_setup import setup_database  

# Identity management
def get_user_name():
    print("Bot: Hi, let's get started with your name: ")
    return input("Enter your name: ")

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
        elif intent == "capabilities":
            print(get_response("capabilities"))
        elif intent == "user_name":
            print(get_response("user_name", name=name))
        else:
            print("Bot: I'm not sure I understand. Could you please clarify?")

# Run the chatbot
if __name__ == "__main__":
    chatbot()
