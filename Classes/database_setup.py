import sqlite3
from datetime import datetime, timedelta
import random

def setup_database():
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('Resources/flight_booking.db')
    cursor = conn.cursor()

    # Create the flights table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flights (
        id INTEGER PRIMARY KEY,
        flight_number TEXT NOT NULL,
        origin TEXT NOT NULL,
        destination TEXT NOT NULL,
        departure_date TEXT NOT NULL,
        return_date TEXT,
        travel_class TEXT NOT NULL,
        price REAL NOT NULL
    )
    ''')
    conn.commit()

    # Generate flight data starting from tomorrow
    def generate_flight_data():
        flight_data = []
        tomorrow = datetime.now() + timedelta(days=1)
        
        origins = ["London", "Toronto", "Sydney", "Dubai", "Frankfurt", "Mumbai"]
        destinations = ["Paris", "New York", "Berlin", "Singapore", "Tokyo", "Amsterdam"]
        travel_classes = ["economy", "business", "first"]
        base_price = 100  # Base price for economy

        # Create flight data for the next 30 days with variation
        for destination in destinations:
            for day in range(30):  # Flights spread over the next 30 days
                # Randomly decide if a flight should be created for this day
                if random.choice([True, False]):  # 50% chance of creating a flight for this day
                    departure_date = (tomorrow + timedelta(days=day)).strftime('%d-%m-%Y')
                    return_date = (tomorrow + timedelta(days=day + 7)).strftime('%d-%m-%Y')  # Return 7 days later

                    # Randomly choose an origin, ensuring it is not the same as the destination
                    origin = random.choice([o for o in origins if o != destination])

                    # Randomly select travel classes to create flights with
                    selected_classes = random.sample(travel_classes, k=random.randint(1, len(travel_classes)))

                    for travel_class in selected_classes:
                        # Adjust price based on class
                        price_multiplier = 1.0 if travel_class == "economy" else (1.5 if travel_class == "business" else 2.0)
                        price = base_price * price_multiplier + (day * 5)  # Increase slightly for each day

                        # Create a unique flight number
                        flight_number = f"{origin[:2].upper()}{destination[:2].upper()}{100 + day * len(travel_classes)}"

                        # Append flight data to the list
                        flight_data.append((flight_number, origin, destination, departure_date, return_date, travel_class, price))
        
        return flight_data

    # Delete existing flights for the same departure dates, destinations, and travel class to avoid duplicates
    def delete_existing_flights(cursor, flight_data):
        for flight in flight_data:
            flight_number, origin, destination, departure_date, return_date, travel_class, price = flight
            cursor.execute('''
            DELETE FROM flights
            WHERE destination = ? AND departure_date = ? AND travel_class = ?
            ''', (destination, departure_date, travel_class))

    def create_bookings_table():
        # Connect to the SQLite database (or create it if it doesn't exist)
        conn = sqlite3.connect('Resources/flight_booking.db')
        cursor = conn.cursor()

        # Create the bookings table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            user_name TEXT NOT NULL,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            departure_date TEXT NOT NULL,
            return_date TEXT,
            flight_number TEXT NOT NULL,
            travel_class TEXT NOT NULL
        )
        ''')
        conn.commit()
        # print("Bookings table created successfully.")

    # Generate new flight data
    flight_data = generate_flight_data()
    create_bookings_table()

    # Delete existing flights to avoid duplicates
    delete_existing_flights(cursor, flight_data)

    # Insert the generated flight data into the database
    cursor.executemany('''
    INSERT INTO flights (flight_number, origin, destination, departure_date, return_date, travel_class, price)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', flight_data)
    conn.commit()
    # print("Flight data inserted successfully without duplicates.")

    # Close the database connection
    conn.close()
