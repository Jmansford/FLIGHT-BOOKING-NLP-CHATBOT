import sqlite3
from Classes.responses import get_response
from datetime import datetime, timedelta
import re
from nltk import pos_tag, word_tokenize
from nltk.metrics import edit_distance

# List of available origins and destinations
ORIGINS = ["London", "Toronto", "Sydney", "Dubai", "Frankfurt", "Mumbai"]
DESTINATIONS = ["Paris", "New York", "Berlin", "Singapore", "Tokyo", "Amsterdam"]

# Connect to SQLite database
def connect_to_db():
    return sqlite3.connect('Resources/flight_booking.db')

# Function to find the best matching location from a list based on user input
def best_match_location(user_input, location_list, max_distance=3):
    tokens = word_tokenize(user_input)
    filtered_tokens = [token.capitalize() for token in tokens if token.isalpha()]
    location = ' '.join(filtered_tokens)
    best_match = min(location_list, key=lambda x: edit_distance(location, x))
    return best_match if edit_distance(location, best_match) <= max_distance else None

# Parse booking details from user input with enhanced origin/destination handling
def parse_booking_details(user_input, booking_details):
    # Ensure all keys are initialized
    details = {
        "origin": booking_details.get("origin"),
        "destination": booking_details.get("destination"),
        "departure_date": booking_details.get("departure_date"),
        "return_date": booking_details.get("return_date"),
        "travel_class": booking_details.get("travel_class"),
        "is_flexible": booking_details.get("is_flexible", False)
    }

    # Tokenize and POS tag user input
    tokens = word_tokenize(user_input)
    pos_tags = pos_tag(tokens)

    # Determine flexibility from input
    details["is_flexible"] = "flexible" in user_input.lower() or details["is_flexible"]

    # Extract travel class
    if not details["travel_class"]:
        if "economy" in user_input.lower():
            details["travel_class"] = "economy"
        elif "business" in user_input.lower():
            details["travel_class"] = "business"
        elif "first" in user_input.lower():
            details["travel_class"] = "first"

    # Handle "from" and "to" as indicators for origin and destination
    if "from" in tokens:
        from_index = tokens.index("from") + 1
        if from_index < len(tokens):
            potential_origin = tokens[from_index]
            details["origin"] = best_match_location(potential_origin, ORIGINS) or details["origin"]

    if "to" in tokens:
        to_index = tokens.index("to") + 1
        if to_index < len(tokens):
            potential_destination = tokens[to_index]
            details["destination"] = best_match_location(potential_destination, DESTINATIONS) or details["destination"]

    # Use general POS tagging as backup if "from" and "to" are not used
    if not details["origin"] or not details["destination"]:
        for i, (word, tag) in enumerate(pos_tags):
            potential_location = word.capitalize()
            if tag == 'NNP' and not details["origin"] and potential_location in ORIGINS:
                details["origin"] = potential_location
            elif tag == 'NNP' and not details["destination"] and potential_location in DESTINATIONS:
                details["destination"] = potential_location

    # Extract departure date (e.g., "tomorrow" or "DD-MM-YYYY")
    if not details["departure_date"]:
        details["departure_date"] = parse_date(user_input)

    return details

# Helper function to parse dates from user input based on keywords
def parse_date(input_text):
    input_text = input_text.lower()
    reference_date = datetime.now()

    try:
        if "tomorrow" in input_text:
            return reference_date + timedelta(days=1)
        elif "next week" in input_text:
            return reference_date + timedelta(weeks=1)
        elif "in " in input_text and " days" in input_text:
            days = int(re.search(r'in (\d+) days', input_text).group(1))
            return reference_date + timedelta(days=days)
        else:
            return datetime.strptime(input_text, '%d-%m-%Y')
    except (ValueError, AttributeError):
        return None

# Function to find flights in the database based on search criteria
def find_flights(conn, origin, destination, departure_date, travel_class):
    cursor = conn.cursor()
    query = '''
    SELECT flight_number, origin, destination, departure_date, return_date, travel_class, price
    FROM flights
    WHERE origin = ? AND destination = ? AND departure_date = ? AND travel_class = ?
    '''
    params = [origin, destination, departure_date.strftime('%d-%m-%Y'), travel_class]
    cursor.execute(query, params)
    flights = cursor.fetchall()

    if not flights:
        print("Bot: I couldn't find an available flight for these dates and locations. Searching for the next available flight...")
        query = '''
        SELECT flight_number, origin, destination, departure_date, return_date, travel_class, price
        FROM flights
        WHERE origin = ? AND destination = ? AND departure_date > ?
        ORDER BY departure_date ASC
        LIMIT 1
        '''
        cursor.execute(query, [origin, destination, departure_date.strftime('%d-%m-%Y')])
        flights = cursor.fetchall()

    return flights

# Helper function to prompt user for missing details
def prompt_for_missing_detail(detail_name, prompt_text, validation_func=None):
    while True:
        response = input(f"Bot: {prompt_text}: ")
        if validation_func:
            valid_response = validation_func(response)
            if valid_response:
                return valid_response
        else:
            return response
        print("Bot: Please enter a valid input.")

# Main booking flow with detail prompting
def booking_flow(name, user_input):
    # Initialize or update booking details from user input
    booking_details = parse_booking_details(user_input, {})
    print(f"Parsed booking details: {booking_details}")

    # Prompt user for missing details
    if not booking_details["origin"]:
        booking_details["origin"] = prompt_for_missing_detail(
            "origin", f"Please provide the origin (Available: {', '.join(ORIGINS)})", 
            lambda x: best_match_location(x, ORIGINS)
        )

    if not booking_details["destination"]:
        booking_details["destination"] = prompt_for_missing_detail(
            "destination", f"Please provide the destination (Available: {', '.join(DESTINATIONS)})", 
            lambda x: best_match_location(x, DESTINATIONS)
        )

    if not booking_details["departure_date"]:
        booking_details["departure_date"] = prompt_for_missing_detail(
            "departure_date", "When would you like to depart? (Format: DD-MM-YYYY or relative terms like 'tomorrow')", 
            lambda x: parse_date(x)
        )

    if not booking_details["travel_class"]:
        booking_details["travel_class"] = prompt_for_missing_detail(
            "travel_class", "What class would you like to travel in? (economy, business, first)", 
            lambda x: x.lower() if x.lower() in ["economy", "business", "first"] else None
        )

    # Query Database for Available Flights
    conn = connect_to_db()
    flights = find_flights(
        conn, 
        booking_details["origin"], 
        booking_details["destination"], 
        booking_details["departure_date"], 
        booking_details["travel_class"]
    )

    # Handle flight selection based on availability
    if flights:
        if len(flights) == 1:
            flight = flights[0]
            print(f"Bot: I found one flight: \n\nFlight {flight[0]} from {flight[1]} to {flight[2]}, "
                  f"Departure: {flight[3]}, Return: {flight[4] if flight[4] else 'One-way'}, "
                  f"Class: {flight[5]}, Price: ${flight[6]}\n")
            confirm = input("Would you like to book this flight? (yes/no): ").lower()
            if confirm in ["yes", "y"]:
                booking_details["flight_number"] = flight[0]
                print(get_response("booking_confirmed"))
            else:
                print("Bot: No problem, let me know if you need anything else.")
        else:
            print("Bot: Here are the available flights:")
            for i, flight in enumerate(flights, start=1):
                print(f"{i}. Flight {flight[0]} from {flight[1]} to {flight[2]}, "
                      f"Departure: {flight[3]}, Return: {flight[4] if flight[4] else 'One-way'}, "
                      f"Class: {flight[5]}, Price: ${flight[6]}")
            selected_flight_index = int(input("Please enter the number of the flight you'd like to book: ")) - 1
            selected_flight = flights[selected_flight_index]
            booking_details["flight_number"] = selected_flight[0]
            print(get_response("booking_confirmed_details", flight_number=selected_flight[0], origin=selected_flight[1],
                               destination=selected_flight[2], departure_date=selected_flight[3],
                               travel_class=selected_flight[5]))
    else:
        print("Bot: I couldn't find any flights matching your criteria.")

    conn.close()
