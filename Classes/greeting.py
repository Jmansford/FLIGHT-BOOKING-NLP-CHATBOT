import sqlite3
from Classes.responses import get_response

DB_PATH = 'Resources/flight_booking.db'

# Function to connect to the database
def connect_to_db():
    return sqlite3.connect(DB_PATH)

# Function to check if the user has made a booking before
def check_existing_user(username):
    conn = connect_to_db()
    cursor = conn.cursor()
    query = "SELECT origin, destination, departure_date FROM bookings WHERE user_name = ? ORDER BY departure_date DESC LIMIT 1"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    conn.close()
    return result

# Function to get the user's name
def get_user_name():
    print("\nBot: Hi, let's get started with your name: ")
    return input("Enter your name: ").strip()

# Function to welcome the user and display their last booking
def welcome_user():
    username = get_user_name()
    last_booking = check_existing_user(username)

    if last_booking:
        origin, destination, departure_date = last_booking
        print(f"Bot: Welcome back, {username}! Last time, you booked a flight from {origin} to {destination} on {departure_date}. How can I assist you today?")
    else:
        print(get_response("new_user_greeting", name=username))
    
    return username
