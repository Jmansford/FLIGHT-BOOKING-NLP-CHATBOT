import random

# Response dictionary for variations
responses = {
    "greeting": [
        "Hello {name}, how can I assist you today?",
        "Hi {name}! What can I do for you today?",
        "Hey {name}, how can I help you?",
        "Greetings {name}, what do you need today?"
    ],
    "new_user_greeting": [
        "Hello {name}! Welcome to the Travel Booking Assistant. How can I assist you today?",
        "Hi {name}, glad to see you here! I can help with booking flights or managing your travel plans. What do you need?",
        "Welcome, {name}! I’m here to assist with all your travel needs. How can I help you today?",
        "Greetings, {name}! Whether it’s booking flights or travel planning, I’ve got you covered. How may I assist?",
        "Hey {name}, welcome aboard! I can help book flights or manage your travel plans. Let’s get started!",
        "Hi {name}! Need help with a flight booking or managing your travel? I'm here to assist!"
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
        "I'm good, but I'm here to help you! How are you?",
        "I'm doing great, thanks for asking! How can I assist you? How are you?",
        "I don't have feelings, but I'm ready to help you! How are you?",
        "I'm here and ready to assist you! How are you?"
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
    "origin_prompt": [
        "Could you let me know where you're flying from? Available options are: {available_origins}.",
        "Great! From which city would you like to start your journey? Choices are: {available_origins}.",
        "Alright, please tell me your origin city. You can choose from: {available_origins}."
    ],
    "destination_prompt": [
        "Where are you headed? Available options are: {available_destinations}.",
        "Could you share your destination? Here’s what we have: {available_destinations}.",
        "Please let me know your destination from these options: {available_destinations}."
    ],
    "departure_date_prompt": [
        "When would you like to depart? (Format: DD-MM-YYYY or words like 'tomorrow')",
        "What is your desired departure date? You can also mention terms like 'next week'.",
        "Could you provide the departure date? Feel free to use relative terms like 'tomorrow'."
    ],
    "travel_class_prompt": [
        "What class would you like to travel in? (economy, business, first)",
        "Which travel class do you prefer: economy, business, or first?",
        "Could you specify the travel class: economy, business, or first?"
    ],
    "confirmation_prompt": [
        "Would you like to proceed with this booking?",
        "Is this flight good for you to confirm the booking?",
        "Should I go ahead and book this flight for you?"
    ],
    "booking_confirmed": [
        "Your booking is confirmed! Safe travels!",
        "All set! Your flight has been booked.",
        "Booking complete. Wishing you a great journey!"
    ],
    "booking_confirmed_details": [
        "Your flight {flight_number} from {origin} to {destination} on {departure_date} in {travel_class} class is booked!",
        "You're all set! Flight {flight_number} from {origin} to {destination} has been booked for {departure_date} in {travel_class} class.",
        "Confirmation received! Flight {flight_number} from {origin} to {destination} on {departure_date} ({travel_class}) is booked!"
    ],
    "no_flights_found": [
        "I couldn't find any flights matching your criteria. Looking for alternatives...",
        "No flights were found with the provided details. Checking what else is available...",
        "I'm sorry, but I couldn’t locate any flights with the current details. Let me find other options..."
    ],
    "positive_feelings": [
        "That's great to hear, {name}! How can I make your day even better?",
        "I'm glad you're feeling good, {name}! Let me know how I can assist.",
        "Wonderful! Keep up the positivity, {name}! How can I help today?",
        "Awesome, {name}! I'm here to keep that good mood going. What do you need?"
    ],
    "negative_feelings": [
        "I'm sorry to hear that, {name}. How can I help make things a bit better?",
        "Oh no, {name}, I hope things improve for you soon. Is there something I can assist with?",
        "That doesn't sound great, {name}. Let me know if there's anything I can do for you.",
        "I'm here for you, {name}. Let me know how I can help make your day a little easier."
    ],
    "neutral_feelings": [
    "Thanks for sharing, {name}. Let me know how I can help.",
    "I hear you, {name}. How can I assist you today?",
    "Got it, {name}. Let me know if there's anything I can do.",
    "Thanks for letting me know, {name}. What can I help you with?",
    "I appreciate you sharing, {name}. How can I assist you?",
    "Alright, {name}. Let me know what you need help with.",
    "Thank you for telling me, {name}. How can I support you today?"
]
}

# Get a random response based on the intent and optional parameters
def get_response(intent, name=None, **kwargs):
    response = random.choice(responses[intent])
    if name:
        response = response.format(name=name)
    if kwargs:
        response = response.format(**kwargs)
    return f"Bot: {response}"
