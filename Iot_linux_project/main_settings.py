import mysql.connector
from datetime import datetime

class Main_settings:
    def __init__(self, id, mode, r_value, g_value, b_value, hue, timestamp, brightness):
        self.id = id
        self.mode = mode
        self.r_value = r_value
        self.g_value = g_value
        self.b_value = b_value
        self.hue = hue
        self.timestamp = timestamp
        self.brightness = brightness



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
            cursor.execute("SELECT * FROM main_settings ORDER BY id DESC LIMIT 1")

            # Fetch the last record
            last_record = cursor.fetchone()

            if last_record:
                # Create an Main_settings object with the fetched data
                main_settings = Main_settings(*last_record)
                return main_settings
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


def write_to_main_settings(main_settings):
    # Define your database connection parameters
    host = "localhost"
    user = "write"  # Replace with your MySQL username
    password = "write"  # Replace with your MySQL password
    database = "rgbdata"

    try:
        # Create a MySQL database connection
        conn = mysql.connector.connect(host=host, user=user, password=password, database=database)

        if conn.is_connected():
            # Create a cursor to interact with the database
            cursor = conn.cursor()

            # Define the SQL INSERT statement
            sql = "INSERT INTO main_settings (mode, r, g, b, hue, created_at, brightness) VALUES (%s, %s, %s,%s, %s, %s, %s)"

            # Tuple containing the values to insert
            values = (main_settings.mode, main_settings.r_value, main_settings.g_value, main_settings.b_value, main_settings.hue,datetime.now(), main_settings.brightness)

            # Execute the SQL INSERT statement
            cursor.execute(sql, values)

            # Commit the transaction
            conn.commit()

            # Close the cursor and the connection
            cursor.close()
            conn.close()

            print("Data written to main_settings successfully.")
            return True

    except mysql.connector.Error as err:
        print("Error:", err)
        return False

    return False