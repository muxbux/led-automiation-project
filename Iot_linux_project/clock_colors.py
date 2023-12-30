import mysql.connector

class Clock_colors:
    def __init__(self, id, hue_seconds, hue_minutes, hue_hour, timestamp):
        self.id = id
        self.hue_seconds = hue_seconds
        self.hue_minutes = hue_minutes
        self.hue_hour = hue_hour
        self.timestamp = timestamp


def get_last_off_settings():
    # Define your database connection parameters
    host = "localhost"
    user = "write"  # Replace with your MySQL username
    password = "write"  # Replace with your MySQL password
    database = "rgbdata"

    # Create a MySQL database connection
    conn = mysql.connector.connect(host=host, user=user, password=password, database=database)

    if conn.is_connected():
        # Create a cursor to interact with the database
        cursor = conn.cursor()

        try:
            # Execute the SQL query to retrieve the last record
            cursor.execute("SELECT * FROM clock_colors ORDER BY id DESC LIMIT 1")

            # Fetch the last record
            last_record = cursor.fetchone()

            if last_record:
                clock_colors = Clock_colors(*last_record)
                return clock_colors
            else:
                return None  # No records found in the database

        except mysql.connector.Error as err:
            print("Error:", err)
            return None

        finally:
            # Close the cursor and the connection
            cursor.close()
            conn.close()

    else:
        print("Connection failed.")
        return None
