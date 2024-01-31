from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta, timezone


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
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    imei = db.Column(db.BigInteger)
    color = db.Column(db.String(50))
    capacity = db.Column(db.String(50))
    condition = db.Column(db.String(10))
    comment = db.Column(db.Text)
    purchase_price = db.Column(db.Float)
    sales_price = db.Column(db.Float)
    supplier_name = db.Column(db.String(100))
    supplier_id_card = db.Column(db.String(50))
    supplier_mobile = db.Column(db.String(15))
    purchase_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sold = db.Column(db.Boolean, default=False)  # Added to mark the phone as sold
    sale_timestamp = db.Column(db.DateTime(timezone=True))
    turnover_time = db.Column(db.Interval)
    collected = db.Column(db.Boolean, default=False)

def get_current_time():
    return datetime.now(timezone.utc)

@app.route('/')
def index():
    phone_listings = PhoneListing.query.filter_by(sold=False).all()
    current_time = get_current_time()
    current_time_plus_one_hour = current_time + timedelta(hours=1) #dodaje 1 sat za nasu vremensku zonu

# Make purchase_timestamp offset-aware for each phone listing
    for phone in phone_listings:
        phone.purchase_timestamp = phone.purchase_timestamp.replace(tzinfo=timezone.utc)

    return render_template('index.html', phone_listings=phone_listings, current_time=current_time_plus_one_hour)





    
# Routes and views
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
