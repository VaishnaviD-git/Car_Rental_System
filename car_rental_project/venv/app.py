from flask import Flask, request, jsonify # type: ignore
from flask_mysqldb import MySQL # type: ignore
from flask import render_template, request, redirect, url_for, session # type: ignore

app = Flask(__name__)

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
        role = request.form['role']

        cur = mysql.connection.cursor()

        if role == 'admin':
            cur.execute("SELECT * FROM Admins WHERE username = %s AND password = %s", (username, password))
            admin = cur.fetchone()
            if admin:
                session['user'] = admin[0]
                session['role'] = 'admin'
                cur.close()
                return redirect(url_for('view_rental_shops'))  # Admin dashboard
            else:
                error = "Invalid admin credentials"
        else:
            cur.execute("SELECT * FROM Customers WHERE AdhaarNo = %s AND DrivingLicense = %s", (username, password))
            customer = cur.fetchone()
            if customer:
                session['user'] = customer[0]
                session['role'] = 'customer'
                cur.close()
                return redirect(url_for('view_vehicles'))  # Customer dashboard
            else:
                error = "Invalid customer credentials"

        cur.close()

    return render_template("login.html", error=error)

#Logout Page
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

#Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        id = request.form.get('id')
        adhaar = request.form.get('adhaar')
        license = request.form.get('license')
        address = request.form.ge('address')
        current_address = request.form.get('current_address')

        cur = mysql.connection.cursor()

        # Check for duplicate Aadhaar or License
        cur.execute("SELECT * FROM Customers WHERE AdhaarNo = %s OR DrivingLicense = %s", (adhaar, license))
        existing = cur.fetchone()

        if existing:
            cur.close()
            return render_template('register.html', error="Aadhaar or License already exists.")

        cur.execute("""
            INSERT INTO Customers (Id, AdhaarNo, DrivingLicense, Adress, CurrentAddress)
            VALUES (%s, %s, %s, %s, %s)
        """, (id, adhaar, license, address, current_address))
        mysql.connection.commit()
        cur.close()

        return render_template('register.html', message="Registration successful!")
    
    return render_template('register.html')



#Customers Table
@app.route('/view/customers') # Get all customers
def get_customers():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Customers")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    customers = [dict(zip(columns, row)) for row in rows]
    cur.close()
    return render_template('customers.html', customers=customers)

#RentalShops Table
@app.route('/view/rental_shops') # Get all Rental Shops
def get_rental_shops():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM RentalShops")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    rentalshops = [dict(zip(columns, row)) for row in rows]
    cur.close()
    return render_template('rental_shops.html', rental_shops=rentalshops)

#Vehicles Table
@app.route('/view/vehicles') # Get all Vehicles
def get_vehicles():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Vehicles")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    vehicles = [dict(zip(columns, row)) for row in rows]
    cur.close()
    return render_template('vehicles.html', vehicles=vehicles)

#Reservations Table
@app.route('/view/reservations') # Get all Reservations
def get_reservations():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Reservation")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    reservations = [dict(zip(columns, row)) for row in rows]
    cur.close()
    return render_template('reservations.html', reservations=reservations)

#Instant Orders Table
@app.route('/view/instant_orders') # Get all Instant Orders
def get_instant_orders():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM InstantOrders")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    instant_orders = [dict(zip(columns, row)) for row in rows]
    cur.close()
    return render_template('instant_orders.html', instant_orders=instant_orders)

#Feedback Table
@app.route('/view/feedbacks') # Get all Feedbacks
def get_feedbacks():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Feedbacks")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    feedbacks = [dict(zip(columns, row)) for row in rows]
    cur.close()
    return render_template('feedbacks.html', feedbacks=feedbacks) 

# Subscriptions Table
@app.route('/view/subscriptions') # Get all Subscriptions
def get_subscriptions():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Subscriptions")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    subscriptions = [dict(zip(columns, row)) for row in rows]
    cur.close()
    return render_template('subscriptions.html', subscriptions=subscriptions)

# ExtraCharges Table
@app.route('/view/extra_charges') # Get all Extra Charges
def get_extra_charges():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM ExtraCharges")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    extra_charges = [dict(zip(columns, row)) for row in rows]
    cur.close()
    return render_template('extra_charges.html', extra_charges=extra_charges)

# Payments Table
@app.route('/view/payments') # Get all Payments
def get_payments():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Payments")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    payments = [dict(zip(columns, row)) for row in rows]
    cur.close()
    return render_template('payments.html', payments=payments)

if __name__ == '__main__':
    app.run(debug=True)

