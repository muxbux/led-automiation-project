import mysql.connector

class OffSettings:
    def __init__(self, id, enableDarkMode, prioritizeRFID, prioritizeLAN, enableIndicators, brightness, darkModeStartTime, darkModeEndTime):
        self.id = id
        self.enableDarkMode = enableDarkMode
        self.prioritizeRFID = prioritizeRFID
        self.prioritizeLAN = prioritizeLAN
        self.enableIndicators = enableIndicators
        self.brightness = brightness
        self.darkModeStartTime = darkModeStartTime
        self.darkModeEndTime = darkModeEndTime



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
            cursor.execute("SELECT * FROM off_settings ORDER BY id DESC LIMIT 1")

            # Fetch the last record
            last_record = cursor.fetchone()

            if last_record:
                # Create an OffSettings object with the fetched data
                off_settings_obj = OffSettings(*last_record)
                return off_settings_obj
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


def get_last_off_settings_with_dark_mode():
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
            # Execute the SQL query to retrieve the last record with non-None darkModeStartTime and darkModeEndTime
            cursor.execute("SELECT * FROM off_settings WHERE darkModeStartTime IS NOT NULL AND darkModeEndTime IS NOT NULL ORDER BY id DESC LIMIT 1")

            # Fetch the last record that meets the criteria
            last_record = cursor.fetchone()

            if last_record:
                # Create an OffSettings object with the fetched data
                off_settings_obj = OffSettings(*last_record)
                return off_settings_obj
            else:
                return None  # No records found in the database that meet the criteria

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