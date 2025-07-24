import sqlite3
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

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Global variable to track if browser was already opened
browser_opened = False
# Database initialization
def init_db():
    conn = sqlite3.connect('stocker.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Portfolio table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            stock_symbol TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            average_price REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Trade history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            stock_symbol TEXT NOT NULL,
            trade_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            total_amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Help messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS help_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Stock data simulation
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
        # SNS simulation for local version
        print(f"SNS Notification: {message}")
        # In real AWS version, this would use boto3
    except Exception as e:
        print(f"SNS notification failed: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        conn = sqlite3.connect('stocker.db')
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        cursor.execute('SELECT id, username, email, role FROM users WHERE email=? AND password_hash=? AND role=?', 
                      (email, password_hash, role))
        user = cursor.fetchone()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['email'] = user[2]
            session['role'] = user[3]
            
            # Send notifications
            send_email_notification(user[2], "Login Alert", f"User {user[1]} logged in as {role}")
            send_sns_notification(f"User {user[1]} logged in as {role}")
            
            if role == 'Admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        
        conn.close()
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        conn = sqlite3.connect('stocker.db')
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute('SELECT id FROM users WHERE username=?', (username,))
        if cursor.fetchone():
            conn.close()
            return render_template('signup.html', error='Username already exists')
        
        password_hash = hash_password(password)
        cursor.execute('INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
                      (username, email, password_hash, role))
        conn.commit()
        conn.close()
        
        # Send notifications
        send_email_notification(email, "Welcome to Stocker", f"Welcome {username}! Your account has been created.")
        send_sns_notification(f"New user signup: {username} as {role}")
        
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/check_username/<username>')
def check_username(username):
    conn = sqlite3.connect('stocker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username=?', (username,))
    exists = cursor.fetchone() is not None
    conn.close()
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
        
        conn = sqlite3.connect('stocker.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO help_messages (user_id, username, message) VALUES (?, ?, ?)',
                      (session['user_id'], session['username'], message))
        conn.commit()
        conn.close()
        
        return render_template('help.html', username=session['username'], success=True)
    
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
    
    conn = sqlite3.connect('stocker.db')
    cursor = conn.cursor()
    
    # Record trade in history
    cursor.execute('''INSERT INTO trade_history 
                     (user_id, stock_symbol, trade_type, quantity, price, total_amount) 
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (session['user_id'], stock_symbol, trade_type, quantity, price, total_amount))
    
    # Update portfolio
    cursor.execute('SELECT quantity, average_price FROM portfolio WHERE user_id=? AND stock_symbol=?',
                  (session['user_id'], stock_symbol))
    portfolio_item = cursor.fetchone()
    
    if trade_type == 'buy':
        if portfolio_item:
            current_quantity = portfolio_item[0]
            current_avg_price = portfolio_item[1]
            new_quantity = current_quantity + quantity
            new_avg_price = ((current_quantity * current_avg_price) + (quantity * price)) / new_quantity
            
            cursor.execute('UPDATE portfolio SET quantity=?, average_price=? WHERE user_id=? AND stock_symbol=?',
                          (new_quantity, new_avg_price, session['user_id'], stock_symbol))
        else:
            cursor.execute('INSERT INTO portfolio (user_id, stock_symbol, quantity, average_price) VALUES (?, ?, ?, ?)',
                          (session['user_id'], stock_symbol, quantity, price))
    
    elif trade_type == 'sell':
        if portfolio_item:
            current_quantity = portfolio_item[0]
            if current_quantity >= quantity:
                new_quantity = current_quantity - quantity
                if new_quantity > 0:
                    cursor.execute('UPDATE portfolio SET quantity=? WHERE user_id=? AND stock_symbol=?',
                                  (new_quantity, session['user_id'], stock_symbol))
                else:
                    cursor.execute('DELETE FROM portfolio WHERE user_id=? AND stock_symbol=?',
                                  (session['user_id'], stock_symbol))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/portfolio')
def api_portfolio():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = sqlite3.connect('stocker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT stock_symbol, quantity, average_price, created_at FROM portfolio WHERE user_id=?',
                  (session['user_id'],))
    portfolio = cursor.fetchall()
    conn.close()
    
    current_prices = get_current_stock_prices()
    
    result = []
    for item in portfolio:
        symbol, quantity, avg_price, created_at = item
        current_price = current_prices.get(symbol, {}).get('price', 0)
        result.append({
            'symbol': symbol,
            'name': STOCK_DATA[symbol]['name'],
            'quantity': quantity,
            'average_price': avg_price,
            'current_price': current_price,
            'total_value': quantity * current_price,
            'created_at': created_at
        })
    
    return jsonify(result)

@app.route('/api/trade_history')
def api_trade_history():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = sqlite3.connect('stocker.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT stock_symbol, trade_type, quantity, price, total_amount, created_at 
                     FROM trade_history WHERE user_id=? ORDER BY created_at DESC''',
                  (session['user_id'],))
    history = cursor.fetchall()
    conn.close()
    
    result = []
    for item in history:
        symbol, trade_type, quantity, price, total_amount, created_at = item
        result.append({
            'symbol': symbol,
            'name': STOCK_DATA[symbol]['name'],
            'trade_type': trade_type,
            'quantity': quantity,
            'price': price,
            'total_amount': total_amount,
            'created_at': created_at
        })
    
    return jsonify(result)

# Admin API endpoints
@app.route('/api/admin/stats')
def api_admin_stats():
    if 'user_id' not in session or session['role'] != 'Admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    conn = sqlite3.connect('stocker.db')
    cursor = conn.cursor()
    
    # Get total traders
    cursor.execute('SELECT COUNT(*) FROM users WHERE role="Trader"')
    total_traders = cursor.fetchone()[0]
    
    # Get total trades
    cursor.execute('SELECT COUNT(*) FROM trade_history')
    total_trades = cursor.fetchone()[0]
    
    # Get total portfolio value
    cursor.execute('SELECT SUM(quantity * average_price) FROM portfolio')
    total_portfolio_value = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return jsonify({
        'total_traders': total_traders,
        'total_trades': total_trades,
        'total_portfolio_value': total_portfolio_value
    })

@app.route('/api/admin/all_portfolios')
def api_admin_all_portfolios():
    if 'user_id' not in session or session['role'] != 'Admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    conn = sqlite3.connect('stocker.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT u.username, p.stock_symbol, p.quantity, p.average_price, p.created_at
                     FROM portfolio p JOIN users u ON p.user_id = u.id
                     ORDER BY u.username, p.stock_symbol''')
    portfolios = cursor.fetchall()
    conn.close()
    
    current_prices = get_current_stock_prices()
    
    result = []
    for item in portfolios:
        username, symbol, quantity, avg_price, created_at = item
        current_price = current_prices.get(symbol, {}).get('price', 0)
        result.append({
            'username': username,
            'symbol': symbol,
            'name': STOCK_DATA[symbol]['name'],
            'quantity': quantity,
            'average_price': avg_price,
            'current_price': current_price,
            'total_value': quantity * current_price,
            'created_at': created_at
        })
    
    return jsonify(result)

@app.route('/api/admin/all_trades')
def api_admin_all_trades():
    if 'user_id' not in session or session['role'] != 'Admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    conn = sqlite3.connect('stocker.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT u.username, t.stock_symbol, t.trade_type, t.quantity, t.price, t.total_amount, t.created_at
                     FROM trade_history t JOIN users u ON t.user_id = u.id
                     ORDER BY t.created_at DESC''')
    trades = cursor.fetchall()
    conn.close()
    
    result = []
    for item in trades:
        username, symbol, trade_type, quantity, price, total_amount, created_at = item
        result.append({
            'username': username,
            'symbol': symbol,
            'name': STOCK_DATA[symbol]['name'],
            'trade_type': trade_type,
            'quantity': quantity,
            'price': price,
            'total_amount': total_amount,
            'created_at': created_at
        })
    
    return jsonify(result)

@app.route('/api/admin/users')
def api_admin_users():
    if 'user_id' not in session or session['role'] != 'Admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    conn = sqlite3.connect('stocker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, email, role, created_at FROM users ORDER BY created_at DESC')
    users = cursor.fetchall()
    conn.close()
    
    result = []
    for item in users:
        username, email, role, created_at = item
        result.append({
            'username': username,
            'email': email,
            'role': role,
            'created_at': created_at
        })
    
    return jsonify(result)

@app.route('/api/admin/messages')
def api_admin_messages():
    if 'user_id' not in session or session['role'] != 'Admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    conn = sqlite3.connect('stocker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, message, created_at FROM help_messages ORDER BY created_at DESC')
    messages = cursor.fetchall()
    conn.close()
    
    result = []
    for item in messages:
        username, message, created_at = item
        result.append({
            'username': username,
            'message': message,
            'created_at': created_at
        })
    
    return jsonify(result)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def open_browser():
    global browser_opened
    if not browser_opened:
        webbrowser.open('http://127.0.0.1:5000')
        browser_opened = True
    

if __name__ == '__main__':
    init_db()
    print("Stocker Local Version Starting...")
    print("Database: SQLite (stocker.db)")
    print("Opening browser...")
    
    # Open browser after a short delay
    timer = threading.Timer(1.0, open_browser)
    timer.start()
    
    app.run(debug=False,host='0.0.0.0', port=5000)
