import sqlite3
from Classes.responses import get_response
from nltk import pos_tag, word_tokenize
from nltk.metrics import edit_distance
from Classes.date_parser import parse_date 

# Constants for available origins and destinations
ORIGINS = ["London", "Toronto", "Sydney", "Dubai", "Frankfurt", "Mumbai"]
DESTINATIONS = ["Paris", "New York", "Berlin", "Singapore", "Tokyo", "Amsterdam"]

# Database connection
def connect_to_db():
    return sqlite3.connect('Resources/flight_booking.db')

# Match user input with the closest location accounting for typos
def best_match_location(user_input, location_list, max_distance=2):
    tokens = word_tokenize(user_input)
    filtered_tokens = [token.capitalize() for token in tokens if token.isalpha()]
    location = ' '.join(filtered_tokens)
    best_match = min(location_list, key=lambda x: edit_distance(location, x))
    return best_match if edit_distance(location, best_match) <= max_distance else None

# Confirm the best match location with the user
def confirm_location(user_input, location_list, name):
    suggested_location = best_match_location(user_input, location_list)
    if suggested_location and suggested_location.lower() != user_input.lower():
        print(f"Bot: Did you mean '{suggested_location}'? (yes/no)")
        confirm = input(f"{name}: ").strip().lower()
        if confirm in ["yes", "y"]:
            return suggested_location
        print("Bot: Got it, please try again.")
    return user_input if user_input.capitalize() in location_list else None

# Parse booking details from user input
def parse_booking_details(user_input, booking_details, name):
    details = {
        "origin": booking_details.get("origin"),
        "destination": booking_details.get("destination"),
        "departure_date": booking_details.get("departure_date"),
        "travel_class": booking_details.get("travel_class"),
    }

    tokens = word_tokenize(user_input)
    pos_tags = pos_tag(tokens)

    # Extract travel class
    if not details["travel_class"]:
        classes = {"economy": "economy", "business": "business", "first": "first"}
        for key, value in classes.items():
            if key in user_input.lower():
                details["travel_class"] = value

    # Handle "from" and "to" keywords for origin and destination
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

    # Use POS tagging as a backup
    for word, tag in pos_tags:
        location = word.capitalize()
        if tag == 'NNP' and not details["origin"] and location in ORIGINS:
            details["origin"] = confirm_location(location, ORIGINS, name)
        elif tag == 'NNP' and not details["destination"] and location in DESTINATIONS:
            details["destination"] = confirm_location(location, DESTINATIONS, name)

    # Extract departure date
    if not details["departure_date"]:
        details["departure_date"] = parse_date(user_input)

    # Acknowledge parsed details
    if any(details.values()):
        print("\nBot: Here's what I've understood so far:")
        for key, value in details.items():
            print(f" - {key.capitalize()}: {value or 'Not provided yet'}")
        print("")
    return details

# Find flights in the database
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

# Prompt user for missing booking details
def prompt_for_missing_detail(detail_name, prompt_text, name, validation_func=None):
    while True:
        print(f"{prompt_text}")
        response = input(f"{name}: ").strip()
        
        if detail_name in ["origin", "destination"]:
            location_list = ORIGINS if detail_name == "origin" else DESTINATIONS
            confirmed_location = confirm_location(response, location_list, name)
            if confirmed_location:
                return confirmed_location
        
        if validation_func:
            valid_response = validation_func(response)
            if valid_response:
                return valid_response
        else:
            return response
        
        print("Bot: Please enter a valid input.")

# Save booking to the database
def save_booking(conn, booking_details, name):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO bookings (user_name, origin, destination, departure_date, return_date, flight_number, travel_class)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        name,
        booking_details["origin"],
        booking_details["destination"],
        booking_details["departure_date"].strftime('%d-%m-%Y'),
        booking_details.get("return_date").strftime('%d-%m-%Y') if booking_details.get("return_date") else None,
        booking_details["flight_number"],
        booking_details["travel_class"]
    ))
    conn.commit()
    print("Bot: Your booking has been saved successfully.")

# PPrint out bookings for a specified user
def display_bookings(name):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT flight_number, origin, destination, departure_date, travel_class
        FROM bookings
        WHERE user_name = ?
        ORDER BY departure_date ASC
    ''', (name,))
    bookings = cursor.fetchall()
    conn.close()

    if not bookings:
        print("Bot: You have no bookings at the moment.")
        return None

    print("Bot: Here are your current bookings:\n")
    for booking in bookings:
        print(f"Flight: {booking[0]} from {booking[1]} to {booking[2]}, "
              f"Departure: {booking[3]}, "
              f"Class: {booking[4]}")
    return bookings

# Display bookings for a specified user and allow them to cancel a booking
def display_and_cancel_booking(name):
    bookings = display_bookings(name)
    if not bookings:
        return

    print("\nBot: Would you like to cancel one of your bookings? (yes/no)")
    confirm = input(f"{name}: ").strip().lower()
    if confirm not in ["yes", "y"]:
        print("Bot: No problem, let me know if you need anything else.")
        return

    print("Bot: Please enter the Flight Number of the booking you'd like to cancel:")
    flight_number = input(f"{name}: ").strip()

    matching_bookings = [b for b in bookings if b[0] == flight_number]
    if not matching_bookings:
        print("Bot: I couldn't find that flight in your bookings. Please try again.")
        return

    print(f"Bot: Are you sure you want to cancel the booking for Flight {flight_number}? (yes/no)")
    final_confirm = input(f"{name}: ").strip().lower()
    if final_confirm not in ["yes", "y"]:
        print("Bot: Your booking was not canceled.")
        return

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM bookings
        WHERE user_name = ? AND flight_number = ?
    ''', (name, flight_number))
    conn.commit()
    conn.close()

    print(f"Bot: Your booking for Flight {flight_number} has been successfully canceled.")


# Main booking flow
def booking_flow(name, user_input):
    booking_details = parse_booking_details(user_input, {}, name)

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

    conn = connect_to_db()
    flights = find_flights(
        conn, 
        booking_details["origin"], 
        booking_details["destination"], 
        booking_details["departure_date"], 
        booking_details["travel_class"]
    )

    if flights:
        flight = flights[0]
        print(f"Bot: I found one flight: \n\nFlight {flight[0]} from {flight[1]} to {flight[2]}, "
              f"Departure: {flight[3]}, Return: {flight[4] if flight[4] else 'One-way'}, "
              f"Class: {flight[5]}, Price: ${flight[6]}\n")
        print(get_response("confirmation_prompt"))
        confirm = input(f"{name}: ")
        if confirm in ["yes", "y"]:
            booking_details["flight_number"] = flight[0]
            print(get_response("booking_confirmed"))
            save_booking(conn, booking_details, name)
        else:
            print("Bot: No problem, let me know if you need anything else.")
    else:
        print("Bot: I couldn't find any flights matching your criteria.")

    conn.close()
