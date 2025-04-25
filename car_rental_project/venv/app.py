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
                session['role'] = 'rental_shop'
                return redirect('rental_shops')
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

@app.route('/rental_shops')
def rental_shops():
    if 'user' not in session or session.get('role') != 'rental_shop':
        return redirect(url_for('login'))
    return render_template('rental_shop.html')

@app.route('/customers')
def customers():
    if 'user' not in session or session.get('role') != 'customer':
        flash("Login as a customer to view your dashboard.", 'error')
        return redirect(url_for('login'))

    cus_id = session['user']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM customers WHERE Id = %s", (cus_id,))
    customer = cursor.fetchone()

    cursor.execute("""
        SELECT Re_id, Location, FromDate, ToDate, TimeSlot, VehicleNo 
        FROM reservation WHERE Cus_id = %s
    """, (cus_id,))
    reservations = cursor.fetchall()

    cursor.execute("""
        SELECT Ord_id, Location, TimeSlot, VehicleNo 
        FROM instantorders WHERE Cus_id = %s
    """, (cus_id,))
    instant_orders = cursor.fetchall()
    cursor.close()

    return render_template('customers.html', customer=customer,
                           reservations=reservations,
                           instant_orders=instant_orders)



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
        name = request.form.get('name')
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
            INSERT INTO Customers (Id, Name, AdhaarNo, DrivingLicense, Address)
            VALUES (%s, %s, %s, %s, %s)
        """, (id, name, adhaar, license, address))
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

    cus_id = session['user']
    cursor = mysql.connection.cursor()

    # Check if customer has a reservation without vehicle
    cursor.execute("""
        SELECT Re_id FROM reservation 
        WHERE Cus_id = %s AND VehicleNo IS NULL 
        ORDER BY Re_id DESC LIMIT 1
    """, (cus_id,))
    res = cursor.fetchone()

    if res:
        cursor.execute("UPDATE reservation SET VehicleNo = %s WHERE Re_id = %s", (vehicle_no, res[0]))
        cursor.execute("UPDATE vehicles SET Cus_id = %s where NoPlate = %s",(cus_id, vehicle_no))
    else:
        # If no reservation, check for pending instant order
        cursor.execute("""
            SELECT Ord_id FROM instantorders 
            WHERE Cus_id = %s AND VehicleNo IS NULL 
            ORDER BY Ord_id DESC LIMIT 1
        """, (cus_id,))
        order = cursor.fetchone()
        if order:
            cursor.execute("UPDATE instantorders SET VehicleNo = %s WHERE Ord_id = %s", (vehicle_no, order[0]))
            cursor.execute("UPDATE vehicles SET Cus_id = %s where NoPlate = %s",(cus_id, vehicle_no))
        else:
            cursor.close()
            return redirect(url_for('customers'))

    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('customers'))


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
        name = request.form['name']
        adhaar_no = request.form['adhaar_no']
        license = request.form['license']
        address = request.form['address']

        cursor.execute("""
            UPDATE customers
            SET Name = %s, AdhaarNo = %s, DrivingLicense = %s, Address = %s
            WHERE Id = %s
        """, (name, adhaar_no, license, address, cus_id))
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

@app.route('/reservation/<int:res_id>')
def reservation_info(res_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM reservation WHERE Re_id = %s", (res_id,))
    data = cursor.fetchone()
    cursor.close()
    return render_template('reservation_info.html', data=data)

@app.route('/instant_order/<int:ord_id>')
def instant_order_info(ord_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM instantorders WHERE Ord_id = %s", (ord_id,))
    data = cursor.fetchone()
    cursor.close()
    return render_template('instant_order_info.html', data=data)

@app.route('/delete_reservation/<int:res_id>', methods=['POST'])
def delete_reservation(res_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM reservation WHERE Re_id = %s",(res_id,))
    vehicle_no = cursor.fetchone()
    cursor.execute("UPDATE vehicles SET Cus_id = NULL WHERE NoPlate = %s",(vehicle_no[6],))
    cursor.execute("DELETE FROM reservation WHERE Re_id = %s", (res_id,))
    mysql.connection.commit()
    cursor.close()
    flash("Reservation deleted.", 'success')
    return redirect(url_for('customers'))

@app.route('/delete_instant_order/<int:ord_id>', methods=['POST'])
def delete_instant_order(ord_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM instantorders WHERE Ord_id = %s",(ord_id,))
    vehicle_no = cursor.fetchone()
    cursor.execute("UPDATE vehicles SET Cus_id = NULL WHERE NoPlate = %s",(vehicle_no[4],))
    cursor.execute("DELETE FROM instantorders WHERE Ord_id = %s", (ord_id,))
    mysql.connection.commit()
    cursor.close()
    flash("Instant order deleted.", 'success')
    return redirect(url_for('customers'))

@app.route('/vehicle_info_customers/<vehicle_no>', methods=['GET'])
def vehicle_info_customers(vehicle_no):
    # Fetch vehicle details along with the rental shop information
    if 'user' not in session or session.get('role') != 'customer':
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
        return render_template('vehicle_info_customer.html', vehicle_info=vehicle_info)
    else:
        return "Vehicle not found", 404
    



@app.route('/vehicles_owner')
def vehicles_owner():
    if 'user' not in session or session.get('role') != 'rental_shop':
        return redirect(url_for('login'))

    shop_id = session['user']
    cursor = mysql.connection.cursor()
    
    query = """
        SELECT V.NoPlate, V.Type, V.Model, V.Seats, S.Name, S.Location
        FROM vehicles V
        JOIN rentalshops S ON V.RentalId = S.Id
        WHERE V.RentalId = %s
    """
    cursor.execute(query, (shop_id,))
    vehicles = cursor.fetchall()
    cursor.close()

    return render_template('vehicles_shop.html', vehicles=vehicles)

# DELETE vehicle
@app.route('/delete_vehicle/<number_plate>', methods=['POST'])
def delete_vehicle(number_plate):
    if 'user' not in session or session.get('role') != 'rental_shop':
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM vehicles WHERE NoPlate = %s AND RentalId = %s", (number_plate, session['user']))
    mysql.connection.commit()
    cursor.close()
    flash("Vehicle deleted successfully.", "success")
    return redirect(url_for('vehicles_owner'))


# EDIT vehicle form + update
@app.route('/edit_vehicle/<number_plate>', methods=['GET', 'POST'])
def edit_vehicle(number_plate):
    if 'user' not in session or session.get('role') != 'rental_shop':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    
    if request.method == 'POST':
        vtype = request.form['type']
        model = request.form['model']
        seats = request.form['seats']
        
        cursor.execute("""
            UPDATE vehicles 
            SET Type = %s, Model = %s, Seats = %s
            WHERE NoPlate = %s AND RentalId = %s
        """, (vtype, model, seats, number_plate, session['user']))
        
        mysql.connection.commit()
        cursor.close()
        flash("Vehicle updated successfully.", "success")
        return redirect(url_for('vehicles_owner'))
    
    # GET request: load vehicle data
    cursor.execute("""
        SELECT NoPlate, Type, Model, Seats 
        FROM vehicles 
        WHERE NoPlate = %s AND RentalId = %s
    """, (number_plate, session['user']))
    vehicle = cursor.fetchone()
    cursor.close()
    
    return render_template('edit_vehicle.html', vehicle=vehicle)

@app.route('/customers_owner')
def customers_owner():
    if 'user' not in session or session.get('role') != 'rental_shop':
        return redirect(url_for('login'))

    rental_id = session['user']
    cursor = mysql.connection.cursor()

    # Get customers from vehicles (Reservations)
    cursor.execute("""
        SELECT DISTINCT c.Id, c.Name, c.AdhaarNo, c.DrivingLicense, c.Address
        FROM customers c
        JOIN vehicles v ON c.Id = v.Cus_id
        WHERE v.RentalId = %s AND v.Cus_id IS NOT NULL
    """, (rental_id,))
    reservation_customers = cursor.fetchall()

    # Get customers from instantorders
    cursor.execute("""
        SELECT DISTINCT c.Id, c.Name, c.AdhaarNo, c.DrivingLicense, c.Address
        FROM customers c
        JOIN instantorders i ON c.Id = i.Cus_id
        WHERE i.Location = (
            SELECT Location FROM rentalshops WHERE Id = %s
        )
    """, (rental_id,))
    order_customers = cursor.fetchall()

    # Combine both sets without duplicates using IDs
    customer_dict = {}
    for customer in reservation_customers + order_customers:
        customer_dict[customer[0]] = customer  # key: Id

    customers = list(customer_dict.values())

    cursor.close()
    return render_template("customers_owner.html", customers=customers)

@app.route('/owner_edit', methods=['GET', 'POST'])
def owner_edit():
    if 'user' not in session or session.get('role') != 'rental_shop':
        return redirect(url_for('login'))

    rental_id = session['user']
    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        no_of_vehicles = request.form['no_of_vehicles']
        ratings = request.form['ratings']

        cursor.execute("""
            UPDATE rentalshops 
            SET Name = %s, Location = %s, No_Of_Vehicles = %s, Ratings = %s 
            WHERE Id = %s
        """, (name, location, no_of_vehicles, ratings, rental_id))
        mysql.connection.commit()
        return render_template('rental_shop.html')

    # GET: fetch existing data
    cursor.execute("SELECT Id, Name, Location, No_Of_Vehicles, Ratings FROM rentalshops WHERE Id = %s", (rental_id,))
    shop = cursor.fetchone()
    cursor.close()
    return render_template("owner_edit.html", shop=shop)



if __name__ == '__main__':
    app.run(debug=True)

