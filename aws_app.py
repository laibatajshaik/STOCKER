import boto3
import hashlib
import secrets
import smtplib
import json
import time
import random
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import webbrowser
import threading
from decimal import Decimal

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Global variable to track if browser was already opened
browser_opened = False
# AWS Configuration (hardcoded for demo)
AWS_REGION = 'us-east-1'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:148761657981:stocker'
DYNAMODB_TABLE_PREFIX = 'stocker_'

# Initialize AWS clients
try:
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    sns = boto3.client('sns', region_name=AWS_REGION)
    print("AWS services initialized successfully")
except Exception as e:
    print(f"AWS initialization failed: {e}")
    # Fallback to local simulation
    dynamodb = None
    sns = None

# DynamoDB table initialization
def init_dynamodb():
    if not dynamodb:
        return
    
    try:
        # Users table
        users_table = dynamodb.create_table(
            TableName=f'{DYNAMODB_TABLE_PREFIX}users',
            KeySchema=[
                {'AttributeName': 'username', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'username', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Portfolio table
        portfolio_table = dynamodb.create_table(
            TableName=f'{DYNAMODB_TABLE_PREFIX}portfolio',
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'stock_symbol', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'stock_symbol', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Trade history table
        trade_history_table = dynamodb.create_table(
            TableName=f'{DYNAMODB_TABLE_PREFIX}trade_history',
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Help messages table
        help_messages_table = dynamodb.create_table(
            TableName=f'{DYNAMODB_TABLE_PREFIX}help_messages',
            KeySchema=[
                {'AttributeName': 'message_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'message_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        print("DynamoDB tables created successfully")
        
    except Exception as e:
        print(f"DynamoDB table creation failed (tables may already exist): {e}")

# Stock data simulation (same as local version)
STOCK_DATA = {
    'AAPL': {'name': 'Apple Inc.', 'base_price': 150.00},
    'GOOGL': {'name': 'Alphabet Inc.', 'base_price': 2500.00},
    'MSFT': {'name': 'Microsoft Corporation', 'base_price': 300.00},
    'AMZN': {'name': 'Amazon.com Inc.', 'base_price': 3200.00},
    'TSLA': {'name': 'Tesla Inc.', 'base_price': 800.00},
    'META': {'name': 'Meta Platforms Inc.', 'base_price': 320.00},
    'NVDA': {'name': 'NVIDIA Corporation', 'base_price': 900.00},
    'NFLX': {'name': 'Netflix Inc.', 'base_price': 500.00},
    'BABA': {'name': 'Alibaba Group', 'base_price': 100.00},
    'JPM': {'name': 'JPMorgan Chase', 'base_price': 140.00},
    'JNJ': {'name': 'Johnson & Johnson', 'base_price': 170.00},
    'V': {'name': 'Visa Inc.', 'base_price': 220.00},
    'WMT': {'name': 'Walmart Inc.', 'base_price': 145.00},
    'PG': {'name': 'Procter & Gamble', 'base_price': 155.00},
    'HD': {'name': 'Home Depot Inc.', 'base_price': 330.00},
    'MA': {'name': 'Mastercard Inc.', 'base_price': 350.00},
    'BAC': {'name': 'Bank of America', 'base_price': 40.00},
    'DIS': {'name': 'Walt Disney Company', 'base_price': 110.00},
    'ADBE': {'name': 'Adobe Inc.', 'base_price': 550.00},
    'CRM': {'name': 'Salesforce Inc.', 'base_price': 210.00},
    'ORCL': {'name': 'Oracle Corporation', 'base_price': 85.00}
}

def get_current_stock_prices():
    prices = {}
    for symbol, data in STOCK_DATA.items():
        # Simulate price fluctuation
        base_price = data['base_price']
        fluctuation = random.uniform(-0.05, 0.05)  # +/- 5% fluctuation
        current_price = base_price * (1 + fluctuation)
        prices[symbol] = {
            'name': data['name'],
            'price': round(current_price, 2),
            'change': round(fluctuation * 100, 2)
        }
    return prices

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def send_email_notification(to_email, subject, body):
    try:
        # Email configuration (hardcoded for demo)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "stocker.demo@gmail.com"
        sender_password = "demo_password_123"
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Email sending failed: {e}")

def send_sns_notification(message):
    try:
        if sns:
            response = sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=message,
                Subject='Stocker Alert'
            )
            print(f"SNS notification sent: {response['MessageId']}")
        else:
            print(f"SNS Notification (simulated): {message}")
    except Exception as e:
        print(f"SNS notification failed: {e}")

# DynamoDB helper functions
def get_user_by_username(username):
    if not dynamodb:
        return None
    
    try:
        table = dynamodb.Table(f'{DYNAMODB_TABLE_PREFIX}users')
        response = table.scan(
            FilterExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        items = response.get('Items', [])
        return items[0] if items else None
    except Exception as e:
        print(f"DynamoDB get_user_by_email error: {e}")
        return None

def get_user_by_username(username):
    if not dynamodb:
        return None
    
    try:
        table = dynamodb.Table(f'{DYNAMODB_TABLE_PREFIX}users')
        response = table.get_item(Key={'username': username})
        return response.get('Item')
    except Exception as e:
        print(f"DynamoDB get_user_by_username error: {e}")
        return None

def create_user(username, email, password_hash, role):
    if not dynamodb:
        return False
    
    try:
        table = dynamodb.Table(f'{DYNAMODB_TABLE_PREFIX}users')
        table.put_item(Item={
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'role': role,
            'created_at': datetime.now().isoformat()
        })
        return True
    except Exception as e:
        print(f"DynamoDB create_user error: {e}")
        return False

def get_user_portfolio(user_id):
    if not dynamodb:
        return []
    
    try:
        table = dynamodb.Table(f'{DYNAMODB_TABLE_PREFIX}portfolio')
        response = table.query(KeyConditionExpression='user_id = :user_id',
                              ExpressionAttributeValues={':user_id': user_id})
        return response.get('Items', [])
    except Exception as e:
        print(f"DynamoDB get_user_portfolio error: {e}")
        return []

def update_portfolio(user_id, stock_symbol, quantity, average_price):
    if not dynamodb:
        return False
    
    try:
        table = dynamodb.Table(f'{DYNAMODB_TABLE_PREFIX}portfolio')
        if quantity > 0:
            table.put_item(Item={
                'user_id': user_id,
                'stock_symbol': stock_symbol,
                'quantity': quantity,
                'average_price': Decimal(str(average_price)),
                'created_at': datetime.now().isoformat()
            })
        else:
            table.delete_item(Key={'user_id': user_id, 'stock_symbol': stock_symbol})
        return True
    except Exception as e:
        print(f"DynamoDB update_portfolio error: {e}")
        return False

def add_trade_history(user_id, stock_symbol, trade_type, quantity, price, total_amount):
    if not dynamodb:
        return False
    
    try:
        table = dynamodb.Table(f'{DYNAMODB_TABLE_PREFIX}trade_history')
        timestamp = datetime.now().isoformat()
        table.put_item(Item={
            'user_id': user_id,
            'timestamp': timestamp,
            'stock_symbol': stock_symbol,
            'trade_type': trade_type,
            'quantity': quantity,
            'price': Decimal(str(price)),
            'total_amount': Decimal(str(total_amount)),
            'created_at': timestamp
        })
        return True
    except Exception as e:
        print(f"DynamoDB add_trade_history error: {e}")
        return False

def get_user_trade_history(user_id):
    if not dynamodb:
        return []
    
    try:
        table = dynamodb.Table(f'{DYNAMODB_TABLE_PREFIX}trade_history')
        response = table.query(KeyConditionExpression='user_id = :user_id',
                              ExpressionAttributeValues={':user_id': user_id},
                              ScanIndexForward=False)
        return response.get('Items', [])
    except Exception as e:
        print(f"DynamoDB get_user_trade_history error: {e}")
        return []

def add_help_message(user_id, username, message):
    if not dynamodb:
        return False
    
    try:
        table = dynamodb.Table(f'{DYNAMODB_TABLE_PREFIX}help_messages')
        message_id = f"{user_id}_{int(time.time())}"
        table.put_item(Item={
            'message_id': message_id,
            'user_id': user_id,
            'username': username,
            'message': message,
            'created_at': datetime.now().isoformat()
        })
        return True
    except Exception as e:
        print(f"DynamoDB add_help_message error: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        password_hash = hash_password(password)
        user = get_user_by_email(email)
        
        if user and user['password_hash'] == password_hash and user['role'] == role:
            session['user_id'] = user['username']
            session['username'] = user['username']
            session['email'] = user['email']
            session['role'] = user['role']
            
            # Send notifications
            send_email_notification(user['email'], "Login Alert", f"User {user['username']} logged in as {role}")
            send_sns_notification(f"User {user['username']} logged in as {role}")
            
            if role == 'Admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        # Check if username already exists
        if get_user_by_username(username):
            return render_template('signup.html', error='Username already exists')
        
        password_hash = hash_password(password)
        if create_user(username, email, password_hash, role):
            # Send notifications
            send_email_notification(email, "Welcome to Stocker", f"Welcome {username}! Your account has been created.")
            send_sns_notification(f"New user signup: {username} as {role}")
            
            return redirect(url_for('login'))
        else:
            return render_template('signup.html', error='Signup failed')
    
    return render_template('signup.html')

@app.route('/check_username/<username>')
def check_username(username):
    exists = get_user_by_username(username) is not None
    return jsonify({'exists': exists})

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session['role'] != 'Trader':
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/trade')
def trade():
    if 'user_id' not in session or session['role'] != 'Trader':
        return redirect(url_for('login'))
    return render_template('trade.html', username=session['username'])

@app.route('/portfolio')
def portfolio():
    if 'user_id' not in session or session['role'] != 'Trader':
        return redirect(url_for('login'))
    return render_template('portfolio.html', username=session['username'])

@app.route('/history')
def history():
    if 'user_id' not in session or session['role'] != 'Trader':
        return redirect(url_for('login'))
    return render_template('history.html', username=session['username'])

@app.route('/help', methods=['GET', 'POST'])
def help():
    if 'user_id' not in session or session['role'] != 'Trader':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        message = request.form['message']
        
        if add_help_message(session['user_id'], session['username'], message):
            return render_template('help.html', username=session['username'], success=True)
        else:
            return render_template('help.html', username=session['username'], error='Failed to send message')
    
    return render_template('help.html', username=session['username'])

# Admin routes
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html', username=session['username'])

@app.route('/admin_portfolio')
def admin_portfolio():
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('login'))
    return render_template('admin_portfolio.html', username=session['username'])

@app.route('/admin_history')
def admin_history():
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('login'))
    return render_template('admin_history.html', username=session['username'])

@app.route('/admin_manage')
def admin_manage():
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('login'))
    return render_template('admin_manage.html', username=session['username'])

# API endpoints
@app.route('/api/stock_prices')
def api_stock_prices():
    return jsonify(get_current_stock_prices())

@app.route('/api/execute_trade', methods=['POST'])
def api_execute_trade():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    stock_symbol = data['stock_symbol']
    trade_type = data['trade_type']
    quantity = int(data['quantity'])
    price = float(data['price'])
    total_amount = quantity * price
    
    # Record trade in history
    add_trade_history(session['user_id'], stock_symbol, trade_type, quantity, price, total_amount)
    
    # Update portfolio
    portfolio = get_user_portfolio(session['user_id'])
    portfolio_item = None
    for item in portfolio:
        if item['stock_symbol'] == stock_symbol:
            portfolio_item = item
            break
    
    if trade_type == 'buy':
        if portfolio_item:
            current_quantity = int(portfolio_item['quantity'])
            current_avg_price = float(portfolio_item['average_price'])
            new_quantity = current_quantity + quantity
            new_avg_price = ((current_quantity * current_avg_price) + (quantity * price)) / new_quantity
            
            update_portfolio(session['user_id'], stock_symbol, new_quantity, new_avg_price)
        else:
            update_portfolio(session['user_id'], stock_symbol, quantity, price)
    
    elif trade_type == 'sell':
        if portfolio_item:
            current_quantity = int(portfolio_item['quantity'])
            if current_quantity >= quantity:
                new_quantity = current_quantity - quantity
                avg_price = float(portfolio_item['average_price'])
                update_portfolio(session['user_id'], stock_symbol, new_quantity, avg_price)
    
    return jsonify({'success': True})

@app.route('/api/portfolio')
def api_portfolio():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    portfolio = get_user_portfolio(session['user_id'])
    current_prices = get_current_stock_prices()
    
    result = []
    for item in portfolio:
        symbol = item['stock_symbol']
        quantity = int(item['quantity'])
        avg_price = float(item['average_price'])
        current_price = current_prices.get(symbol, {}).get('price', 0)
        
        result.append({
            'symbol': symbol,
            'name': STOCK_DATA[symbol]['name'],
            'quantity': quantity,
            'average_price': avg_price,
            'current_price': current_price,
            'total_value': quantity * current_price,
            'created_at': item['created_at']
        })
    
    return jsonify(result)

@app.route('/api/trade_history')
def api_trade_history():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    history = get_user_trade_history(session['user_id'])
    
    result = []
    for item in history:
        symbol = item['stock_symbol']
        result.append({
            'symbol': symbol,
            'name': STOCK_DATA[symbol]['name'],
            'trade_type': item['trade_type'],
            'quantity': int(item['quantity']),
            'price': float(item['price']),
            'total_amount': float(item['total_amount']),
            'created_at': item['created_at']
        })
    
    return jsonify(result)

# Admin API endpoints (simplified for AWS version)
@app.route('/api/admin/stats')
def api_admin_stats():
    if 'user_id' not in session or session['role'] != 'Admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    # Simplified stats for AWS version
    return jsonify({
        'total_traders': 25,
        'total_trades': 150,
        'total_portfolio_value': 125000.00
    })

@app.route('/api/admin/all_portfolios')
def api_admin_all_portfolios():
    if 'user_id' not in session or session['role'] != 'Admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    # Simplified for AWS version
    return jsonify([])

@app.route('/api/admin/all_trades')
def api_admin_all_trades():
    if 'user_id' not in session or session['role'] != 'Admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    # Simplified for AWS version
    return jsonify([])

@app.route('/api/admin/users')
def api_admin_users():
    if 'user_id' not in session or session['role'] != 'Admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    # Simplified for AWS version
    return jsonify([])

@app.route('/api/admin/messages')
def api_admin_messages():
    if 'user_id' not in session or session['role'] != 'Admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    # Simplified for AWS version
    return jsonify([])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def open_browser():
    global browser_opened
    if not browser_opened:
        webbrowser.open('http://127.0.0.1:5000')
        browser_opened = True
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    init_dynamodb()
    print("Stocker AWS Version Starting...")
    print("Database: AWS DynamoDB")
    print("Notifications: AWS SNS")
    print("Opening browser...")
    
    # Open browser after a short delay
    timer = threading.Timer(1.0, open_browser)
    timer.start()
    
    app.run(debug=True,host='0.0.0.0', port=5000)
