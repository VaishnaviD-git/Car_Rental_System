import pandas as pd
import mysql.connector # type: ignore

# Load Excel file
df = pd.read_excel("Vehicles Excel Sheet.xlsx")

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Vaishu&samu@05",
    database="car_rental"
)

cursor = conn.cursor()

# Insert each row
for index, row in df.iterrows():
    sql = "INSERT INTO Vehicles (NoPlate, Type, Model, Seats, RentalId) VALUES (%s, %s, %s, %s, %s)"
    # Adjust the SQL statement according to your table structure    
    cursor.execute(sql, tuple(row))

conn.commit()
cursor.close()
conn.close()

