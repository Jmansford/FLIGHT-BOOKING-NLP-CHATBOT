import sqlite3
from Classes.responses import get_response
from datetime import datetime, timedelta
import re
from Classes.preprocessing import preprocess_input
from nltk.corpus import stopwords

# Connect to SQLite database
def connect_to_db():
    return sqlite3.connect('Resources/flight_booking.db')

# Extract Location Function
def extract_location(user_input):
    tokens = preprocess_input(user_input)
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token not in stop_words and token.isalpha()]

    # Assume the last meaningful word is the location
    if filtered_tokens:
        return filtered_tokens[-1].capitalize()
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

# Find Flights in Database with Exact or Flexible Criteria
def find_flights(conn, origin, destination, departure_date, travel_class, flexible=False):
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

    # If no exact matches and flexible search is enabled, relax the criteria
    if not flights and flexible:
        print("Bot: No exact matches found. Let me find some similar options.")
        
        # Adjusted query to find flights within ±7 days of departure_date
        query = '''
        SELECT flight_number, origin, destination, departure_date, return_date, travel_class, price
        FROM flights
        WHERE origin = ? AND destination = ?
        AND departure_date BETWEEN ? AND ?
        '''
        
        # Search for flights within a 7 day range
        start_date = (departure_date - timedelta(days=7)).strftime('%d-%m-%Y')
        end_date = (departure_date + timedelta(days=7)).strftime('%d-%m-%Y')
        params = [origin, destination, start_date, end_date]
        
        cursor.execute(query, params)
        flights = cursor.fetchall()

    # If still no matches, find the next available flight after the requested date
    if not flights:
        print("Bot: No close matches found. Searching for the next available flight.")
        query = '''
        SELECT flight_number, origin, destination, departure_date, return_date, travel_class, price
        FROM flights
        WHERE origin = ? AND destination = ? AND departure_date > ?
        ORDER BY departure_date ASC
        LIMIT 1
        '''
        params = [origin, destination, departure_date.strftime('%d-%m-%Y')]
        
        cursor.execute(query, params)
        flights = cursor.fetchall()
    
    return flights

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
    
    # Step 4: Get Travel Class
    while not booking_details["travel_class"]:
        print("Bot: What class would you like to travel in? (economy, business, first): ")
        user_input = input(f"{name}: ")
        travel_class = user_input.lower()
        if travel_class in ['economy', 'business', 'first']:
            booking_details["travel_class"] = travel_class
            print(get_response("travel_class", travel_class=booking_details['travel_class']))
        else:
            print("Bot: Please choose a valid class (economy, business, first).")
    
    # Step 5: Query Database for Available Flights
    conn = connect_to_db()
    flights = find_flights(conn, booking_details['origin'], booking_details['destination'], booking_details['departure_date'], booking_details['travel_class'], flexible=True)
    
    # Directly ask to book if only one flight is returned
    if flights:
        if len(flights) == 1:
            # Only one flight found, directly ask for confirmation
            flight = flights[0]
            print(f"Bot: I found one flight: Flight {flight[0]} from {flight[1]} to {flight[2]}, "
                  f"Departure: {flight[3]}, Return: {flight[4] if flight[4] else 'One-way'}, "
                  f"Class: {flight[5]}, Price: ${flight[6]}")
            
            print("Bot: Would you like to book this flight?")
            confirm = input(f"{name}: ")
            if confirm.lower() in ['yes', 'y']:
                booking_details['flight_number'] = flight[0]
                print(get_response("booking_confirmed"))
            else:
                print("Bot: No problem, let me know if you need anything else.")
        else:
            # Multiple flights found, print and prompt to select
            print("Bot: Here are the available flights:")
            for i, flight in enumerate(flights, start=1):
                print(f"{i}. Flight {flight[0]} from {flight[1]} to {flight[2]}, "
                      f"Departure: {flight[3]}, Return: {flight[4] if flight[4] else 'One-way'}, "
                      f"Class: {flight[5]}, Price: ${flight[6]}")
            
            # Prompt user to select a flight
            while True:
                print("Bot: Please enter the number of the flight you'd like to book.")
                try:
                    choice = int(input(f"{name}: ")) - 1
                    selected_flight = flights[choice]
                    booking_details['flight_number'] = selected_flight[0]
                    print(get_response("booking_confirmed_details", flight_number=selected_flight[0], origin=selected_flight[1],
                                       destination=selected_flight[2], departure_date=selected_flight[3],
                                       travel_class=selected_flight[5]))
                    break
                except (IndexError, ValueError):
                    print("Bot: Please enter a valid number.")
    else:
        # If no flights were found
        print("Bot: I couldn't find any flights matching your criteria.")

    # Close the database connection
    conn.close()
