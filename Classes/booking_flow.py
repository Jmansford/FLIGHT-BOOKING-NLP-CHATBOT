import sqlite3
from Classes.responses import get_response
from datetime import datetime, timedelta
import re
from Classes.preprocessing import preprocess_input
from nltk.corpus import stopwords
from nltk.metrics import edit_distance

# List of available origins and destinations
ORIGINS = ["London", "Toronto", "Sydney", "Dubai", "Frankfurt", "Mumbai"]
DESTINATIONS = ["Paris", "New York", "Berlin", "Singapore", "Tokyo", "Amsterdam"]

# Connect to SQLite database
def connect_to_db():
    return sqlite3.connect('Resources/flight_booking.db')

# Function to find the best matching location from a list based on user input
def best_match_location(user_input, location_list):
    # Preprocess the user input
    tokens = preprocess_input(user_input)
    
    # Filter out non-alphabetic tokens and capitalise each token to standardise for comparison
    filtered_tokens = [token.capitalize() for token in tokens if token.isalpha()]
    
    # Join tokens to handle multi-word locations (e.g., "New York")
    location = ' '.join(filtered_tokens)
    
    # Find the closest match in location_list based on edit distance (Levenshtein distance)
    best_match = min(location_list, key=lambda x: edit_distance(location, x))
    
    # Return the best match if its edit distance to the input is within the allowed threshold
    return best_match if edit_distance(location, best_match) <= 3 else None  

# Primary function to extract the location from user input, using both origin and destination lists
def extract_location(user_input):
    # Check if user input matches any available origin location
    origin_match = best_match_location(user_input, ORIGINS)
    if origin_match:
        return origin_match  # Return the origin match if found
    
    # Check if user input matches any available destination location
    destination_match = best_match_location(user_input, DESTINATIONS)
    if destination_match:
        return destination_match  # Return the destination match if found
    
    # Return None if no suitable match is found within the threshold
    return None

# Helper function to parse dates from user input
def parse_date(input_date, reference_date=None):
    reference_date = reference_date or datetime.now()
    input_date = input_date.lower()
    
    try:
        if input_date == "tomorrow":
            return reference_date + timedelta(days=1)
        elif "in" in input_date and "days" in input_date:
            days = int(re.search(r"\d+", input_date).group())
            return reference_date + timedelta(days=days)
        elif "days later" in input_date:
            days = int(re.search(r"\d+", input_date).group())
            return reference_date + timedelta(days=days)
        elif "next week" in input_date or "week later" in input_date:
            return reference_date + timedelta(weeks=1)
        else:
            return datetime.strptime(input_date, '%d-%m-%Y')
    except (ValueError, AttributeError):
        return None

# Function to find flights in the database based on search criteria
def find_flights(conn, origin, destination, departure_date, travel_class):
    cursor = conn.cursor()
    
    # Exact match query
    query = '''
    SELECT flight_number, origin, destination, departure_date, return_date, travel_class, price
    FROM flights
    WHERE origin = ? AND destination = ? AND departure_date = ? AND travel_class = ?
    '''
    params = [origin, destination, departure_date.strftime('%d-%m-%Y'), travel_class]
    cursor.execute(query, params)
    flights = cursor.fetchall()
    
    # If no matches, find the next available flight after requested date
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

# Helper function to get user input with prompt and validation
def get_user_input(prompt, validation_func=None):
    while True:
        user_input = input(prompt + ": ")
        if validation_func:
            valid_input = validation_func(user_input)
            if valid_input:
                return valid_input
        else:
            return user_input
        print("Bot: Please enter a valid input.")

# Main booking flow
def booking_flow(name):
    booking_details = {
        "origin": None,
        "destination": None,
        "departure_date": None,
        "return_date": None,
        "travel_class": None,
    }
    
    print("Bot: Let's get the details for your flight booking.")
    
    # Step 1: Get Origin with validation
    booking_details["origin"] = get_user_input(
        f"Please provide the origin (Available: {', '.join(ORIGINS)})", 
        lambda x: extract_location(x) if extract_location(x) in ORIGINS else None
    )
    print(get_response("origin", origin=booking_details["origin"])) 
    
    # Step 2: Get Destination with validation
    booking_details["destination"] = get_user_input(
        f"Please provide the destination (Available: {', '.join(DESTINATIONS)})", 
        lambda x: extract_location(x) if extract_location(x) in DESTINATIONS else None
    )
    print(get_response("destination", destination=booking_details["destination"]))
    
    # Step 3: Get Departure Date
    booking_details["departure_date"] = get_user_input(
        "When would you like to depart? (Format: DD-MM-YYYY or relative terms like 'tomorrow')", 
        lambda x: parse_date(x)
    )
    print(get_response("departure_date", departure_date=booking_details["departure_date"].strftime('%d-%m-%Y')))
    
    # Step 4: Get Travel Class
    booking_details["travel_class"] = get_user_input(
        "What class would you like to travel in? (economy, business, first)", 
        lambda x: x.lower() if x.lower() in ["economy", "business", "first"] else None
    )
    print(get_response("travel_class", travel_class=booking_details["travel_class"]))
    
    # Step 5: Query Database for Available Flights
    conn = connect_to_db()
    flights = find_flights(
        conn, 
        booking_details["origin"], 
        booking_details["destination"], 
        booking_details["departure_date"], 
        booking_details["travel_class"], 
    )
    
    # Handle flight selection based on availability
    if flights:
        if len(flights) == 1:
            # Direct confirmation if only one flight is found
            flight = flights[0]
            print(f"Bot: I found one flight: \n\nFlight {flight[0]} from {flight[1]} to {flight[2]}, "
                  f"Departure: {flight[3]}, Return: {flight[4] if flight[4] else 'One-way'}, "
                  f"Class: {flight[5]}, Price: ${flight[6]}\n")
            confirm = get_user_input("Would you like to book this flight? (yes/no)", lambda x: x.lower() in ["yes", "no", "y", "n"])
            if confirm in ["yes", "y"]:
                booking_details["flight_number"] = flight[0]
                print(get_response("booking_confirmed"))
            else:
                print("Bot: No problem, let me know if you need anything else.")
        else:
            # List flights if multiple options found
            print("Bot: Here are the available flights:")
            for i, flight in enumerate(flights, start=1):
                print(f"{i}. Flight {flight[0]} from {flight[1]} to {flight[2]}, "
                      f"Departure: {flight[3]}, Return: {flight[4] if flight[4] else 'One-way'}, "
                      f"Class: {flight[5]}, Price: ${flight[6]}")
            # Prompt user to select a flight
            selected_flight = get_user_input("Please enter the number of the flight you'd like to book", 
                                             lambda x: flights[int(x)-1] if x.isdigit() and 0 < int(x) <= len(flights) else None)
            booking_details["flight_number"] = selected_flight[0]
            print(get_response("booking_confirmed_details", flight_number=selected_flight[0], origin=selected_flight[1],
                               destination=selected_flight[2], departure_date=selected_flight[3],
                               travel_class=selected_flight[5]))
    else:
        print("Bot: I couldn't find any flights matching your criteria.")

    # Close the database connection
    conn.close() 
