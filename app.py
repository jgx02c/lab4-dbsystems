import sqlite3
from datetime import datetime

# [Previous setup_database() function and test data remains exactly the same]

def setup_database():
    connection = sqlite3.connect("pomona_transit.db")
    cursor = connection.cursor()

    # Create all required tables
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS Trip (
            TripNumber INTEGER PRIMARY KEY,
            StartLocationName TEXT,
            DestinationName TEXT
        );

        CREATE TABLE IF NOT EXISTS TripOffering (
            TripNumber INTEGER,
            Date TEXT,
            ScheduledStartTime TEXT,
            ScheduledArrivalTime TEXT,
            DriverName TEXT,
            BusID INTEGER,
            PRIMARY KEY (TripNumber, Date, ScheduledStartTime),
            FOREIGN KEY (TripNumber) REFERENCES Trip(TripNumber),
            FOREIGN KEY (DriverName) REFERENCES Driver(DriverName),
            FOREIGN KEY (BusID) REFERENCES Bus(BusID)
        );

        CREATE TABLE IF NOT EXISTS Bus (
            BusID INTEGER PRIMARY KEY,
            Model TEXT,
            Year INTEGER
        );

        CREATE TABLE IF NOT EXISTS Driver (
            DriverName TEXT PRIMARY KEY,
            DriverTelephoneNumber TEXT
        );

        CREATE TABLE IF NOT EXISTS Stop (
            StopNumber INTEGER PRIMARY KEY,
            StopAddress TEXT
        );

        CREATE TABLE IF NOT EXISTS TripStopInfo (
            TripNumber INTEGER,
            StopNumber INTEGER,
            SequenceNumber INTEGER,
            DrivingTime INTEGER,
            PRIMARY KEY (TripNumber, StopNumber),
            FOREIGN KEY (TripNumber) REFERENCES Trip(TripNumber),
            FOREIGN KEY (StopNumber) REFERENCES Stop(StopNumber)
        );

        CREATE TABLE IF NOT EXISTS ActualTripStopInfo (
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
        );
    ''')
    
    # Insert test data
    test_data = {
        'trips': [
            (1, 'Pomona', 'Los Angeles'),
            (2, 'Pomona', 'San Diego'),
            (3, 'Los Angeles', 'San Francisco')
        ],
        'drivers': [
            ('John Doe', '555-0101'),
            ('Jane Smith', '555-0102'),
            ('Bob Wilson', '555-0103')
        ],
        'buses': [
            (101, 'Mercedes Sprinter', 2020),
            (102, 'Ford Transit', 2021),
            (103, 'Toyota Coaster', 2019)
        ],
        'stops': [
            (1, '123 Main St, Pomona'),
            (2, '456 Broadway, Los Angeles'),
            (3, '789 Ocean Ave, San Diego')
        ],
        'trip_offerings': [
            (1, '2024-11-24', '08:00', '10:00', 'John Doe', 101),
            (1, '2024-11-24', '12:00', '14:00', 'Jane Smith', 102),
            (2, '2024-11-24', '09:00', '13:00', 'Bob Wilson', 103)
        ],
        'trip_stops': [
            (1, 1, 1, 30),
            (1, 2, 2, 45),
            (2, 1, 1, 30),
            (2, 3, 2, 60)
        ]
    }

    # Insert test data with INSERT OR IGNORE to prevent duplicates
    cursor.executemany('INSERT OR IGNORE INTO Trip VALUES (?, ?, ?)', test_data['trips'])
    cursor.executemany('INSERT OR IGNORE INTO Driver VALUES (?, ?)', test_data['drivers'])
    cursor.executemany('INSERT OR IGNORE INTO Bus VALUES (?, ?, ?)', test_data['buses'])
    cursor.executemany('INSERT OR IGNORE INTO Stop VALUES (?, ?)', test_data['stops'])
    cursor.executemany('INSERT OR IGNORE INTO TripOffering VALUES (?, ?, ?, ?, ?, ?)', test_data['trip_offerings'])
    cursor.executemany('INSERT OR IGNORE INTO TripStopInfo VALUES (?, ?, ?, ?)', test_data['trip_stops'])

    connection.commit()
    connection.close()

def get_connection():
    return sqlite3.connect("pomona_transit.db")

def add_driver(name, phone):
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute('INSERT INTO Driver VALUES (?, ?)', (name, phone))
    connection.commit()
    connection.close()

def display_all_drivers():
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT * FROM Driver')
    results = cursor.fetchall()
    connection.close()
    return results

def add_trip_offering(trip_number, date, start_time, arrival_time, driver, bus_id):
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute('''
        INSERT INTO TripOffering 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (trip_number, date, start_time, arrival_time, driver, bus_id))
    
    connection.commit()
    connection.close()


def display_all_trips():
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute('''
        SELECT TripNumber, StartLocationName, DestinationName
        FROM Trip
    ''')
    
    results = cursor.fetchall()
    connection.close()
    return results

def delete_trip(trip_number):
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        # First delete related records from TripOffering and TripStopInfo
        cursor.execute('DELETE FROM TripOffering WHERE TripNumber = ?', (trip_number,))
        cursor.execute('DELETE FROM TripStopInfo WHERE TripNumber = ?', (trip_number,))
        # Then delete the trip itself
        cursor.execute('DELETE FROM Trip WHERE TripNumber = ?', (trip_number,))
        connection.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return False
    finally:
        connection.close()

def delete_bus(bus_id):
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        # Check if bus is currently assigned to any trips
        cursor.execute('SELECT COUNT(*) FROM TripOffering WHERE BusID = ?', (bus_id,))
        if cursor.fetchone()[0] > 0:
            print("Cannot delete bus: Bus is assigned to existing trip offerings")
            return False
            
        cursor.execute('DELETE FROM Bus WHERE BusID = ?', (bus_id,))
        connection.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return False
    finally:
        connection.close()

def delete_driver(driver_name):
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        # Check if driver is currently assigned to any trips
        cursor.execute('SELECT COUNT(*) FROM TripOffering WHERE DriverName = ?', (driver_name,))
        if cursor.fetchone()[0] > 0:
            print("Cannot delete driver: Driver is assigned to existing trip offerings")
            return False
            
        cursor.execute('DELETE FROM Driver WHERE DriverName = ?', (driver_name,))
        connection.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return False
    finally:
        connection.close()

def add_bus(bus_id, model, year):
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('INSERT INTO Bus (BusID, Model, Year) VALUES (?, ?, ?)', 
                      (bus_id, model, year))
        connection.commit()
        return True
    except sqlite3.IntegrityError:
        print("Error: Bus ID already exists!")
        return False
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return False
    finally:
        connection.close()

def display_all_buses():
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT * FROM Bus')
    results = cursor.fetchall()
    connection.close()
    return results

def record_actual_trip_data(trip_number, date, scheduled_start_time):
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        # First, verify the trip offering exists
        cursor.execute('''
            SELECT EXISTS (
                SELECT 1 FROM TripOffering 
                WHERE TripNumber = ? AND Date = ? AND ScheduledStartTime = ?
            )
        ''', (trip_number, date, scheduled_start_time))
        
        if not cursor.fetchone()[0]:
            print("Error: Trip offering not found!")
            return False
        
        # Get all stops for this trip
        cursor.execute('''
            SELECT s.StopNumber, s.StopAddress, tsi.SequenceNumber
            FROM TripStopInfo tsi
            JOIN Stop s ON tsi.StopNumber = s.StopNumber
            WHERE tsi.TripNumber = ?
            ORDER BY tsi.SequenceNumber
        ''', (trip_number,))
        
        stops = cursor.fetchall()
        
        if not stops:
            print("Error: No stops found for this trip!")
            return False
            
        print("\nRecording actual data for each stop:")
        print("(Times should be in HH:MM format)")
        
        for stop in stops:
            print(f"\nStop {stop[0]}: {stop[1]} (Sequence: {stop[2]})")
            
            scheduled_arrival = input("Scheduled Arrival Time: ")
            actual_start = input("Actual Start Time: ")
            actual_arrival = input("Actual Arrival Time: ")
            
            while True:
                try:
                    passengers_in = int(input("Number of Passengers In: "))
                    passengers_out = int(input("Number of Passengers Out: "))
                    break
                except ValueError:
                    print("Please enter valid numbers for passengers.")
            
            # Insert the actual trip stop information
            cursor.execute('''
                INSERT INTO ActualTripStopInfo (
                    TripNumber, Date, ScheduledStartTime, StopNumber,
                    ScheduledArrivalTime, ActualStartTime, ActualArrivalTime,
                    NumberOfPassengerIn, NumberOfPassengerOut
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trip_number, date, scheduled_start_time, stop[0],
                scheduled_arrival, actual_start, actual_arrival,
                passengers_in, passengers_out
            ))
        
        connection.commit()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

def display_actual_trip_data(trip_number, date, scheduled_start_time):
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            SELECT 
                a.StopNumber,
                s.StopAddress,
                a.ScheduledArrivalTime,
                a.ActualStartTime,
                a.ActualArrivalTime,
                a.NumberOfPassengerIn,
                a.NumberOfPassengerOut
            FROM ActualTripStopInfo a
            JOIN Stop s ON a.StopNumber = s.StopNumber
            WHERE a.TripNumber = ? 
            AND a.Date = ? 
            AND a.ScheduledStartTime = ?
            ORDER BY a.StopNumber
        ''', (trip_number, date, scheduled_start_time))
        
        return cursor.fetchall()
    finally:
        connection.close()

def display_trip_stops(trip_number):
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            SELECT tsi.TripNumber, s.StopNumber, s.StopAddress, 
                   tsi.SequenceNumber, tsi.DrivingTime
            FROM TripStopInfo tsi
            JOIN Stop s ON tsi.StopNumber = s.StopNumber
            WHERE tsi.TripNumber = ?
            ORDER BY tsi.SequenceNumber
        ''', (trip_number,))
        
        results = cursor.fetchall()
        return results
    finally:
        connection.close()


def display_driver_weekly_schedule(driver_name, start_date):
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            SELECT 
                t.TripNumber,
                t.StartLocationName,
                t.DestinationName,
                to.Date,
                to.ScheduledStartTime,
                to.ScheduledArrivalTime
            FROM TripOffering to
            JOIN Trip t ON to.TripNumber = t.TripNumber
            WHERE to.DriverName = ?
            AND date(to.Date) BETWEEN date(?) AND date(?, '+6 days')
            ORDER BY to.Date, to.ScheduledStartTime
        ''', (driver_name, start_date, start_date))
        
        results = cursor.fetchall()
        return results
    finally:
        connection.close()



def display_schedule(start_location, destination, date):
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute('''
        SELECT TripOffering.TripNumber, TripOffering.ScheduledStartTime, 
               TripOffering.ScheduledArrivalTime, TripOffering.DriverName, 
               TripOffering.BusID
        FROM TripOffering
        JOIN Trip ON Trip.TripNumber = TripOffering.TripNumber
        WHERE Trip.StartLocationName = ? 
        AND Trip.DestinationName = ? 
        AND TripOffering.Date = ?
    ''', (start_location, destination, date))
    
    results = cursor.fetchall()
    connection.close()
    return results


def main_menu():
    while True:
        print("\n=== Pomona Transit System ===")
        print("1. Display Schedule")
        print("2. Add Driver")
        print("3. Display All Trips")
        print("4. Display All Drivers")
        print("5. Add Trip Offering")
        print("6. Delete Trip")
        print("7. Add Bus")
        print("8. Delete Bus")
        print("9. Delete Driver")
        print("10. Display All Buses")
        print("11. Display Trip Stops")
        print("12. Display Driver's Weekly Schedule")
        print("13. Record Actual Trip Data")
        print("14. View Actual Trip Data")
        print("0. Exit")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            print("\n--- Display Schedule ---")
            print("Available locations:", end=" ")
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT DISTINCT StartLocationName, DestinationName FROM Trip")
            locations = cursor.fetchall()
            print("\nFrom -> To:")
            for loc in locations:
                print(f"{loc[0]} -> {loc[1]}")
            
            start = input("Enter Start Location: ")
            destination = input("Enter Destination: ")
            date = input("Enter Date (YYYY-MM-DD): ")
            
            schedule = display_schedule(start, destination, date)
            print("\nSchedule:")
            print("TripNumber | Start Time | Arrival Time | Driver | Bus ID")
            print("-" * 60)
            for trip in schedule:
                print(f"{trip[0]:^10} | {trip[1]:^10} | {trip[2]:^11} | {trip[3]:^6} | {trip[4]:^6}")
        
        elif choice == "2":
            print("\n--- Add Driver ---")
            name = input("Enter Driver Name: ")
            phone = input("Enter Driver Phone Number: ")
            try:
                add_driver(name, phone)
                print("Driver added successfully!")
            except sqlite3.IntegrityError:
                print("Error: Driver already exists!")
        
        elif choice == "3":
            print("\n--- All Trips ---")
            trips = display_all_trips()
            print("TripNumber | Start Location | Destination")
            print("-" * 50)
            for trip in trips:
                print(f"{trip[0]:^10} | {trip[1]:^14} | {trip[2]}")
        
        elif choice == "4":
            print("\n--- All Drivers ---")
            drivers = display_all_drivers()
            print("Driver Name | Phone Number")
            print("-" * 30)
            for driver in drivers:
                print(f"{driver[0]} | {driver[1]}")
        
        elif choice == "5":
            print("\n--- Add Trip Offering ---")
            trip_number = int(input("Enter Trip Number: "))
            date = input("Enter Date (YYYY-MM-DD): ")
            start_time = input("Enter Start Time (HH:MM): ")
            arrival_time = input("Enter Arrival Time (HH:MM): ")
            driver = input("Enter Driver Name: ")
            bus_id = int(input("Enter Bus ID: "))
            
            try:
                add_trip_offering(trip_number, date, start_time, arrival_time, driver, bus_id)
                print("Trip offering added successfully!")
            except sqlite3.IntegrityError as e:
                print(f"Error: {e}")

        elif choice == "6":
            print("\n--- Delete Trip ---")
            trips = display_all_trips()
            print("\nAvailable Trips:")
            print("TripNumber | Start Location | Destination")
            print("-" * 50)
            for trip in trips:
                print(f"{trip[0]:^10} | {trip[1]:^14} | {trip[2]}")
            
            trip_number = int(input("\nEnter Trip Number to delete: "))
            if delete_trip(trip_number):
                print("Trip deleted successfully!")
            else:
                print("Failed to delete trip.")

        elif choice == "7":
            print("\n--- Add Bus ---")
            bus_id = int(input("Enter Bus ID: "))
            model = input("Enter Bus Model: ")
            year = int(input("Enter Bus Year: "))
            if add_bus(bus_id, model, year):
                print("Bus added successfully!")
            
        elif choice == "8":
            print("\n--- Delete Bus ---")
            buses = display_all_buses()
            print("\nAvailable Buses:")
            print("BusID | Model | Year")
            print("-" * 30)
            for bus in buses:
                print(f"{bus[0]:^6} | {bus[1]} | {bus[2]}")
            
            bus_id = int(input("\nEnter Bus ID to delete: "))
            if delete_bus(bus_id):
                print("Bus deleted successfully!")
        
        elif choice == "9":
            print("\n--- Delete Driver ---")
            drivers = display_all_drivers()
            print("\nAvailable Drivers:")
            print("Driver Name | Phone Number")
            print("-" * 30)
            for driver in drivers:
                print(f"{driver[0]} | {driver[1]}")
            
            driver_name = input("\nEnter Driver Name to delete: ")
            if delete_driver(driver_name):
                print("Driver deleted successfully!")

        elif choice == "10":
            print("\n--- All Buses ---")
            buses = display_all_buses()
            print("BusID | Model | Year")
            print("-" * 30)
            for bus in buses:
                print(f"{bus[0]:^6} | {bus[1]} | {bus[2]}")
        

        elif choice == "11":
            print("\n--- Display Trip Stops ---")
            trips = display_all_trips()
            print("\nAvailable Trips:")
            print("TripNumber | Start Location | Destination")
            print("-" * 50)
            for trip in trips:
                print(f"{trip[0]:^10} | {trip[1]:^14} | {trip[2]}")
            
            trip_number = int(input("\nEnter Trip Number to see stops: "))
            stops = display_trip_stops(trip_number)
            
            if stops:
                print("\nStops for Trip", trip_number)
                print("Stop Number | Stop Address | Sequence | Driving Time (min)")
                print("-" * 70)
                for stop in stops:
                    print(f"{stop[1]:^11} | {stop[2]:<12} | {stop[3]:^8} | {stop[4]:^16}")
            else:
                print(f"No stops found for Trip {trip_number}")

        elif choice == "12":
            print("\n--- Display Driver's Weekly Schedule ---")
            drivers = display_all_drivers()
            print("\nAvailable Drivers:")
            print("Driver Name | Phone Number")
            print("-" * 30)
            for driver in drivers:
                print(f"{driver[0]} | {driver[1]}")
            
            driver_name = input("\nEnter Driver Name: ")
            start_date = input("Enter Start Date (YYYY-MM-DD): ")
            
            schedule = display_driver_weekly_schedule(driver_name, start_date)
            
            if schedule:
                print(f"\nWeekly Schedule for {driver_name} starting {start_date}")
                print("Trip # | From | To | Date | Start Time | Arrival Time")
                print("-" * 70)
                for trip in schedule:
                    print(f"{trip[0]:^6} | {trip[1]:<4} | {trip[2]:<2} | {trip[3]} | {trip[4]:^10} | {trip[5]:^11}")
            else:
                print(f"No schedule found for {driver_name} in the specified week")

     # Replace the problematic section in the main_menu() function with this corrected version:

        elif choice == "13":
            print("\n--- Record Actual Trip Data ---")
            # Show available trips first
            print("\nAvailable Trip Offerings:")
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute('''
                SELECT DISTINCT t.TripNumber, t.StartLocationName, t.DestinationName,
                       tr.Date, tr.ScheduledStartTime
                FROM Trip t
                JOIN TripOffering tr ON t.TripNumber = tr.TripNumber
            ''')
            trips = cursor.fetchall()
            print("Trip # | From | To | Date | Start Time")
            print("-" * 50)
            for trip in trips:
                print(f"{trip[0]:^6} | {trip[1]:<4} | {trip[2]:<2} | {trip[3]} | {trip[4]}")
            
            try:
                trip_number = int(input("\nEnter Trip Number: "))
                date = input("Enter Date (YYYY-MM-DD): ")
                scheduled_start = input("Enter Scheduled Start Time (HH:MM): ")
                
                if record_actual_trip_data(trip_number, date, scheduled_start):
                    print("\nActual trip data recorded successfully!")
                else:
                    print("\nFailed to record actual trip data.")
            except ValueError:
                print("Invalid input. Trip Number must be a number.")
            finally:
                connection.close()

        elif choice == "14":
            print("\n--- View Actual Trip Data ---")
            trip_number = int(input("Enter Trip Number: "))
            date = input("Enter Date (YYYY-MM-DD): ")
            scheduled_start = input("Enter Scheduled Start Time (HH:MM): ")
            
            actual_data = display_actual_trip_data(trip_number, date, scheduled_start)
            
            if actual_data:
                print("\nActual Trip Data:")
                print("Stop # | Stop Address | Scheduled | Actual Start | Actual Arrival | In | Out")
                print("-" * 80)
                for data in actual_data:
                    print(f"{data[0]:^7} | {data[1]:<12} | {data[2]:^9} | {data[3]:^12} | {data[4]:^14} | {data[5]:^3} | {data[6]:^3}")
            else:
                print("No actual trip data found for this trip offering.")

        elif choice == "0":
            print("\nGoodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    setup_database()
    main_menu()