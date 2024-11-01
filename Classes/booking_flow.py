import sqlite3
from Classes.responses import get_response
from datetime import datetime, timedelta
import re
from Classes.preprocessing import preprocess_input
from nltk.corpus import stopwords

# Connect to SQLite database
def connect_to_db():
    return sqlite3.connect('Resources/flight_booking.db')

# Helper function to extract location from user input
def extract_location(user_input):
    tokens = preprocess_input(user_input)
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token not in stop_words and token.isalpha()]
    return filtered_tokens[-1].capitalize() if filtered_tokens else user_input

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
    
    # Step 1: Get Origin
    booking_details["origin"] = get_user_input(
        "Please provide the origin", lambda x: extract_location(x)
    )
    print(get_response("origin", origin=booking_details["origin"]))
    
    # Step 2: Get Destination
    booking_details["destination"] = get_user_input(
        "Please provide the destination", lambda x: extract_location(x)
    )
    print(get_response("destination", destination=booking_details["destination"]))
    
    # Step 3: Get Departure Date
    booking_details["departure_date"] = get_user_input(
        "When would you like to depart?", lambda x: parse_date(x)
    )
    print(get_response("departure_date", departure_date=booking_details["departure_date"].strftime('%d-%m-%Y')))
    
    # Step 4: Get Travel Class
    booking_details["travel_class"] = get_user_input(
        "What class would you like to travel in? (economy, business, first):", 
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
            print(f"Bot: I found one flight: Flight {flight[0]} from {flight[1]} to {flight[2]}, "
                  f"Departure: {flight[3]}, Return: {flight[4] if flight[4] else 'One-way'}, "
                  f"Class: {flight[5]}, Price: ${flight[6]}")
            confirm = get_user_input("Would you like to book this flight? (yes/no):", lambda x: x.lower() in ["yes", "no", "y", "n"])
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
            selected_flight = get_user_input("Please enter the number of the flight you'd like to book:", 
                                             lambda x: flights[int(x)-1] if x.isdigit() and 0 < int(x) <= len(flights) else None)
            booking_details["flight_number"] = selected_flight[0]
            print(get_response("booking_confirmed_details", flight_number=selected_flight[0], origin=selected_flight[1],
                               destination=selected_flight[2], departure_date=selected_flight[3],
                               travel_class=selected_flight[5]))
    else:
        print("Bot: I couldn't find any flights matching your criteria.")

    # Close the database connection
    conn.close()
