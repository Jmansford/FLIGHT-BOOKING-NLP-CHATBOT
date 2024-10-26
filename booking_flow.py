# booking_flow.py

from responses import get_response
from datetime import datetime, timedelta
import re

# Extract Location Function (assumes the function is in preprocessing.py)
from preprocessing import preprocess_input
from nltk.corpus import stopwords

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

# Booking Flow Function
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
            print(get_response("one_way"))
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
