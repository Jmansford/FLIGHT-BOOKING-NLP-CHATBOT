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
def best_match_location(user_input, location_list, max_distance=2):
    tokens = word_tokenize(user_input)
    filtered_tokens = [token.capitalize() for token in tokens if token.isalpha()]
    location = ' '.join(filtered_tokens)
    best_match = min(location_list, key=lambda x: edit_distance(location, x))
    return best_match if edit_distance(location, best_match) <= max_distance else None

# Helper function to confirm the best match location with the user
def confirm_location(user_input, location_list, name):
    # Try to find the best match for the user's input
    suggested_location = best_match_location(user_input, location_list)
    # Only ask for confirmation if the suggested location is not an exact match
    if suggested_location and suggested_location.lower() != user_input.lower():
        print(f"Bot: Did you mean '{suggested_location}'? (yes/no)")
        confirm = input(f"{name}: ").strip().lower()
        if confirm in ["yes", "y"]:
            return suggested_location
        else:
            print("Bot: Got it, please try again.")
    # Return the input unchanged if it matches exactly or user did not confirm
    return user_input if user_input.capitalize() in location_list else None


# Parse booking details from user input with enhanced origin/destination handling
def parse_booking_details(user_input, booking_details, name):
    details = {
        "origin": booking_details.get("origin"),
        "destination": booking_details.get("destination"),
        "departure_date": booking_details.get("departure_date"),
        "return_date": booking_details.get("return_date"),
        "travel_class": booking_details.get("travel_class"),
    }

    # Tokenize and POS tag user input
    tokens = word_tokenize(user_input)
    pos_tags = pos_tag(tokens)

    # Extract travel class
    if not details["travel_class"]:
        if "economy" in user_input.lower():
            details["travel_class"] = "economy"
        elif "business" in user_input.lower():
            details["travel_class"] = "business"
        elif "first" in user_input.lower():
            details["travel_class"] = "first"

    # Handle "from" and "to" as indicators for origin and destination with proper noun check
    if "from" in tokens:
        from_index = tokens.index("from") + 1
        if from_index < len(tokens):
            potential_origin = tokens[from_index]
            if pos_tags[from_index][1] == 'NNP' or potential_origin.capitalize() in ORIGINS:
                details["origin"] = confirm_location(potential_origin, ORIGINS, name) or details["origin"]

    if "to" in tokens:
        to_index = tokens.index("to") + 1
        if to_index < len(tokens):
            potential_destination = tokens[to_index]
            if pos_tags[to_index][1] == 'NNP' or potential_destination.capitalize() in DESTINATIONS:
                details["destination"] = confirm_location(potential_destination, DESTINATIONS, name) or details["destination"]

    # Use POS tagging as backup if "from" and "to" are not used
    if not details["origin"] or not details["destination"]:
        for word, tag in pos_tags:
            potential_location = word.capitalize()
            if tag == 'NNP' and not details["origin"] and potential_location in ORIGINS:
                details["origin"] = confirm_location(potential_location, ORIGINS, name)
            elif tag == 'NNP' and not details["destination"] and potential_location in DESTINATIONS:
                details["destination"] = confirm_location(potential_location, DESTINATIONS, name)

    # Extract departure date (e.g., "tomorrow" or "DD-MM-YYYY")
    if not details["departure_date"]:
        details["departure_date"] = parse_date(user_input)

    # Print acknowledgment of parsed details
    if(all(details.values())):
        print("\nBot: Here's what I've understood so far:")
        for key, value in details.items():
            if value:
                print(f" - {key.capitalize()}: {value}")
            else:
                print(f" - {key.capitalize()}: Not provided yet")
        print("")
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
        print(get_response("no_flights_found"))
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
def prompt_for_missing_detail(detail_name, prompt_text, name, validation_func=None):
    while True:
        print(f"{prompt_text}")
        response = input(f"{name}: ").strip()
        
        # Use confirm_location if the detail is a location
        if detail_name in ["origin", "destination"]:
            location_list = ORIGINS if detail_name == "origin" else DESTINATIONS
            confirmed_location = confirm_location(response, location_list, name)
            if confirmed_location:
                return confirmed_location
        
        # Apply validation function if provided
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
    booking_details = parse_booking_details(user_input, {}, name)

    # Prompt user for missing details
    if not booking_details["origin"]:
        booking_details["origin"] = prompt_for_missing_detail(
            "origin", get_response("origin_prompt", available_origins=", ".join(ORIGINS)), name,
            lambda x: best_match_location(x, ORIGINS)
        )

    if not booking_details["destination"]:
        booking_details["destination"] = prompt_for_missing_detail(
            "destination", get_response("destination_prompt", available_destinations=", ".join(DESTINATIONS)), name,
            lambda x: best_match_location(x, DESTINATIONS)
        )

    if not booking_details["departure_date"]:
        booking_details["departure_date"] = prompt_for_missing_detail(
            "departure_date", get_response("departure_date_prompt"), name,
            lambda x: parse_date(x)
        )

    if not booking_details["travel_class"]:
        booking_details["travel_class"] = prompt_for_missing_detail(
            "travel_class", get_response("travel_class_prompt"), name,
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
            print(get_response("confirmation_prompt"))
            confirm = input(f"{name}: ")
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
            print("\nBot: Please enter the number of the flight you'd like to book.")
            selected_flight_index = int(input(f"{name}: ")) - 1
            selected_flight = flights[selected_flight_index]
            booking_details["flight_number"] = selected_flight[0]
            print(get_response("booking_confirmed_details", flight_number=selected_flight[0], origin=selected_flight[1],
                               destination=selected_flight[2], departure_date=selected_flight[3],
                               travel_class=selected_flight[5]))
    else:
        print("Bot: I couldn't find any flights matching your criteria.")

    conn.close()
