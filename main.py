import sqlite3

# === Database Setup ===
def setup_database():
    connection = sqlite3.connect("pomona_transit.db")
    cursor = connection.cursor()

    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS Trip (
        TripNumber INTEGER PRIMARY KEY,
        StartLocationName TEXT,
        DestinationName TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS TripOffering (
        TripNumber INTEGER,
        Date TEXT,
        ScheduledStartTime TEXT,
        ScheduledArrivalTime TEXT,
        DriverName TEXT,
        BusID INTEGER,
        PRIMARY KEY (TripNumber, Date, ScheduledStartTime),
        FOREIGN KEY (TripNumber) REFERENCES Trip(TripNumber)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Bus (
        BusID INTEGER PRIMARY KEY,
        Model TEXT,
        Year INTEGER
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Driver (
        DriverName TEXT PRIMARY KEY,
        DriverTelephoneNumber TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Stop (
        StopNumber INTEGER PRIMARY KEY,
        StopAddress TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS TripStopInfo (
        TripNumber INTEGER,
        StopNumber INTEGER,
        SequenceNumber INTEGER,
        DrivingTime INTEGER,
        PRIMARY KEY (TripNumber, StopNumber),
        FOREIGN KEY (TripNumber) REFERENCES Trip(TripNumber),
        FOREIGN KEY (StopNumber) REFERENCES Stop(StopNumber)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS ActualTripStopInfo (
        TripNumber INTEGER,
        Date TEXT,
        ScheduledStartTime TEXT,
        StopNumber INTEGER,
        ScheduledArrivalTime TEXT,
        ActualStartTime TEXT,
        ActualArrivalTime TEXT,
        NumberOfPassengerIn INTEGER,
        NumberOfPassengerOut INTEGER,
        PRIMARY KEY (TripNumber, Date, ScheduledStartTime, StopNumber),
        FOREIGN KEY (TripNumber) REFERENCES Trip(TripNumber),
        FOREIGN KEY (StopNumber) REFERENCES Stop(StopNumber)
    )''')

    connection.commit()
    connection.close()


# === Database Connection Helper ===
def get_connection():
    return sqlite3.connect("pomona_transit.db")


# === Transaction Functions ===
def display_schedule(start_location, destination, date):
    connection = get_connection()
    cursor = connection.cursor()

    query = '''
    SELECT TripOffering.TripNumber, TripOffering.Date, 
           TripOffering.ScheduledStartTime, TripOffering.ScheduledArrivalTime, 
           TripOffering.DriverName, TripOffering.BusID
    FROM TripOffering
    JOIN Trip ON Trip.TripNumber = TripOffering.TripNumber
    WHERE Trip.StartLocationName = ? AND Trip.DestinationName = ? AND TripOffering.Date = ?
    '''

    cursor.execute(query, (start_location, destination, date))
    results = cursor.fetchall()
    connection.close()
    return results


def delete_trip_offering(trip_number, date, start_time):
    connection = get_connection()
    cursor = connection.cursor()

    query = '''
    DELETE FROM TripOffering 
    WHERE TripNumber = ? AND Date = ? AND ScheduledStartTime = ?
    '''
    cursor.execute(query, (trip_number, date, start_time))
    connection.commit()
    connection.close()


def add_trip_offering(trip_number, date, start_time, arrival_time, driver, bus_id):
    connection = get_connection()
    cursor = connection.cursor()

    query = '''
    INSERT INTO TripOffering (TripNumber, Date, ScheduledStartTime, ScheduledArrivalTime, DriverName, BusID)
    VALUES (?, ?, ?, ?, ?, ?)
    '''
    cursor.execute(query, (trip_number, date, start_time, arrival_time, driver, bus_id))
    connection.commit()
    connection.close()


def display_stops(trip_number):
    connection = get_connection()
    cursor = connection.cursor()

    query = '''
    SELECT StopNumber, SequenceNumber, DrivingTime 
    FROM TripStopInfo 
    WHERE TripNumber = ?
    ORDER BY SequenceNumber
    '''
    cursor.execute(query, (trip_number,))
    results = cursor.fetchall()
    connection.close()
    return results


def add_bus(bus_id, model, year):
    connection = get_connection()
    cursor = connection.cursor()

    query = '''
    INSERT INTO Bus (BusID, Model, Year) VALUES (?, ?, ?)
    '''
    cursor.execute(query, (bus_id, model, year))
    connection.commit()
    connection.close()


def delete_bus(bus_id):
    connection = get_connection()
    cursor = connection.cursor()

    query = '''
    DELETE FROM Bus WHERE BusID = ?
    '''
    cursor.execute(query, (bus_id,))
    connection.commit()
    connection.close()


# === User Interface ===
def main_menu():
    while True:
        print("\n--- Pomona Transit System ---")
        print("1. Display Schedule")
        print("2. Edit Schedule")
        print("3. Display Stops for a Trip")
        print("4. Add Bus")
        print("5. Delete Bus")
        print("0. Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            start = input("Enter Start Location: ")
            destination = input("Enter Destination: ")
            date = input("Enter Date (YYYY-MM-DD): ")
            schedule = display_schedule(start, destination, date)
            print("\nSchedule:")
            for row in schedule:
                print(row)
        elif choice == "2":
            sub_choice = input("Edit Schedule - 1. Delete Trip 2. Add Trip: ")
            if sub_choice == "1":
                trip_number = int(input("Enter Trip Number: "))
                date = input("Enter Date (YYYY-MM-DD): ")
                start_time = input("Enter Scheduled Start Time: ")
                delete_trip_offering(trip_number, date, start_time)
                print("Trip offering deleted.")
            elif sub_choice == "2":
                trip_number = int(input("Enter Trip Number: "))
                date = input("Enter Date (YYYY-MM-DD): ")
                start_time = input("Enter Scheduled Start Time: ")
                arrival_time = input("Enter Scheduled Arrival Time: ")
                driver = input("Enter Driver Name: ")
                bus_id = int(input("Enter Bus ID: "))
                add_trip_offering(trip_number, date, start_time, arrival_time, driver, bus_id)
                print("Trip offering added.")
        elif choice == "3":
            trip_number = int(input("Enter Trip Number: "))
            stops = display_stops(trip_number)
            print("\nStops:")
            for row in stops:
                print(row)
        elif choice == "4":
            bus_id = int(input("Enter Bus ID: "))
            model = input("Enter Bus Model: ")
            year = int(input("Enter Bus Year: "))
            add_bus(bus_id, model, year)
            print("Bus added.")
        elif choice == "5":
            bus_id = int(input("Enter Bus ID: "))
            delete_bus(bus_id)
            print("Bus deleted.")
        elif choice == "0":
            break
        else:
            print("Invalid choice. Please try again.")


# === Main Execution ===
if __name__ == "__main__":
    setup_database()
    main_menu()
