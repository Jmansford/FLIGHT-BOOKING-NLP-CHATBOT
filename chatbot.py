from Classes.responses import get_response
from Classes.intent_matching import match_intent, find_answer
from Classes.booking_flow import booking_flow, display_and_cancel_booking
from Classes.database_setup import setup_database
from Classes.sentiment_analysis import classify_sentiment
from Classes.greeting import welcome_user

# Chatbot Main Loop
def chatbot():
    """
    Main function for running the chatbot application.
    This function manages the chatbot's setup
    """
    # Initial database setup to ensure all prerequisites are in place.
    setup_database()

    # Initialise the user's name as None, to prompt a greeting upon first interaction.
    name = None

    # Begin infinite loop to handle continuous user interaction.
    while True:
        # If user's name is not yet set, prompt them with a welcome message.
        if name is None:
            name = welcome_user()

        # Capture user input for processing.
        user_input = input(f"{name}: ")

        answer = find_answer(user_input)
        if answer:
            print(f"Bot: {answer}")
            continue

        # Determine the user's intent based on the input.
        intent = match_intent(user_input)

        # Respond based on the matched intent.
        if intent == "greeting":
            # Provide a greeting response, incorporating the user's name.
            print(get_response("greeting", name=name))
        elif intent == "booking":
            # Handle the booking flow for the user.
            booking_flow(name, user_input)
        elif intent == "thanks":
            # Respond to user expressions of gratitude.
            print(get_response("thanks", name=name))
        elif intent == "farewell":
            # Respond to 'bye' related inputs and exit the chatbot loop.
            print(get_response("farewell", name=name))
            break
        elif intent == "how_are_you":
            # Respond to inquiries about the chatbot's state and analyse sentiment.
            print(get_response("how_are_you"))
            user_response = input(f"{name}: ")
            classify_sentiment(user_response, name)
        elif intent == "capabilities":
            # Inform the user about the chatbot's capabilities.
            print(get_response("capabilities"))
        elif intent == "user_name":
            # Remind the user of their recorded name.
            print(get_response("user_name", name=name))
        elif intent == "edit_view_booking":
            # Allow the user to edit or cancel an existing booking.
            display_and_cancel_booking(name)
        else:
            # Handle unrecognised inputs by prompting clarification.
            print("Bot: I'm not sure I understand. Could you please clarify?")

# Run the chatbot if the script is executed directly.
if __name__ == "__main__":
    chatbot()
