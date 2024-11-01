import random

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
        "{travel_class} class selected. Let me see what's available."
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
    "booking_confirmed_details": [
        "Flight successfully booked from {origin} to {destination} on {departure_date} in {travel_class} class.",
        "I've booked you a flight from {origin} to {destination} on {departure_date} in {travel_class} class.",
        "All sorted! You're flying from {origin} to {destination} on {departure_date} in {travel_class} class."
    ],
    "booking_confirmed": [
        "Your flight has been booked successfully!",
        "All done! Your flight is booked.",
        "Great! Your flight is confirmed and booked."
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
