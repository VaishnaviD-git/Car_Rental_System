from flask import Flask, request, jsonify # type: ignore
from flask_mysqldb import MySQL # type: ignore

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Vaishu&samu@05'
app.config['MYSQL_DB'] = 'car_rental'

mysql = MySQL(app)

@app.route('/')
def home():
    return "Welcome to the Car Rental System"

#Customers Table
@app.route('/customers', methods=['POST'])
def add_customer():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO Customers (Id, AdhaarNo, DrivingLicense, Adress, CurrentAddress)
        VALUES (%s, %s, %s, %s, %s)
    """, (data['Id'], data['AdhaarNo'], data['DrivingLicense'], data['Adress'], data['CurrentAddress']))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Customer added successfully'})

@app.route('/customers', methods=['GET'])
def get_customers():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Customers")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    customers = [dict(zip(columns, row)) for row in rows]
    cur.close()
    return jsonify(customers)

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE Customers
        SET AdhaarNo = %s, DrivingLicense = %s, Adress = %s, CurrentAddress = %s
        WHERE Id = %s
    """, (data['AdhaarNo'], data['DrivingLicense'], data['Adress'], data['CurrentAddress'], id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Customer updated successfully'})

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Customers WHERE Id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Customer deleted successfully'})

@app.route('/customers/<int:id>', methods=['GET'])
def get_customer_by_id(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Customers WHERE Id = %s", (id,))
    row = cur.fetchone()
    columns = [desc[0] for desc in cur.description]
    customer = dict(zip(columns, row)) if row else None
    cur.close()
    return jsonify(customer)

#RentalShops Table
@app.route('/rental_shops', methods=['POST'])
def add_rental_shop():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO RentalShops (Id, Location, Ratings)
        VALUES (%s, %s, %s)
    """, (data['Id'], data['Location'], data['Ratings']))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Rental Shop added successfully'})

@app.route('/rental_shops', methods=['GET'])
def get_rental_shops():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM RentalShops")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    rentalshops = [dict(zip(columns, row)) for row in rows]
    cur.close()
    return jsonify(rentalshops)

@app.route('/rental_shops/<int:id>', methods=['PUT'])
def update_rental_shops(id):
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE RentalShops
        SET Location = %s, Ratings = %s
        WHERE Id = %s
    """, (data['Location'], data['Ratings'],id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Rental Shop updated successfully'})

@app.route('/rental_shops/<int:id>', methods=['DELETE'])
def delete_rental_shops(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM RentalShops WHERE Id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Rental Shop deleted successfully'})

@app.route('/rental_shops/<int:id>', methods=['GET'])
def get_rental_shop_by_id(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM RentalShops WHERE Id = %s", (id,))
    row = cur.fetchone()
    columns = [desc[0] for desc in cur.description]
    rentalshop = dict(zip(columns, row)) if row else None
    cur.close()
    return jsonify(rentalshop)

#Vehicles Table
@app.route('/vehicles', methods=['POST'])
def add_vehicle():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO Vehicles (NoPlate, Type, Model, RentalId)
        VALUES (%s, %s, %s, %s, %s)
    """, (data['NoPlate'], data['Type'], data['Model'], data['RentalId']))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Vehicle added successfully'})

@app.route('/vehicles', methods=['GET'])
def get_vehicles():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Vehicles")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    vehicles = [dict(zip(columns, row)) for row in rows]
    cur.close()
    return jsonify(vehicles)

@app.route('/vehicles/<string:no_plate>', methods=['PUT'])
def update_vehicle(no_plate):
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE Vehicles
        SET Type = %s, Model = %s, RentalId = %s
        WHERE NoPlate = %s
    """, (data['Type'], data['Model'], data['RentalId'], no_plate))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Vehicle updated successfully'})

@app.route('/vehicles/<string:no_plate>', methods=['DELETE'])
def delete_vehicle(no_plate):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Vehicles WHERE NoPlate = %s", (no_plate,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Vehicle deleted successfully'})

@app.route('/vehicles/<string:no_plate>', methods=['GET'])
def get_vehicle(no_plate):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Vehicles WHERE NoPlate = %s", (no_plate,))
    row = cur.fetchone()
    columns = [desc[0] for desc in cur.description]
    vehicle = dict(zip(columns, row)) if row else None
    cur.close()
    return jsonify(vehicle)

#Reservations Table
@app.route('/reservations', methods=['POST'])
def add_reservation():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
                INSERT INTO Reservation (Re_id, Cus_id, Location, TimeSlot, DateSlot, VehicleId)
                VALUES (%s, %s, %s, %s, %s)
                """, (data['Re_id'], data['Cus_id'], data['Location'], data['TimeSlot'], data['DateSlot'], data['VehicleId']))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Reservation added successfully'})

@app.route('/reservations', methods=['GET'])
def get_reservations():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Reservation")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    reservations = [dict(zip(columns, row)) for row in rows]
    cur.close()
    return jsonify(reservations)

@app.route('/reservations/<int:re_id>', methods=['PUT'])
def update_reservation(re_id):
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
                UPDATE Reservation
                SET Cus_id = %s, Location = %s, TimeSlot = %s, DateSlot = %s, VehicleId = %s
                WHERE Re_id = %s
                """, (data['Cus_id'], data['Location'], data['TimeSlot'], data['DateSlot'], data['VehicleId'], re_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Reservation updated successfully'})

@app.route('/reservations/<int:re_id>', methods=['DELETE'])
def delete_reservation(re_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Reservation WHERE Re_id = %s", (re_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Reservation deleted successfully'})

@app.route('/reservations/<int:re_id>', methods=['GET'])
def get_reservation_by_id(re_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Reservation WHERE Re_id = %s", (re_id,))
    row = cur.fetchone()
    columns = [desc[0] for desc in cur.description]
    reservation = dict(zip(columns, row)) if row else None
    cur.close()
    return jsonify(reservation)

#Instant Orders Table
@app.route('/instant_orders', methods=['POST'])
def add_instant_order():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO InstantOrders (Ord_id, Cus_id, Location, TimeSlot, VehicleId) VALUES (%s, %s, %s, %s, %s)", 
                (data['Ord_id'], data['Cus_id'], data['Location'], data['TimeSlot'], data['VehicleId']))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Instant Order added successfully'})

@app.route('/instant_orders', methods=['GET'])
def get_instant_orders():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM InstantOrders")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    instant_orders = [dict(zip(columns, row)) for row in rows]
    cur.close()
    return jsonify(instant_orders)

@app.route('/instant_orders/<int:ord_id>', methods=['PUT'])
def update_instant_order(ord_id):
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("UPDATE InstantOrders SET Cus_id = %s, Location = %s, TimeSlot = %s, VehicleId = %s WHERE Ord_id = %s", 
                (data['Cus_id'], data['Location'], data['TimeSlot'], data['VehicleId'], ord_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Instant Order updated successfully'})

@app.route('/instant_orders/<int:ord_id>', methods=['DELETE'])
def delete_instant_order(ord_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM InstantOrders WHERE Ord_id = %s", (ord_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Instant Order deleted successfully'})

@app.route('/instant_orders/<int:ord_id>', methods=['GET'])
def get_instant_order_by_id(ord_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM InstantOrders WHERE Ord_id = %s", (ord_id,))
    row = cur.fetchone()
    columns = [desc[0] for desc in cur.description]
    instant_order = dict(zip(columns, row)) if row else None
    cur.close()
    return jsonify(instant_order)

# Feedbacks Table
@app.route('/feedbacks', methods=['POST'])
def add_feedback():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
                INSERT INTO Feedbacks (Ord_id, Res_id, Info)
                VALUES (%s, %s, %s)
                """, (data['Ord_id'], data['Res_id'], data['Info']))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Feedback added successfully'})

@app.route('/feedbacks', methods=['GET'])
def get_feedbacks():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Feedbacks")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    feedbacks = [dict(zip(columns, row)) for row in rows]
    cur.close()
    return jsonify(feedbacks)

@app.route('/feedbacks/<int:ord_id>', methods=['PUT'])
def update_feedback(ord_id):
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
                UPDATE Feedbacks
                SET Res_id = %s, Info = %s
                WHERE Ord_id = %s
                """, (data['Res_id'], data['Info'], ord_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Feedback updated successfully'})

@app.route('/feedbacks/<int:ord_id>', methods=['DELETE'])
def delete_feedback(ord_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Feedbacks WHERE Ord_id = %s", (ord_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Feedback deleted successfully'})

@app.route('/feedbacks/<int:ord_id>', methods=['GET'])
def get_feedback_by_id(ord_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Feedbacks WHERE Ord_id = %s", (ord_id,))
    row = cur.fetchone()
    columns = [desc[0] for desc in cur.description]
    feedback = dict(zip(columns, row)) if row else None
    cur.close()
    return jsonify(feedback)


# Subscriptions Table
@app.route('/subscriptions', methods=['POST'])
def add_subscription():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
                INSERT INTO Subscriptions (Type, Benefits, Cus_id, Discounts)
                VALUES (%s, %s, %s, %s)
                """, (data['Type'], data['Benefits'], data['Cus_id'], data['Discounts']))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Subscription added successfully'})

@app.route('/subscriptions', methods=['GET'])
def get_subscriptions():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Subscriptions")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    subscriptions = [dict(zip(columns, row)) for row in rows]
    cur.close()
    return jsonify(subscriptions)

@app.route('/subscriptions/<int:sub_id>', methods=['PUT'])
def update_subscription(sub_id):
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
                UPDATE Subscriptions
                SET Type = %s, Benefits = %s, Cus_id = %s, Discounts = %s
                WHERE Sub_id = %s
                """, (data['Type'], data['Benefits'], data['Cus_id'], data['Discounts'], sub_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Subscription updated successfully'})

@app.route('/subscriptions/<int:sub_id>', methods=['DELETE'])
def delete_subscription(sub_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Subscriptions WHERE Sub_id = %s", (sub_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Subscription deleted successfully'})

@app.route('/subscriptions/<int:sub_id>', methods=['GET'])
def get_subscription_by_id(sub_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Subscriptions WHERE Sub_id = %s", (sub_id,))
    row = cur.fetchone()
    columns = [desc[0] for desc in cur.description]
    subscription = dict(zip(columns, row)) if row else None
    cur.close()
    return jsonify(subscription)

# ExtraCharges Table
@app.route('/extra_charges', methods=['POST'])
def add_extra_charge():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
                INSERT INTO ExtraCharges (Ord_id, Re_id, Amount, Reason)
                VALUES (%s, %s, %s, %s)
                """, (data['Ord_id'], data['Re_id'], data['Amount'], data['Reason']))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Extra charge added successfully'})

@app.route('/extra_charges', methods=['GET'])
def get_extra_charges():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM ExtraCharges")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    extra_charges = [dict(zip(columns, row)) for row in rows]
    cur.close()
    return jsonify(extra_charges)

@app.route('/extra_charges/<int:ord_id>', methods=['PUT'])
def update_extra_charge(ord_id):
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("UPDATE ExtraCharges SET Amount = %s, Reason = %s WHERE Ord_id = %s", 
                (data['Amount'], data['Reason'], ord_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Extra charge updated successfully'})

@app.route('/extra_charges/<int:ord_id>', methods=['DELETE'])
def delete_extra_charge(ord_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM ExtraCharges WHERE Ord_id = %s", (ord_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Extra charge deleted successfully'})

@app.route('/extra_charges/<int:ord_id>', methods=['GET'])
def get_extra_charge(ord_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM ExtraCharges WHERE Ord_id = %s", (ord_id,))
    row = cur.fetchone()
    if row:
        columns = [desc[0] for desc in cur.description]
        extra_charge = dict(zip(columns, row))
    else:
        extra_charge = None
    cur.close()
    return jsonify(extra_charge)

# Payments Table
@app.route('/payments', methods=['POST'])
def add_payment():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
                INSERT INTO Payments (TransactionId, Cus_id, Discounts, Extra)
                VALUES (%s, %s, %s, %s)
                """, (data['TransactionId'], data['Cus_id'], data['Discounts'], data['Extra']))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Payment added successfully'})

@app.route('/payments', methods=['GET'])
def get_payments():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Payments")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    payments = [dict(zip(columns, row)) for row in rows]
    cur.close()
    return jsonify(payments)

@app.route('/payments/<int:transaction_id>', methods=['PUT'])
def update_payment(transaction_id):
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
                UPDATE Payments
                SET Cus_id = %s, Discounts = %s, Extra = %s
                WHERE TransactionId = %s
                """, (data['Cus_id'], data['Discounts'], data['Extra'], transaction_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Payment updated successfully'})

@app.route('/payments/<int:transaction_id>', methods=['DELETE'])
def delete_payment(transaction_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Payments WHERE TransactionId = %s", (transaction_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Payment deleted successfully'})

@app.route('/payments/<int:transaction_id>', methods=['GET'])
def get_payment(transaction_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Payments WHERE TransactionId = %s", (transaction_id,))
    row = cur.fetchone()
    columns = [desc[0] for desc in cur.description]
    payment = dict(zip(columns, row)) if row else None
    cur.close()
    return jsonify(payment)

if __name__ == '__main__':
    app.run(debug=True)
