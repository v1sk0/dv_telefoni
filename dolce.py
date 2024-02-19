from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import jsonify  # Import jsonify from the flask module
from sqlalchemy import func
from sqlalchemy import Column, Integer, String
from flask import request
import os
import configparser
from configparser import ConfigParser

app = Flask(__name__)

# Load configuration from config.ini file
config = ConfigParser()
config.read('config.ini')

# Definise tekst za Print ticket klauzolu
app.config['COMMENT_CLAUSE'] = 'TEST KLAUZOLA ZA PRINT.'
app.config['IME_KOMPANIJE'] = 'Your company name'
app.config['ADRESA'] = 'Your company address'
app.config['PIB'] = '123456789'  # Example PIB (9 numbers)
app.config['MATICNI_BROJ'] = '12345678'  # Example Maticni broj (8 digits)
app.config['SIFRA_DELATNOSTI'] = '123456'  # Example Šifra delatnosti (up to 6 digits)
app.config['OBAVEZNIK_PDV'] = True  # Example Obaveznik PDV: Da (True) or Ne (False)
app.config['BROJ_TELEFONA'] = '+1234567890'  # Example phone number
app.config['MAIL'] = 'example@example.com'  # Example email
app.config['POSLOVNA_BANKA'] = 'Bank name - account number'  # Example Poslovna Banka


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
    purchase_timestamp = db.Column(db.DateTime, default=datetime.now)   # Timestamp of purchase from the supplier
    sold = db.Column(db.Boolean, default=False)  # Flag to indicate if the phone has been sold
    sale_timestamp = db.Column(db.DateTime(timezone=True))  # Timestamp of sale to customer (with timezone)
    turnover_time = db.Column(db.Interval)  # Time interval to sell the phone after purchase
    collected = db.Column(db.Boolean, default=False)  # Flag to indicate if the payment has been collected


class SparePart(db.Model):
    """
    Represents a spare part listing in the database.
    """
    id = db.Column(db.Integer, primary_key=True)
    purchase_timestamp = db.Column(db.DateTime, default=datetime.now)   # Timestamp of purchase from the supplier
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
    purchase_timestamp = db.Column(db.DateTime, default=datetime.now)  # Timestamp of the spare part purchase
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
    purchase_timestamp = db.Column(db.DateTime, default=datetime.now)   # Timestamp of Open Ticket
    service_ticket_nr = Column(Integer, unique=True, nullable=False)  # Use Integer type
    date = db.Column(db.Date, default=datetime.now)   # Date the service ticket was created
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
    closed_timestamp = db.Column(db.DateTime(timezone=True))  # Timestamp when the ticket was closed
    collected_timestamp = db.Column(db.DateTime(timezone=True))  # Timestamp when the ticket was collected
    owner_collect = db.Column(db.String(255))  # Owner who collected the ticket
    owner_collect_timestamp = db.Column(db.DateTime(timezone=True))  # Timestamp when the ticket was collected by the owner
    sms_notification_completed = db.Column(db.Boolean, default=False)  # SMS notification for completion
    sms_notification_10_days = db.Column(db.Boolean, default=False)  # SMS notification for 10 days
    sms_notification_30_days = db.Column(db.Boolean, default=False)  # SMS notification for 30 days
    complete_duration = db.Column(db.Integer) # Duration of the service ticket completion
    
    
class ComputerListing(db.Model):
    """
    Represents a computer listing in the database.
    """
    id = db.Column(db.Integer, primary_key=True)
    purchase_timestamp = db.Column(db.DateTime, default=datetime.now)   # Timestamp of purchase from the supplier
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
    purchase_timestamp = db.Column(db.DateTime, default=datetime.now)   # Timestamp of purchase from supplier
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

# definise funkciju za prikazivanje sledeceg racuna
def get_next_ticket_number():
    latest_ticket = db.session.query(func.max(ServiceTicket.service_ticket_nr)).scalar()
    
    if latest_ticket is not None:
        return latest_ticket + 1
    else:
        return 0  # Start from 0 if no tickets exist yet
    
    
# Ucivatvanje konfiguracije iz config.ini fajla
def load_config_from_ini():
    config = configparser.ConfigParser()
    config_file_path = os.path.join(app.root_path, 'config.ini')
    config.read(config_file_path)

    if 'COMPANY' in config:
        app.config['IME_KOMPANIJE'] = config['COMPANY'].get('ime_kompanije', 'Your company name')
        app.config['ADRESA'] = config['COMPANY'].get('adresa', 'Your company address')
        app.config['PIB'] = config['COMPANY'].get('pib', '123456789')
        app.config['MATICNI_BROJ'] = config['COMPANY'].get('maticni_broj', '12345678')
        app.config['SIFRA_DELATNOSTI'] = config['COMPANY'].get('sifra_delatnosti', '123456')
        app.config['OBAVEZNIK_PDV'] = config['COMPANY'].getboolean('obaveznik_pdv', True)
        app.config['BROJ_TELEFONA'] = config['COMPANY'].get('broj_telefona', '+1234567890')
        app.config['MAIL'] = config['COMPANY'].get('mail', 'example@example.com')
        app.config['POSLOVNA_BANKA'] = config['COMPANY'].get('poslovna_banka', 'Bank name - account number')
    
    if 'KLAUZOLA' in config:    
        app.config['COMMENT_CLAUSE'] = config['KLAUZOLA'].get('comment_clause', 'DODAJ KLAUZOLU ZA PRINT.')
load_config_from_ini()


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

# get closed collected tickets
def get_closed_collected_tickets():
    try:
        # Query the database to get closed service tickets with collected status = 1
        closed_collected_tickets = ServiceTicket.query.filter_by(ticket_status='Closed', collected=1).all()
        return closed_collected_tickets
    except Exception as e:
        # Handle any exceptions or errors that may occur during the database query
        print(f"Error while fetching closed collected tickets: {str(e)}")
        return []


# definise funkciju za brojanje neprodatih telefona
def count_unsold_phones():
    # Perform a query to count unsold phones
    unsold_phone_count = PhoneListing.query.filter_by(sold=0).count()
    return unsold_phone_count

# definise funkciju za sumiranje prodajne cene za neprodate telefone
def sum_sales_price_for_unsold_phones():
    # Perform a query to sum sales_price for phones with sold status equal to 0
    Phone_on_stock_sales_price = db.session.query(db.func.sum(PhoneListing.sales_price)).filter(PhoneListing.sold == 0).scalar()
    return Phone_on_stock_sales_price or 0  # If there are no unsold phones, return 0

# definise funkciju za brojanje zatvorenih naloga nenaplacenih iz baze
def count_closed_tickets_not_collected():
    # Perform a query to count tickets with closed status and collected = 0
    ticket_count = db.session.query(ServiceTicket).filter(ServiceTicket.ticket_status == 'Closed', ServiceTicket.collected == 0).count()
    return ticket_count

# Additional database operations or functions can be defined here









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
    
    return render_template('setup_form.html', technicians=technicians, service_locations=service_locations, app=app)


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


@app.route('/update_config', methods=['POST'])
def update_config():
    # Get the form data
    ime_kompanije = request.form.get('ime_kompanije')
    adresa = request.form.get('adresa')
    pib = request.form.get('pib')
    maticni_broj = request.form.get('maticni_broj')
    sifra_delatnosti = request.form.get('sifra_delatnosti')
    obaveznik_pdv = request.form.get('obaveznik_pdv')
    broj_telefona = request.form.get('broj_telefona')
    mail = request.form.get('mail')
    poslovna_banka = request.form.get('poslovna_banka')
    
    # Retrieve the comment clause from the form data
    comment_clause = request.form.get('comment_clause')

    # Convert obaveznik_pdv to boolean
    obaveznik_pdv = obaveznik_pdv == 'True'

    # Update app.config properties
    app.config['IME_KOMPANIJE'] = ime_kompanije
    app.config['ADRESA'] = adresa
    app.config['PIB'] = pib
    app.config['MATICNI_BROJ'] = maticni_broj
    app.config['SIFRA_DELATNOSTI'] = sifra_delatnosti
    app.config['OBAVEZNIK_PDV'] = obaveznik_pdv
    app.config['BROJ_TELEFONA'] = broj_telefona
    app.config['MAIL'] = mail
    app.config['POSLOVNA_BANKA'] = poslovna_banka
    # Update the COMMENT_CLAUSE property
    app.config['COMMENT_CLAUSE'] = comment_clause

    # Save changes to the configuration file
    config = configparser.ConfigParser()
    config['COMPANY'] = {
        'ime_kompanije': str(ime_kompanije),
        'adresa': str(adresa),
        'pib': str(pib),
        'maticni_broj': str(maticni_broj),
        'sifra_delatnosti': str(sifra_delatnosti),
        'obaveznik_pdv': str(obaveznik_pdv),
        'broj_telefona': str(broj_telefona),
        'mail': str(mail),
        'poslovna_banka': str(poslovna_banka)
    }
    config['KLAUZOLA'] = {
        'comment_clause': str(comment_clause)
    }
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
        
    # Reload configuration
    app.config.update(request.form)

    # Redirect to the setup form or any other page
    return redirect(url_for('setup_form'))

# Tabela servisnih naloga (Service tickets)
@app.route('/service_tickets')
def service_tickets():
    technicians = Technician.query.all()
    service_tickets = ServiceTicket.query.all()
    service_locations = ServiceLocation.query.all()

    open_tickets_count = 0  # Initialize the counter for open tickets
    closed_not_collected_tickets_count = 0  # Initialize the counter for closed, not collected tickets
    open_tickets_sales_sum = 0  # Initialize the sum of sales_price for open tickets
    closed_tickets_sales_sum = 0  # Initialize the sum of sales_price for closed tickets
    closed_collected_tickets_sales_sum = 0  # Initialize the sum of sales_price for closed, collected tickets

    # Calculate and update the "Open Duration" for each active service ticket
    for ticket in service_tickets:
        if ticket.ticket_status == 'Open':
            current_time = datetime.now()
            time_difference = current_time - ticket.purchase_timestamp
            days = time_difference.days
            seconds = time_difference.seconds
            hours, remainder = divmod(seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            ticket.open_duration = f"{days} days, {hours} hours, {minutes} minutes"
            open_tickets_count += 1  # Increment the counter for open tickets
            open_tickets_sales_sum += ticket.sales_price  # Add the sales_price to the sum
        elif ticket.ticket_status == 'Closed':
            if ticket.collected == 0:
                closed_not_collected_tickets_count += 1  # Increment the counter for closed, not collected tickets
                closed_tickets_sales_sum += ticket.sales_price  # Add the sales_price to the sum for closed tickets
            else:
                closed_collected_tickets_sales_sum += ticket.sales_price  # Add the sales_price to the sum for closed, collected tickets

    return render_template('service_tickets.html', service_tickets=service_tickets, technicians=technicians, service_locations=service_locations, open_tickets_count=open_tickets_count, closed_not_collected_tickets_count=closed_not_collected_tickets_count, open_tickets_sales_sum=open_tickets_sales_sum, closed_tickets_sales_sum=closed_tickets_sales_sum, closed_collected_tickets_sales_sum=closed_collected_tickets_sales_sum)



@app.route('/add_service_ticket', methods=['POST'])
def add_service_ticket():
    if request.method != 'POST':
        return redirect(url_for('service_tickets'))

    # Retrieve form data using request.form and create a new ServiceTicket object
    next_ticket_nr = get_next_ticket_number()  # Get the next ticket numFber

    customer_name = request.form['customer_name']
    customer_contact = request.form['customer_contact']
    customer_mail = request.form['customer_email']
    customer_company_name = request.form['customer_company_name']
    customer_pib = request.form['customer_pib']
    
    # Handle checkbox input for service_category
    service_section = request.form.get('service_category', '')

    brand = request.form['brand']
    model = request.form['model']
    imei = request.form['imei']
    comment = request.form['comment']
    ticket_status = request.form['ticket_status']
    sales_price = request.form['sales_price']
    priority = request.form['priority']
    assigned_technician_name = request.form['assigned_technician']
    attachments = request.form['attachments']
    service_location_id = request.form['service_location']

    # Get the current timestamp
    purchase_timestamp = datetime.now()

    # Create a new ServiceTicket object
    service_ticket = ServiceTicket(
        service_ticket_nr=next_ticket_nr,  # Set the next ticket number
        customer_name=customer_name,
        customer_contact=customer_contact,
        customer_mail=customer_mail,
        customer_company_name=customer_company_name,
        customer_pib=customer_pib,
        service_section=service_section,
        brand=brand,
        model=model,
        imei=imei,
        comment=comment,
        ticket_status=ticket_status,
        sales_price=sales_price,
        priority=priority,
        assigned_technician=assigned_technician_name,  # Store technician name instead of ID
        attachments=attachments,
        service_location=service_location_id,
        purchase_timestamp=purchase_timestamp,
       
    )

    # Add the service_ticket to the database and commit the transaction
    db.session.add(service_ticket)
    db.session.commit()

    flash('Service ticket added successfully', 'success')
    return redirect(url_for('service_tickets'))

# ruta za definisanje static foldera
@app.route('/static/<path:resource>')
def serveStaticResource(resource):
    return send_from_directory('static', resource)



# Tabela Racunara (Computer listings)
@app.route('/computer_listings')
def computer_listings():
    computer_listings = ComputerListing.query.all()
    return render_template('computer_listings.html', computer_listings=computer_listings)


# Phone listings "phone_list.html
@app.route('/phone_list')
def phone_list():
    phone_listings = PhoneListing.query.filter_by(sold=False).all()
    current_time = get_current_time()
    current_time_plus_one_hour = current_time + timedelta(hours=1) #dodaje 1 sat za nasu vremensku zonu
    unsold_phone_count = count_unsold_phones()  # Funkcija za brojanje neprodatih telefona
    suma_neprodatih_telefona = sum_sales_price_for_unsold_phones()
    
# Make purchase_timestamp offset-aware for each phone listing
    for phone in phone_listings:
        phone.purchase_timestamp = phone.purchase_timestamp.replace(tzinfo=timezone.utc)

    return render_template('phone_list.html', phone_listings=phone_listings, current_time=current_time_plus_one_hour, unsold_phone_count=unsold_phone_count ,suma_neprodatih_telefona=suma_neprodatih_telefona)

@app.route('/')
def index():
    open_tickets_count_sum = (ServiceTicket.query.filter_by(ticket_status='Open').count())
    unsold_phone_count = count_unsold_phones()  # Funkcija za brojanje neprodatih telefona
    closed_tickets_uncollected_count = count_closed_tickets_not_collected()
    
    return render_template('index.html', unsold_phone_count=unsold_phone_count , open_tickets_count_sum=open_tickets_count_sum , closed_tickets_uncollected_count=closed_tickets_uncollected_count , ime_kompanije=config['COMPANY']['ime_kompanije']) 

@app.route('/forms')
def forms():
    return render_template('forms.html')

@app.route('/tables')
def tables():
    return render_template('tables.html')

    

# Kalkulator statistike za prodate telefone danas / ovu nedelju / ovaj mesec
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


# service tickets

 # Update the status of a service ticket
@app.route('/update_ticket_status/<int:ticket_id>', methods=['PUT'])
def update_ticket_status(ticket_id):
    new_status = request.json.get('newStatus')
    ticket = ServiceTicket.query.get(ticket_id)

    if not ticket:
        return jsonify({'success': False, 'message': 'Ticket not found'}), 404

    if ticket.ticket_status != new_status:
        ticket.ticket_status = new_status

        if new_status == 'Closed':
            # Set the closed timestamp
            ticket.closed_timestamp = datetime.now()

            # Calculate the complete duration in seconds
            complete_duration = (ticket.closed_timestamp - ticket.purchase_timestamp).total_seconds()

            # Store the complete duration in seconds
            ticket.complete_duration = complete_duration

    db.session.commit()

    return jsonify({'success': True}), 200

@app.route('/collect_ticket/<int:ticket_id>', methods=['PUT'])
def collect_ticket(ticket_id):
    try:
        # Get the final price from the request payload
        data = request.json
        final_price = data.get('finalPrice')

        # Update the ticket status, final price, and collected timestamp in the database
        ticket = ServiceTicket.query.get(ticket_id)
        if ticket:
            # Preserve the existing final price if not provided in the request payload
            if final_price is not None:
                ticket.sales_price = final_price
            
            ticket.collected = True  # Assuming 'collected' is a boolean field
            ticket.collected_timestamp = datetime.now()

            # Commit the changes to the database
            db.session.commit()

            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Define a route to display the closed_service_tickets.html template
@app.route('/closed_service_tickets')
def closed_service_tickets():
    # Query the database to get closed service tickets with collected status = 1
    closed_tickets = get_closed_collected_tickets()  # Implement this function based on your database model

    closed_collected_tickets = ServiceTicket.query.filter(
        ServiceTicket.ticket_status=='Closed', 
        ServiceTicket.collected==1, 
        ServiceTicket.owner_collect.is_(None)
    ).all()
    closed_collected_tickets_sales_sum = sum(ticket.sales_price for ticket in closed_collected_tickets)

    return render_template('closed_service_tickets.html', closed_tickets=closed_tickets, closed_collected_tickets_sales_sum=closed_collected_tickets_sales_sum)

# Print ticket
@app.route('/print_ticket/<int:ticket_id>')
def print_ticket(ticket_id):
    # Query ticket details from the database based on ticket_id
    ticket = ServiceTicket.query.get(ticket_id)  # Assuming Ticket is your SQLAlchemy model for tickets

    if ticket:
        # Pass the ticket and app object to the template context
        return render_template('printable_ticket.html', ticket=ticket, app=app)
    else:
        # Handle case where ticket with given ID is not found
        flash('Ticket not found.', 'error')
        return redirect(url_for('service_tickets'))
    
@app.route('/update_comment_clause', methods=['POST'])
def update_comment_clause():
    new_comment_clause = request.form['comment_clause']
    app.config['DEFAULT_COMMENT_CLAUSE'] = new_comment_clause

    # Save the updated comment clause text to a config INI file
    config = configparser.ConfigParser()
    config.read('config.ini')  # Replace with the path to your config INI file
    if 'KLAUZOLA' not in config.sections():
        config.add_section('KLAUZOLA')
    config.set('KLAUZOLA', 'comment_clause', new_comment_clause)
    with open('config.ini', 'w') as configfile:  # Replace with the path to your config INI file
        config.write(configfile)

    return redirect(url_for('setup_form'))


# Define a route to display the closed_service_tickets.html template    
@app.route('/reject_ticket/<int:ticket_id>', methods=['PUT'])
def reject_ticket(ticket_id):
    # Get the comment from the request
    comment = request.json.get('comment')

    # Update the ticket status to "rejected" and add a closed timestamp
    ticket = ServiceTicket.query.get(ticket_id)
    if ticket:
        ticket.ticket_status = 'Rejected'
        ticket.closed_timestamp = datetime.now()
        ticket.ticket_notes = comment  # Assuming ticket_notes is the field to store comments
        db.session.commit()
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False, 'message': 'Ticket not found'}), 404


@app.route('/owner_collect_ticket/<int:ticket_id>', methods=['PUT'])
def owner_collect_ticket(ticket_id):
    # Get the sales price from the request payload
    data = request.get_json()
    sales_price = data.get('salesPrice')

    # Update the database with owner collect information
    ticket = ServiceTicket.query.get(ticket_id)
    if ticket:
        ticket.owner_collect = 1
        ticket.owner_collect_timestamp = datetime.now()  # Fetch local time from PC

        # Optionally, update the sales price as well
        ticket.sales_price = sales_price

        # Commit the changes to the database
        db.session.commit()

        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Ticket not found'}), 404

  # Define route for rendering base_layout.html
@app.route('/base_layout')
def base_layout():
    return render_template('base_layout.html', ime_kompanije=config['COMPANY']['ime_kompanije'])

  # Define route for rendering test.html
@app.route('/test')
def test():
    return render_template('test.html', ime_kompanije=config['COMPANY']['ime_kompanije'])


if __name__ == '__main__':
    app.run(debug=True)
