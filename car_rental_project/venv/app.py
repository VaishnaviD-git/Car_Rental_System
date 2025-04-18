from flask import Flask, render_template, request, redirect, url_for, session, jsonify,flash # type: ignore
from flask_mysqldb import MySQL # type: ignore
from datetime import datetime # type: ignore

app = Flask(__name__)

# ✅ Add this line right here!
app.secret_key = '7yhuthu775hjhfh'  # Replace with any unique random string

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Vaishu&samu@05'
app.config['MYSQL_DB'] = 'car_rental'

mysql = MySQL(app)


@app.route('/')
def index():
    return render_template('layout.html')

#Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']  # 'owner' or 'customer'

        cur = mysql.connection.cursor()

        if role == 'owner':
            cur.execute("SELECT * FROM rentalshops WHERE Id = %s AND Code = %s", (username, password))
            owner = cur.fetchone()
            if owner:
                session['user'] = owner[0]  # This is owner ID
                session['role'] = 'owner'
                return render_template('owner.html')
            else:
                error = "Invalid owner credentials."

        elif role == 'customer':
            cur.execute("SELECT * FROM Customers WHERE AdhaarNo = %s AND DrivingLicense = %s", (username, password))
            customer = cur.fetchone()
            if customer:
                session['user'] = customer[0]  # This is customer ID
                session['role'] = 'customer'
                return redirect(url_for('customers'))
            else:
                error = "Invalid customer credentials."

    return render_template("login.html", error=error)

@app.route('/customers')
def customers():
    if 'user' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))

    cus_id = session['user']
    cursor = mysql.connection.cursor()

    # Get customer data
    cursor.execute("SELECT * FROM customers WHERE Id = %s", (cus_id,))
    customer = cursor.fetchone()

    # Get booked vehicle data with rental shop location
    cursor.execute("""
        SELECT v.NoPlate, v.Type, v.Model, v.Seats, r.Location 
        FROM vehicles v 
        JOIN rentalshops r ON v.RentalId = r.Id 
        WHERE v.Cus_id = %s
    """, (cus_id,))
    vehicles = cursor.fetchall()

    cursor.close()
    return render_template('customers.html', customer=customer, vehicles=vehicles)


#Logout Page
@app.route('/logout')
def logout():
    if 'user' not in session or session.get('role') != 'customer':
        flash("Please log in as a customer to view this page.", 'error')
        return redirect(url_for('login'))
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))

#Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        id = request.form.get('id')
        adhaar = request.form.get('adhaar')
        license = request.form.get('license')
        address = request.form.get('address')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Customers WHERE AdhaarNo = %s OR DrivingLicense = %s", (adhaar, license))
        existing = cur.fetchone()

        if existing:
            cur.close()
            return render_template('register.html', error="Aadhaar or License already exists.")

        cur.execute("""
            INSERT INTO Customers (Id, AdhaarNo, DrivingLicense, Address)
            VALUES (%s, %s, %s, %s)
        """, (id, adhaar, license, address))
        mysql.connection.commit()
        cur.close()

        # ✅ Redirect to login page
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/reservation', methods=['GET', 'POST'])
def reservation():
    # Only allow customers to reserve
    if 'user' not in session or session.get('role') != 'customer':
        flash("Please log in as a customer to make a reservation.", 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        customer_id = session['user']  # Get customer ID from session
        from_date = request.form['from_date']
        to_date = request.form['to_date']
        location = request.form['location']
        time_slot = request.form['time_slot']

        # Validate date logic
        if datetime.strptime(from_date, '%Y-%m-%d') >= datetime.strptime(to_date, '%Y-%m-%d'):
            flash("From Date must be less than To Date.", 'error')
            return redirect(url_for('reservation'))

        # Insert reservation
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO reservation (Cus_id, FromDate, ToDate, Location, TimeSlot)
            VALUES (%s, %s, %s, %s, %s)
        """, (customer_id, from_date, to_date, location, time_slot))
        mysql.connection.commit()
        cur.close()

        flash("Reservation successful!", 'success')
        return redirect(url_for('vehicles', location=location))

    return render_template('reservation.html')



@app.route('/vehicles', methods=['GET'])
def vehicles():
    location = request.args.get('location')
    if 'user' not in session or session.get('role') != 'customer':
        flash("Please log in as a customer to view this page.", 'error')
        return redirect(url_for('login'))
    # Get available vehicles based on location and check if they are booked
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT v.NoPlate, v.Type, v.Model, v.Seats, r.Name AS RentalName
        FROM vehicles v
        JOIN rentalshops r ON v.RentalId = r.Id
        WHERE r.Location = %s AND v.Cus_id IS NULL
    """, (location,))
    available_vehicles = cursor.fetchall()
    cursor.close()

    return render_template('vehicles.html', vehicles=available_vehicles, location=location)

@app.route('/book_vehicle/<vehicle_no>', methods=['GET'])
def book_vehicle(vehicle_no):
    if 'user' not in session or session.get('role') != 'customer':
        flash("You must be logged in as a customer to book a vehicle.", 'error')
        return redirect(url_for('login'))

    cus_id = session['user']  # Customer ID from session

    # Update the vehicle to assign it to the customer
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE vehicles SET Cus_id = %s WHERE NoPlate = %s", (cus_id, vehicle_no))
    mysql.connection.commit()
    cursor.close()

    # Redirect to "your_info" page after booking
    return redirect(url_for('customers'))  # Redirect to customers page
  # Redirect back to vehicles page

@app.route('/vehicle_info/<vehicle_no>', methods=['GET'])
def vehicle_info(vehicle_no):
    # Fetch vehicle details along with the rental shop information
    if 'user' not in session or session.get('role') != 'customer':
        flash("Please log in as a customer to view this page.", 'error')
        return redirect(url_for('login'))
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT v.NoPlate, v.Type, v.Model, v.Seats, r.Name AS RentalName, r.Location AS RentalLocation
        FROM vehicles v
        JOIN rentalshops r ON v.RentalId = r.Id
        WHERE v.NoPlate = %s
    """, (vehicle_no,))
    vehicle_info = cursor.fetchone()
    cursor.close()

    if vehicle_info:
        return render_template('vehicle_info.html', vehicle_info=vehicle_info)
    else:
        return "Vehicle not found", 404

@app.route('/edit_customer', methods=['GET', 'POST'])
def edit_customer():
    if 'user' not in session or session.get('role') != 'customer':
        flash("Please log in as a customer to view this page.", 'error')
        return redirect(url_for('login'))
    cus_id = session['user']
    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        adhaar_no = request.form['adhaar_no']
        license = request.form['license']
        address = request.form['address']

        cursor.execute("""
            UPDATE customers
            SET AdhaarNo = %s, DrivingLicense = %s, Address = %s
            WHERE Id = %s
        """, (adhaar_no, license, address, cus_id))
        mysql.connection.commit()
        cursor.execute("SELECT * FROM vehicles WHERE Cus_id = %s", (cus_id,))
        booked_vehicles = cursor.fetchall()
        cursor.execute("SELECT * FROM Customers WHERE Id = %s", (cus_id,))
        customer = cursor.fetchone()
        cursor.close()
        flash("Information updated successfully!", 'success')
        return render_template('customers.html', customer=customer, vehicles=booked_vehicles)

    # GET request: show current customer info
    cursor.execute("SELECT * FROM customers WHERE Id = %s", (cus_id,))
    customer = cursor.fetchone()
    cursor.close()

    return render_template('edit_customer.html', customer=customer)

@app.route('/instant_order', methods=['GET', 'POST'])
def instant_order():
    if 'user' not in session or session.get('role') != 'customer':
        flash("Please log in to place an instant order.", 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        location = request.form['location']
        time_slot = request.form['time_slot']
        cus_id = session['user']

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO instantorders (Cus_id, Location, TimeSlot)
            VALUES (%s, %s, %s)
        """, (cus_id, location, time_slot))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('vehicles', location=location))

    return render_template('instant_orders.html')

@app.route('/delete_booking/<vehicle_no>', methods=['POST'])
def delete_booking(vehicle_no):
    if 'user' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))

    cus_id = session['user']
    cursor = mysql.connection.cursor()

    # Only allow the logged-in customer to delete their own bookings
    cursor.execute("UPDATE vehicles SET Cus_id = NULL WHERE NoPlate = %s AND Cus_id = %s", (vehicle_no, cus_id))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('customers'))

if __name__ == '__main__':
    app.run(debug=True)

