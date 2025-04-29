import os
import random
import string
import smtplib
from email.message import EmailMessage
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))

# MongoDB Atlas connection
client = MongoClient('mongodb+srv://siddharth:thisisarandompassword@voting-cluster.6xurpnj.mongodb.net/?retryWrites=true&w=majority&appName=voting-cluster')
db = client.votingApp

# Collections instead of JSON files
allowed_emails_collection = db.allowed_emails
otp_collection = db.otp_data
votes_collection = db.votes

# Ensure our MongoDB collections and data exist
def ensure_mongodb_setup():
    # Create initial data if collections are empty
    if allowed_emails_collection.count_documents({}) == 0:
        allowed_emails_collection.insert_many([{'email': 'aakarshit1@me.iitr.ac.in', 'has_voted': False}, {'email': 'aaryan_k@me.iitr.ac.in', 'has_voted': False}, {'email': 'aditya_j@me.iitr.ac.in', 'has_voted': False}, {'email': 'aditya_s@me.iitr.ac.in', 'has_voted': False}, {'email': 'aditya_s1@me.iitr.ac.in', 'has_voted': False}, {'email': 'akshit_j@me.iitr.ac.in', 'has_voted': False}, {'email': 'anjali1@me.iitr.ac.in', 'has_voted': False}, {'email': 'arjun_k@me.iitr.ac.in', 'has_voted': False}, {'email': 'aryan_s2@me.iitr.ac.in', 'has_voted': False}, {'email': 'bhushan_dk@me.iitr.ac.in', 'has_voted': False}, {'email': 'chiraag_mk@me.iitr.ac.in', 'has_voted': False}, {'email': 'devansh_c@me.iitr.ac.in', 'has_voted': False}, {'email': 'diwase_ss@me.iitr.ac.in', 'has_voted': False}, {'email': 'hardik_g@me.iitr.ac.in', 'has_voted': False}, {'email': 'harsh_n@me.iitr.ac.in', 'has_voted': False}, {'email': 'harsh_n1@me.iitr.ac.in', 'has_voted': False}, {'email': 'harshal_r@me.iitr.ac.in', 'has_voted': False}, {'email': 'harshita1@me.iitr.ac.in', 'has_voted': False}, {'email': 'harshita_b@me.iitr.ac.in', 'has_voted': False}, {'email': 'himanshu_y@me.iitr.ac.in', 'has_voted': False}, {'email': 'himesh_k@me.iitr.ac.in', 'has_voted': False}, {'email': 'jadhavar_sb@me.iitr.ac.in', 'has_voted': False}, {'email': 'jaswant_km@me.iitr.ac.in', 'has_voted': False}, {'email': 'liki_b@me.iitr.ac.in', 'has_voted': False}, {'email': 'mahajan_pj@me.iitr.ac.in', 'has_voted': False}, {'email': 'manav1@me.iitr.ac.in', 'has_voted': False}, {'email': 'mayank_m@me.iitr.ac.in', 'has_voted': False}, {'email': 'mohit_g2@me.iitr.ac.in', 'has_voted': False}, {'email': 'mohit_k1@me.iitr.ac.in', 'has_voted': False}, {'email': 'monika_s@me.iitr.ac.in', 'has_voted': False}, {'email': 'mukul1@me.iitr.ac.in', 'has_voted': False}, {'email': 'vamsi_kvv@me.iitr.ac.in', 'has_voted': False}, {'email': 'naman_pm@me.iitr.ac.in', 'has_voted': False}, {'email': 'navya_j@me.iitr.ac.in', 'has_voted': False}, {'email': 'nilansh_b@me.iitr.ac.in', 'has_voted': False}, {'email': 'palak_p@me.iitr.ac.in', 'has_voted': False}, {'email': 'pallavi_k@me.iitr.ac.in', 'has_voted': False}, {'email': 'parteek_g@me.iitr.ac.in', 'has_voted': False}, {'email': 'parthan_as@me.iitr.ac.in', 'has_voted': False}, {'email': 'patil_sc@me.iitr.ac.in', 'has_voted': False}, {'email': 'piyush_k1@me.iitr.ac.in', 'has_voted': False}, {'email': 'pragya_b@me.iitr.ac.in', 'has_voted': False}, {'email': 'rishi_t@me.iitr.ac.in', 'has_voted': False}, {'email': 'rudra_ps@me.iitr.ac.in', 'has_voted': False}, {'email': 'sanat_kj@me.iitr.ac.in', 'has_voted': False}, {'email': 'neel_sp@me.iitr.ac.in', 'has_voted': False}, {'email': 'satyam_p@me.iitr.ac.in', 'has_voted': False}, {'email': 'saumya_n@me.iitr.ac.in', 'has_voted': False}, {'email': 'shrey_d@me.iitr.ac.in', 'has_voted': False}, {'email': 'shubham_a@me.iitr.ac.in', 'has_voted': False}, {'email': 'siddharth_c1@me.iitr.ac.in', 'has_voted': False}, {'email': 'khushi_sv@me.iitr.ac.in', 'has_voted': False}, {'email': 'subhra_jd@me.iitr.ac.in', 'has_voted': False}, {'email': 'suhani_r@me.iitr.ac.in', 'has_voted': False}, {'email': 'suyash_j@me.iitr.ac.in', 'has_voted': False}, {'email': 'tushar_k@me.iitr.ac.in', 'has_voted': False}, {'email': 'vinayak_r@me.iitr.ac.in', 'has_voted': False}, {'email': 'yatharth_g@me.iitr.ac.in', 'has_voted': False}])
    
    # Create voting options if they don't exist
    if votes_collection.count_documents({"type": "options"}) == 0:
        votes_collection.insert_one({
            "type": "options",
            "options": ["Yatharth Goyal", "Devansh Chouksey", "Harsh Ninania", "None of the above"]
        })

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
    user = allowed_emails_collection.find_one({"email": email})
    return user is not None and not user.get("has_voted", False)

# Generate a random 6-digit OTP
def generate_otp():
    return ''.join(random.choice(string.digits) for _ in range(6))

# Send OTP via email
def send_otp_email(email, otp):
    print(f"OTP for {email}: {otp}")  # For development/testing only
    
    # Configure your email settings here
    msg = EmailMessage()
    msg.set_content(f"Your OTP for login is: {otp}")
    msg['Subject'] = 'Voting App Login OTP'
    msg['From'] = 'pni28election@gmail.com'
    msg['To'] = email
    
    # Connect to SMTP server and send
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('pni28election@gmail.com', 'zhaw ylnb msdh ixuj')
        smtp.send_message(msg)
    
    return True

# Save OTP to MongoDB
def save_otp(email, otp):
    # Remove any existing OTP for this email
    otp_collection.delete_many({"email": email})
    
    # Insert new OTP with timestamp
    otp_collection.insert_one({
        "email": email,
        "otp": otp,
        "timestamp": datetime.now().timestamp()
    })

# Verify OTP is correct and not expired
def verify_otp(email, entered_otp):
    otp_data = otp_collection.find_one({"email": email})
    
    if not otp_data:
        return False
    
    # Check if OTP is correct and not expired (10 minutes validity)
    otp_time = otp_data["timestamp"]
    current_time = datetime.now().timestamp()
    
    # 600 seconds = 10 minutes
    if current_time - otp_time <= 600 and otp_data["otp"] == entered_otp:
        # Remove the OTP after successful verification
        otp_collection.delete_one({"email": email})
        return True
    
    return False

# Save vote to MongoDB
def save_vote(option, email):
    # Get the current highest serial number
    highest_vote = votes_collection.find_one(
        {"type": "vote"}, 
        sort=[("s_no", -1)]
    )
    
    sno = 1  # Default if no votes exist
    if highest_vote and "s_no" in highest_vote:
        sno = highest_vote["s_no"] + 1
    
    # Add vote with timestamp
    votes_collection.insert_one({
        "type": "vote",
        "s_no": sno,
        "option": option,
        "timestamp": datetime.now().timestamp()
    })
    
    # Mark email as voted
    allowed_emails_collection.update_one(
        {"email": email},
        {"$set": {"has_voted": True}}
    )

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
    options_data = votes_collection.find_one({"type": "options"})
    options = options_data["options"] if options_data else []
    
    if request.method == 'POST':
        selected_option = request.form.get('option')
        
        if not selected_option or selected_option not in options:
            flash('Please select a valid option.', 'danger')
            return render_template('vote.html', options=options)
        
        # Save the vote
        save_vote(selected_option, session['email'])
        
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
    # Initialize MongoDB collections
    ensure_mongodb_setup()
    app.run(debug=True)