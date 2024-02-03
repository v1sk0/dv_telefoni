from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import jsonify  # Import jsonify from the flask module



app = Flask(__name__)

# Enable debug mode
app.debug = True

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dolcevita.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Constants for flash messages
SUCCESS_FLASH = 'success'
ERROR_FLASH = 'error'

# Define database models

class PhoneListing(db.Model):
    """
    Represents a phone listing in the database.
    """
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for a phone listing
    brand = db.Column(db.String(100))  # Brand of the phone, e.g., 'Apple', 'Samsung'
    model = db.Column(db.String(100))  # Model of the phone, e.g., 'iPhone 12'
    imei = db.Column(db.BigInteger)  # International Mobile Equipment Identity number
    color = db.Column(db.String(50))  # Color of the phone
    capacity = db.Column(db.String(50))  # Storage capacity of the phone
    condition = db.Column(db.String(10))  # Condition of the phone, e.g., 'New', 'Used'
    comment = db.Column(db.Text)  # Additional comments or notes about the phone
    purchase_price = db.Column(db.Float)  # Purchase price of the phone from the supplier
    sales_price = db.Column(db.Float)  # Selling price to the customer
    supplier_name = db.Column(db.String(100))  # Name of the supplier
    supplier_id_card = db.Column(db.String(50))  # ID card number of the supplier
    supplier_mobile = db.Column(db.String(15))  # Contact number of the supplier
    purchase_timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of purchase from the supplier
    sold = db.Column(db.Boolean, default=False)  # Flag to indicate if the phone has been sold
    sale_timestamp = db.Column(db.DateTime(timezone=True))  # Timestamp of sale to customer (with timezone)
    turnover_time = db.Column(db.Interval)  # Time interval to sell the phone after purchase
    collected = db.Column(db.Boolean, default=False)  # Flag to indicate if the payment has been collected


class SparePart(db.Model):
    """
    Represents a spare part listing in the database.
    """
    id = db.Column(db.Integer, primary_key=True)
    purchase_timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of purchase from the supplier
    service_section = db.Column(db.String(50), nullable=False)  # Section of service, e.g., 'Mobile', 'PC'
    brand = db.Column(db.String(100))  # Brand of the spare part
    model = db.Column(db.String(100))  # Model number or identifier of the spare part
    part_name = db.Column(db.String(100))  # Name of the spare part
    part_number = db.Column(db.String(50))  # Part number for inventory purposes
    part_category = db.Column(db.String(50))  # Category of the part, e.g., 'Display', 'Battery'
    picture = db.Column(db.String(200))  # Path or URL to an image of the spare part
    original_part = db.Column(db.Boolean, default=False)  # Whether the part is original or aftermarket
    comment = db.Column(db.Text)  # Additional comments or notes about the spare part
    quantity_in_stock = db.Column(db.Integer)  # Current stock quantity of the spare part
    purchase_price = db.Column(db.Float)  # Purchase price of the spare part
    sales_price = db.Column(db.Float)  # Recommended selling price of the spare part
    warehouse_location = db.Column(db.String(100))  # Storage location within the warehouse
    purchase_timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of the spare part purchase
    collected = db.Column(db.Boolean, default=False)  # Whether the payment has been collected after selling
    inventory_code = db.Column(db.String(50), unique=True)  # Unique code for inventory management
    barcode = db.Column(db.String(50), unique=True)  # Barcode of the spare part
    imei = db.Column(db.BigInteger)  # IMEI number, if applicable
    condition = db.Column(db.String(10))  # Condition of the spare part, e.g., 'New', 'Used'
    sold = db.Column(db.Boolean, default=False)  # Whether the spare part has been sold
    sale_timestamp = db.Column(db.DateTime)  # Timestamp when the spare part was sold

class ServiceTicket(db.Model):
    """
    Represents a service ticket in the database.
    """
    id = db.Column(db.Integer, primary_key=True)
    purchase_timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of Open Ticket
    service_ticket_nr = db.Column(db.String(20), unique=True, nullable=False)  # Unique service ticket number
    date = db.Column(db.Date, default=datetime.utcnow)  # Date the service ticket was created
    customer_name = db.Column(db.String(100), nullable=False)  # Name of the customer
    customer_contact = db.Column(db.String(20))  # Contact details of the customer
    customer_mail = db.Column(db.String(100))  # Email address of the customer
    customer_company_name = db.Column(db.String(100))  # Name of the customer's company
    customer_pib = db.Column(db.String(15))  # Tax identification number of the customer's company
    service_section = db.Column(db.String(50), nullable=False)  # Section of service, e.g., 'Hardware', 'Software'
    brand = db.Column(db.String(50))  # Brand of the item being serviced
    model = db.Column(db.String(50))  # Model of the item being serviced
    imei = db.Column(db.BigInteger)  # IMEI number if the serviced item is a mobile device
    comment = db.Column(db.Text)  # Additional comments or notes about the service ticket
    ticket_status = db.Column(db.String(20), default='On hold')  # Current status of the ticket, e.g., 'Pending', 'Completed'
    sales_price = db.Column(db.Float)  # The price of the service
    priority = db.Column(db.String(20))  # Priority level of the ticket, e.g., 'High', 'Medium', 'Low'
    assigned_technician = db.Column(db.String(100))  # Technician assigned to the service ticket
    resolution_details = db.Column(db.Text)  # Details of the resolution of the service ticket
    parent_ticket_id = db.Column(db.Integer, db.ForeignKey('service_ticket.id'))  # Service history associated with the ticket
    attachments = db.Column(db.String(200))  # File paths or URLs to attachments related to the service
    billing_status = db.Column(db.String(20))  # Billing status, e.g., 'Unbilled', 'Billed'
    invoice_number = db.Column(db.String(20))  # Invoice number related to the service
    service_location = db.Column(db.String(100))  # Location where the service was provided
    notification_preference = db.Column(db.String(20))  # Preferred method of notification, e.g., 'Email', 'SMS'
    ticket_notes = db.Column(db.Text)  # Notes or additional information about the service ticket
    collected = db.Column(db.Boolean, default=False)  # Whether the payment has been collected after selling

class ComputerListing(db.Model):
    """
    Represents a computer listing in the database.
    """
    id = db.Column(db.Integer, primary_key=True)
    purchase_timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of purchase from the supplier
    type = db.Column(db.String(20))  # Type of computer, values like 'Laptop' or 'PC'
    brand = db.Column(db.String(100))  # Brand of the computer, e.g., 'Dell', 'HP'
    model = db.Column(db.String(100))  # Specific model of the computer, e.g., 'XPS 15', 'Pavilion 15'
    cpu_brand = db.Column(db.String(100))  # CPU brand, e.g., 'Intel', 'AMD'
    cpu_model = db.Column(db.String(100))  # CPU model, e.g., 'Core i7', 'Ryzen 7'
    capacity = db.Column(db.String(50))  # Memory capacity, e.g., '16GB', '32GB'
    hdd = db.Column(db.String(100))  # Hard drive capacity, e.g., '512GB', '1TB'
    hdd_type = db.Column(db.String(50))  # Hard drive type, e.g., 'SSD', 'HDD'
    graphics_card_model = db.Column(db.String(100))  # Graphics card model, e.g., 'NVIDIA GTX 1650'
    screen_size = db.Column(db.String(50))  # Screen size, e.g., '15.6 inches', '27 inches'
    screen_type = db.Column(db.String(50))  # Screen type, e.g., 'LCD', 'LED'
    condition = db.Column(db.String(10))  # Condition of the computer, e.g., 'New', 'Used'
    comment = db.Column(db.Text)  # Additional comments or notes about the computer listing
    purchase_price = db.Column(db.Float)  # Purchase price of the computer from the supplier
    sales_price = db.Column(db.Float)  # Selling price to the customer
    supplier_name = db.Column(db.String(100))  # Name of the supplier
    supplier_id_card = db.Column(db.String(50))  # ID card number of the supplier
    supplier_mobile = db.Column(db.String(15))  # Contact number of the supplier
    purchase_timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of purchase from supplier
    sold = db.Column(db.Boolean, default=False)  # Flag to indicate if the computer has been sold
    sale_timestamp = db.Column(db.DateTime)  # Timestamp of sale to customer
    turnover_time = db.Column(db.Interval)  # Time interval to sell the computer after purchase
    collected = db.Column(db.Boolean, default=False)  # Flag to indicate if the payment has been collected

# tehnicari (Technicians)baza
class Technician(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100))
    # Add more fields as needed

    def __init__(self, name, specialization):
        self.name = name
        self.specialization = specialization
        # Initialize other fields as needed


# Servis Lokacije (Service Locations)
class ServiceLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255))
    contact_phone = db.Column(db.String(20))

    def __init__(self, name, address=None, contact_phone=None):
        self.name = name
        self.address = address
        self.contact_phone = contact_phone




# Helper function to get the current time with timezone
def get_current_time():
    return datetime.now(timezone.utc)

# Helper function to get the next ticket number
def get_next_ticket_number():
    # Query the database to get the highest ticket number
    highest_ticket = ServiceTicket.query.order_by(ServiceTicket.service_ticket_nr.desc()).first()
    
    # If there are no existing tickets, start with 1, otherwise increment the highest ticket number
    if highest_ticket is None:
        next_ticket_number = 1
    else:
        next_ticket_number = int(highest_ticket.service_ticket_nr) + 1

    return next_ticket_number

# Routes and views for the application


# Tehnicari (Technicians)
@app.route('/add_technician', methods=['GET', 'POST'])
def add_technician():
    if request.method == 'POST':
        name = request.form['name']
        specialization = request.form['specialization']

        technician = Technician(name=name, specialization=specialization)
        db.session.add(technician)
        db.session.commit()

        return redirect(url_for('setup_form'))

    return render_template('setup_form.html')
# Tabela Tehnicara (Technicians list)
@app.route('/list_technicians')
def list_technicians():
    technicians = Technician.query.all()
    return render_template('technician_list.html', technicians=technicians)


# Define a route for /setup_form
@app.route('/setup_form')
def setup_form():
    technicians = Technician.query.all()
    service_locations = ServiceLocation.query.all()  # Query the service locations
    
    return render_template('setup_form.html', technicians=technicians, service_locations=service_locations)


# Define a route for removing a technician
@app.route('/remove_technician/<int:technician_id>', methods=['POST'])
def remove_technician(technician_id):
    technician = Technician.query.get(technician_id)
    if technician:
        db.session.delete(technician)
        db.session.commit()
    return redirect(url_for('setup_form'))


# Define a route for /add_service_location
@app.route('/add_service_location', methods=['GET', 'POST'])
def add_service_location():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        contact_phone = request.form['contact_phone']

        service_location = ServiceLocation(name=name, address=address, contact_phone=contact_phone)
        db.session.add(service_location)
        db.session.commit()

        return redirect(url_for('setup_form'))

    return render_template('setup_form.html')

@app.route('/list_service_locations')
def list_service_locations():
    # Query all service locations from the database
    service_locations = ServiceLocation.query.all()

    # Create a list of dictionaries to represent service locations
    location_list = [{"id": location.id, "name": location.name, "address": location.address, "contact_phone": location.contact_phone} for location in service_locations]

    return jsonify({"success": True, "locations": location_list})
    
    # Render the template and pass the data to it
    return render_template('setup_form.html', service_locations=service_locations)
# Define a route for removing a service location
@app.route('/remove_service_location/<int:location_id>', methods=['POST'])
def remove_service_location(location_id):
    if request.method == 'POST':
        service_location = ServiceLocation.query.get(location_id)
        if service_location:
            db.session.delete(service_location)
            db.session.commit()
            return jsonify({'success': True})  # Return a JSON response upon successful removal
        else:
            return jsonify({'success': False, 'error': 'Location not found'})  # Return an error if the location was not found
    return redirect(url_for('list_service_locations'))




# Rezervni delovi (Spare parts)
@app.route('/spare_parts')
def spare_parts():
    spare_parts = SparePart.query.all()
    return render_template('spare_parts.html', spare_parts=spare_parts)




# Tabela servisnih naloga (Service tickets)
@app.route('/service_tickets')
def service_tickets():
    technicians = Technician.query.all()  # Retrieve the list of technicians from the database
    service_tickets = ServiceTicket.query.all()
    return render_template('service_tickets.html', service_tickets=service_tickets, technicians=technicians)


# Tabela Racunara (Computer listings)
@app.route('/computer_listings')
def computer_listings():
    computer_listings = ComputerListing.query.all()
    return render_template('computer_listings.html', computer_listings=computer_listings)


# Main page "index.html"
@app.route('/')
def index():
    phone_listings = PhoneListing.query.filter_by(sold=False).all()
    current_time = get_current_time()
    current_time_plus_one_hour = current_time + timedelta(hours=1) #dodaje 1 sat za nasu vremensku zonu

# Make purchase_timestamp offset-aware for each phone listing
    for phone in phone_listings:
        phone.purchase_timestamp = phone.purchase_timestamp.replace(tzinfo=timezone.utc)

    return render_template('index.html', phone_listings=phone_listings, current_time=current_time_plus_one_hour)





    

@app.route('/phones_on_stock')
def phones_on_stock():
    phone_listings = PhoneListing.query.filter_by(sold=False).all()
    current_time = get_current_time()
    current_time_plus_one_hour = current_time + timedelta(hours=1) #dodaje 1 sat za nasu vremensku zonu
    return render_template('phones_on_stock.html', phone_listings=phone_listings, current_time=current_time_plus_one_hour)


def calculate_statistics(time_frame):
    current_time = get_current_time()
    sold_phones = PhoneListing.query.filter_by(sold=True).all()

    if time_frame == 'today':
        start_time = current_time - timedelta(days=1)
    elif time_frame == 'this_week':
        start_time = current_time - timedelta(weeks=1)
    elif time_frame == 'this_month':
        start_time = current_time - timedelta(days=30)
    else:
        return None  # Invalid time frame

    # Convert start_time to an aware datetime
    start_time = start_time.replace(tzinfo=timezone.utc)

    # Make sure sale_timestamp is offset-aware for each sold phone
    for phone in sold_phones:
        if phone.sale_timestamp is not None:
            phone.sale_timestamp = phone.sale_timestamp.replace(tzinfo=timezone.utc)

    # Filter phones based on the comparison with start_time
    filtered_phones = [phone for phone in sold_phones if phone.sale_timestamp >= start_time]
    total_sales_count = len(filtered_phones)
    total_sales_sum = sum(phone.sales_price for phone in filtered_phones)

    # Calculate profit
    total_profit = sum(phone.sales_price - phone.purchase_price for phone in filtered_phones)

    return total_sales_count, total_sales_sum, total_profit

@app.route('/statistics')
def statistics():
    today_count, today_sum, today_profit = calculate_statistics('today')
    this_week_count, this_week_sum, this_week_profit = calculate_statistics('this_week')
    this_month_count, this_month_sum, this_month_profit = calculate_statistics('this_month')

    return render_template('statistics.html', today_count=today_count, today_sum=today_sum,
                           today_profit=today_profit, this_week_count=this_week_count,
                           this_week_sum=this_week_sum, this_week_profit=this_week_profit,
                           this_month_count=this_month_count, this_month_sum=this_month_sum,
                           this_month_profit=this_month_profit)


@app.route('/sell_phone/<int:id>', methods=['POST'])
def sell_phone(id):
    if request.method == 'POST':
        phone = PhoneListing.query.get(id)

        if phone:
            sale_price_str = request.form.get('price')

            if sale_price_str is not None:
                try:
                    sale_price = float(sale_price_str)
                    
                    # Set the sale timestamp to the current UTC time plus one hour
                    sale_timestamp = datetime.utcnow() + timedelta(hours=1)

                    # Calculate turnover time as the difference between sale_timestamp and purchase_timestamp
                    turnover_time = sale_timestamp - phone.purchase_timestamp

                    phone.sales_price = sale_price
                    phone.sale_timestamp = sale_timestamp
                    phone.sold = True
                    phone.turnover_time = turnover_time

                    db.session.commit()
                    flash(f'Sale recorded successfully at {sale_timestamp}', 'success')
                except ValueError:
                    flash('Invalid sale price format', 'error')
            else:
                flash('Sale price is missing', 'error')
        else:
            flash('Phone not found', 'error')

    return redirect(url_for('index'))



@app.route('/advanced_report')
def advanced_report():
    sold_phones = PhoneListing.query.filter_by(sold=True).all()

    today_count, today_sum, today_profit = calculate_statistics('today')
    this_week_count, this_week_sum, this_week_profit = calculate_statistics('this_week')
    this_month_count, this_month_sum, this_month_profit = calculate_statistics('this_month')



    return render_template('advanced_report.html', sold_phones=sold_phones ,  today_count=today_count, today_sum=today_sum,
                           today_profit=today_profit, this_week_count=this_week_count,
                           this_week_sum=this_week_sum, this_week_profit=this_week_profit,
                           this_month_count=this_month_count, this_month_sum=this_month_sum,
                           this_month_profit=this_month_profit)


@app.route('/sales_report')
def sales_report():
    sold_phones = PhoneListing.query.filter_by(sold=True).all()
    
    # Query the database to retrieve sold phones that are not collected
    sold_phones_not_collected = PhoneListing.query.filter_by(sold=True, collected=False).all()

    # Calculate the sum of sales_price for sold phones that are not collected
    total_sales_price_not_collected = sum(phone.sales_price for phone in sold_phones_not_collected)

    # Calculate the count of sold phones that are not collected
    count_sold_not_collected = len(sold_phones_not_collected)

    return render_template('sales_report.html', sold_phones=sold_phones ,sold_phones_not_collected=sold_phones_not_collected, total_sales_price_not_collected=total_sales_price_not_collected, count_sold_not_collected=count_sold_not_collected)





@app.route('/customers')
def customers():
    # Your code for the Customers page goes here
    return render_template('customers.html')  # You should create a 'customers.html' template

@app.route('/suppliers')
def suppliers():
    # Your code for the Suppliers page goes here
    return render_template('suppliers.html')  # You should create a 'suppliers.html' template

@app.route('/modify_purchase_price/<int:id>', methods=['POST'])
def modify_purchase_price(id):
    if request.method == 'POST':
        phone = PhoneListing.query.get(id)

        if phone:
            new_purchase_price_str = request.form.get('purchase_price')

            if new_purchase_price_str is not None:
                try:
                    new_purchase_price = float(new_purchase_price_str)
                    
                    # Update the purchase price of the phone
                    phone.purchase_price = new_purchase_price

                    db.session.commit()
                    flash('Purchase price modified successfully', 'success')
                except ValueError:
                    flash('Invalid purchase price format', 'error')
            else:
                flash('New purchase price is missing', 'error')
        else:
            flash('Phone not found', 'error')

    return redirect(url_for('advanced_report'))


@app.route('/collect_phone/<int:id>', methods=['POST'])
def collect_phone(id):
    if request.method == 'POST':
        phone = PhoneListing.query.get(id)

        if phone:
            # Set the 'collected' property to True when the "Collect" button is pressed
            phone.collected = True
            db.session.commit()
            flash(f'Phone collected: {phone.brand} {phone.model}', 'success')
        else:
            flash('Phone not found', 'error')

    return redirect(url_for('sales_report'))


@app.route('/add_listing', methods=['GET', 'POST'])
def add_listing():
    if request.method == 'POST':
        # Get data from the form
        brand = request.form.get('brand')
        model = request.form.get('model')
        imei = request.form.get('imei')
        color = request.form.get('color')
        capacity = request.form.get('capacity')
        condition = request.form.get('condition')
        comment = request.form.get('comment')
        purchase_price = request.form.get('purchase_price')
        sales_price = request.form.get('sales_price')
        supplier_name = request.form.get('supplier_name')
        supplier_id_card = request.form.get('supplier_id_card')
        supplier_mobile = request.form.get('supplier_mobile')
        
        # Get the current timestamp
        purchase_timestamp = datetime.now()

        # Create a new PhoneListing object and add it to your database
        new_listing = PhoneListing(
            brand=brand,
            model=model,
            imei=imei,
            color=color,
            capacity=capacity,
            condition=condition,
            comment=comment,
            purchase_price=purchase_price,
            sales_price=sales_price,
            supplier_name=supplier_name,
            supplier_id_card=supplier_id_card,
            supplier_mobile=supplier_mobile,
            purchase_timestamp=purchase_timestamp
        )

        db.session.add(new_listing)
        db.session.commit()

        # Redirect back to the index page after adding the phone listing
        return redirect(url_for('index'))

    return render_template('add_listing.html')  # Create this template for the add listing form

if __name__ == '__main__':
    app.run(debug=True)
