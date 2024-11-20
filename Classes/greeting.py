import sqlite3

DB_PATH = 'Resources/flight_booking.db'

def connect_to_db():
    return sqlite3.connect(DB_PATH)

def check_existing_user(name):
    conn = connect_to_db()
    cursor = conn.cursor()
    query = "SELECT origin, destination, departure_date FROM bookings WHERE user_name = ? ORDER BY departure_date DESC LIMIT 1"
    cursor.execute(query, (name,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_user_name():
    print("\nBot: Hi, let's get started with your name: ")
    return input("Enter your name: ").strip()

def welcome_user():
    name = get_user_name()
    last_booking = check_existing_user(name)

    if last_booking:
        origin, destination, departure_date = last_booking
        print(f"\nBot: Welcome back, {name}! Last time, you booked a flight from {origin} to {destination} on {departure_date}. How can I assist you today?")
    else:
        print(f"\nBot: Hello {name}! Welcome to the Travel Booking Assistant. I can help you book a flight or manage your travel plans. How can I assist you?")
    
    return name
