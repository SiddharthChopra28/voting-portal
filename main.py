import os
import json
import random
import string
import smtplib
from email.message import EmailMessage
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))

# File paths for our JSON storage
ALLOWED_EMAILS_FILE = 'allowed_emails.json'
OTP_DATA_FILE = 'otp_data.json'
VOTES_FILE = 'votes.json'

# Ensure our JSON files exist
def ensure_json_files():
    # Structure for allowed emails
    if not os.path.exists(ALLOWED_EMAILS_FILE):
        with open(ALLOWED_EMAILS_FILE, 'w') as f:
            json.dump({
                "emails": [
                    "test@example.com",
                    "user@example.com",
                    "admin@example.com"
                ]
            }, f, indent=4)
    
    # Structure for OTP data
    if not os.path.exists(OTP_DATA_FILE):
        with open(OTP_DATA_FILE, 'w') as f:
            json.dump({}, f, indent=4)
    
    # Structure for votes
    if not os.path.exists(VOTES_FILE):
        with open(VOTES_FILE, 'w') as f:
            json.dump({
                "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                "votes": []
            }, f, indent=4)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Check if email is in allowed list
def is_email_allowed(email):
    with open(ALLOWED_EMAILS_FILE, 'r') as f:
        data = json.load(f)
        return (email in data["emails"].keys()) and (not data["emails"][email])

# Generate a random 6-digit OTP
def generate_otp():
    return ''.join(random.choice(string.digits) for _ in range(6))

# Send OTP via email (mock function - we'll just print it for this example)
def send_otp_email(email, otp):
    # In a real application, you would configure SMTP settings and send an actual email
    print(f"OTP for {email}: {otp}")  # For development/testing only
    
    # Simulated email sending
    # message = f"""
    # Subject: Your OTP for Voting App Login
    
    # Your One-Time Password is: {otp}
    
    # This OTP will expire in 10 minutes.
    # """
    # print(message)
    
    # You would use something like this in production:
    
    # Configure your email settings here
    msg = EmailMessage()
    msg.set_content(f"Your OTP for login is: {otp}")
    msg['Subject'] = 'Voting App Login OTP'
    msg['From'] = 'chiraagkathiresan7@gmail.com'
    msg['To'] = email
    
    # Connect to SMTP server and send
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('chiraagkathiresan7@gmail.com', 'ovca zaiv szvo khbd')
        smtp.send_message(msg)
    
    return True

# Save OTP to file
def save_otp(email, otp):
    with open(OTP_DATA_FILE, 'r') as f:
        data = json.load(f)
    
    # Add/update OTP with timestamp for expiry checking
    data[email] = {
        "otp": otp,
        "timestamp": datetime.now().timestamp()
    }
    
    with open(OTP_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Verify OTP is correct and not expired
def verify_otp(email, entered_otp):
    with open(OTP_DATA_FILE, 'r') as f:
        data = json.load(f)
    
    if email not in data:
        return False
    
    # Check if OTP is correct and not expired (10 minutes validity)
    otp_data = data[email]
    otp_time = otp_data["timestamp"]
    current_time = datetime.now().timestamp()
    
    # 600 seconds = 10 minutes
    if current_time - otp_time <= 600 and otp_data["otp"] == entered_otp:
        # Remove the OTP after successful verification
        del data[email]
        with open(OTP_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    
    return False

# Save vote to file (anonymized and randomized)
def save_vote(option, emailid):
    with open(VOTES_FILE, 'r') as f:
        data = json.load(f)
        
    sno = 0
    for i in data["votes"]:
        if int(i["s.no"])>sno:
            sno = int(i["s.no"])
    sno += 1
    # Add vote with timestamp
    data["votes"].append({
        "s.no": sno,
        "option": option,
        "timestamp": datetime.now().timestamp()
    })
    
    with open(VOTES_FILE, 'w') as f:
        json.dump(data, f, indent=4)
        
    with open(ALLOWED_EMAILS_FILE, 'r') as f:
        data = json.load(f)
    data["emails"][emailid] = True
        
    with open(ALLOWED_EMAILS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Route for the home page
@app.route('/')
def home():
    if 'email' in session:
        return redirect(url_for('voting_page'))
    return redirect(url_for('login'))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Please enter an email address.', 'danger')
            return render_template('login.html')
        
        if not is_email_allowed(email):
            flash('This email is not allowed to access the voting system or has already voted.', 'danger')
            return render_template('login.html')
        
        # Generate and save OTP
        otp = generate_otp()
        save_otp(email, otp)
        
        # Send OTP to the email
        send_otp_email(email, otp)
        
        # Store email in session temporarily for OTP verification
        session['temp_email'] = email
        
        # Redirect to OTP verification page
        return redirect(url_for('verify_otp_route'))
    
    return render_template('login.html')

# OTP verification route
@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp_route():
    if 'temp_email' not in session:
        flash('Please start the login process again.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        email = session['temp_email']
        
        if not entered_otp:
            flash('Please enter the OTP sent to your email.', 'danger')
            return render_template('verify_otp.html')
        
        if verify_otp(email, entered_otp):
            # OTP verified successfully, set up the actual session
            session.pop('temp_email', None)
            session['email'] = email
            flash('Logged in successfully!', 'success')
            return redirect(url_for('voting_page'))
        else:
            flash('Invalid or expired OTP. Please try again.', 'danger')
            return render_template('verify_otp.html')
    
    return render_template('verify_otp.html')

# Voting page route
@app.route('/vote', methods=['GET', 'POST'])
@login_required
def voting_page():
    # Get voting options
    with open(VOTES_FILE, 'r') as f:
        data = json.load(f)
        options = data["options"]
    
    if request.method == 'POST':
        selected_option = request.form.get('option')
        
        if not selected_option or selected_option not in options:
            flash('Please select a valid option.', 'danger')
            return render_template('vote.html', options=options)
        
        # Save the anonymized vote
        save_vote(selected_option, session['email'])
        print(session['email'])
        
        flash('Your vote has been recorded. Thank you!', 'success')
        return redirect(url_for('thank_you'))
    
    return render_template('vote.html', options=options)

# Thank you page after voting
@app.route('/thank-you')
def thank_you():
    session.clear()
    return render_template('thank_you.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    # Initialize JSON files and templates
    ensure_json_files()
    app.run(debug=True)