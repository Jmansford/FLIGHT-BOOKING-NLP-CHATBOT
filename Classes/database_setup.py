import sqlite3
from datetime import datetime, timedelta
import random

def setup_database():
    # Connect to the SQLite database (or create it if it doesn't exist).
    conn = sqlite3.connect('Resources/flight_booking.db')
    cursor = conn.cursor()

    # Create the flights table if it doesn't already exist.
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

    # Function to generate flight data starting from tomorrow.
    def generate_flight_data():
        flight_data = []
        tomorrow = datetime.now() + timedelta(days=1)

        origins = ["London", "Toronto", "Sydney", "Dubai", "Frankfurt", "Mumbai"]
        destinations = ["Paris", "New York", "Berlin", "Singapore", "Tokyo", "Amsterdam"]
        travel_classes = ["economy", "business", "first"]
        base_price = 100  # Base price for economy class flights.

        # Generate flight data for the next 30 days.
        for destination in destinations:
            for day in range(30):  # Flights are spread over the next 30 days.
                # Randomly decide whether to create a flight for this day (50% chance).
                if random.choice([True, False]):
                    departure_date = (tomorrow + timedelta(days=day)).strftime('%d-%m-%Y')
                    return_date = (tomorrow + timedelta(days=day + 7)).strftime('%d-%m-%Y')  # Return after 7 days.

                    # Randomly select an origin that is not the same as the destination.
                    origin = random.choice([o for o in origins if o != destination])

                    # Randomly select travel classes for flight creation.
                    selected_classes = random.sample(travel_classes, k=random.randint(1, len(travel_classes)))

                    for travel_class in selected_classes:
                        # Adjust the price based on the travel class.
                        price_multiplier = 1.0 if travel_class == "economy" else (1.5 if travel_class == "business" else 2.0)
                        price = base_price * price_multiplier + (day * 5)  # Slight increase for each day.

                        # Generate a unique flight number.
                        flight_number = f"{origin[:2].upper()}{destination[:2].upper()}{100 + day * len(travel_classes)}"

                        # Append flight details to the data list.
                        flight_data.append((flight_number, origin, destination, departure_date, return_date, travel_class, price))
        
        return flight_data

    # Function to delete existing flights to avoid duplication.
    def delete_existing_flights(cursor, flight_data):
        for flight in flight_data:
            _, origin, destination, departure_date, return_date, travel_class, _ = flight
            cursor.execute('''
            DELETE FROM flights
            WHERE destination = ? AND departure_date = ? AND travel_class = ?
            ''', (destination, departure_date, travel_class))

    # Function to create the bookings table if it doesn't exist.
    def create_bookings_table():
        # Connect to the SQLite database (or create it if it doesn't exist).
        conn = sqlite3.connect('Resources/flight_booking.db')
        cursor = conn.cursor()

        # Create the bookings table if it doesn't already exist.
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

    # Generate flight data for the next 30 days.
    flight_data = generate_flight_data()
    create_bookings_table()

    # Remove duplicate flights from the database before inserting new data.
    delete_existing_flights(cursor, flight_data)

    # Insert the generated flight data into the flights table.
    cursor.executemany('''
    INSERT INTO flights (flight_number, origin, destination, departure_date, return_date, travel_class, price)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', flight_data)
    conn.commit()

    # Close the database connection.
    conn.close()
