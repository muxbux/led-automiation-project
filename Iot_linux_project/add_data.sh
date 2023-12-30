#!/bin/bash
echo "test";
# Database connection details
DB_HOST="localhost"
DB_USER="write"
DB_PASS="write"
DB_NAME="rgbdata"

# Generate random data
mode=$((RANDOM%2))
r=$((RANDOM%256))
g=$((RANDOM%256))
b=$((RANDOM%256))
hue=$((RANDOM%361))

# SQL query to insert data into the 'settings' table
SQL_QUERY="INSERT INTO settings (mode, r, g, b, hue) VALUES ('$mode', '$r', '$g', '$b', '$hue');"

# Execute the SQL query using the mysql command
mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "$SQL_QUERY"

# Check the exit status to see if the query was successful
if [ $? -eq 0 ]; then
    echo "Record added successfully."
else
    echo "Error: Failed to add record to the database."
fi
