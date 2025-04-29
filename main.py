import os
import random
import string
import smtplib
from email.message import EmailMessage
from flask import Flask, render_template, render_template_string, request, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))

DB_PWD = os.environ["DB_PWD"]
SMTP_PWD = os.environ["SMTP_PWD"]

IS_LIVE = bool(os.environ["IS_LIVE"])



client = MongoClient(f'mongodb+srv://siddharth:{DB_PWD}@voting-cluster.6xurpnj.mongodb.net/?retryWrites=true&w=majority&appName=voting-cluster')
db = client.votingApp

allowed_emails_collection = db.allowed_emails
otp_collection = db.otp_data
votes_collection = db.votes




def ensure_mongodb_setup():
    if allowed_emails_collection.count_documents({}) == 0:
        allowed_emails_collection.insert_many([{'email': 'aakarshit1@me.iitr.ac.in', 'has_voted': False}, {'email': 'aaryan_k@me.iitr.ac.in', 'has_voted': False}, {'email': 'aditya_j@me.iitr.ac.in', 'has_voted': False}, {'email': 'aditya_s@me.iitr.ac.in', 'has_voted': False}, {'email': 'aditya_s1@me.iitr.ac.in', 'has_voted': False}, {'email': 'akshit_j@me.iitr.ac.in', 'has_voted': False}, {'email': 'anjali1@me.iitr.ac.in', 'has_voted': False}, {'email': 'arjun_k@me.iitr.ac.in', 'has_voted': False}, {'email': 'aryan_s2@me.iitr.ac.in', 'has_voted': False}, {'email': 'bhushan_dk@me.iitr.ac.in', 'has_voted': False}, {'email': 'chiraag_mk@me.iitr.ac.in', 'has_voted': False}, {'email': 'devansh_c@me.iitr.ac.in', 'has_voted': False}, {'email': 'diwase_ss@me.iitr.ac.in', 'has_voted': False}, {'email': 'hardik_g@me.iitr.ac.in', 'has_voted': False}, {'email': 'harsh_n@me.iitr.ac.in', 'has_voted': False}, {'email': 'harsh_n1@me.iitr.ac.in', 'has_voted': False}, {'email': 'harshal_r@me.iitr.ac.in', 'has_voted': False}, {'email': 'harshita1@me.iitr.ac.in', 'has_voted': False}, {'email': 'harshita_b@me.iitr.ac.in', 'has_voted': False}, {'email': 'himanshu_y@me.iitr.ac.in', 'has_voted': False}, {'email': 'himesh_k@me.iitr.ac.in', 'has_voted': False}, {'email': 'jadhavar_sb@me.iitr.ac.in', 'has_voted': False}, {'email': 'jaswant_km@me.iitr.ac.in', 'has_voted': False}, {'email': 'liki_b@me.iitr.ac.in', 'has_voted': False}, {'email': 'mahajan_pj@me.iitr.ac.in', 'has_voted': False}, {'email': 'manav1@me.iitr.ac.in', 'has_voted': False}, {'email': 'mayank_m@me.iitr.ac.in', 'has_voted': False}, {'email': 'mohit_g2@me.iitr.ac.in', 'has_voted': False}, {'email': 'mohit_k1@me.iitr.ac.in', 'has_voted': False}, {'email': 'monika_s@me.iitr.ac.in', 'has_voted': False}, {'email': 'mukul1@me.iitr.ac.in', 'has_voted': False}, {'email': 'vamsi_kvv@me.iitr.ac.in', 'has_voted': False}, {'email': 'naman_pm@me.iitr.ac.in', 'has_voted': False}, {'email': 'navya_j@me.iitr.ac.in', 'has_voted': False}, {'email': 'nilansh_b@me.iitr.ac.in', 'has_voted': False}, {'email': 'palak_p@me.iitr.ac.in', 'has_voted': False}, {'email': 'pallavi_k@me.iitr.ac.in', 'has_voted': False}, {'email': 'parteek_g@me.iitr.ac.in', 'has_voted': False}, {'email': 'parthan_as@me.iitr.ac.in', 'has_voted': False}, {'email': 'patil_sc@me.iitr.ac.in', 'has_voted': False}, {'email': 'piyush_k1@me.iitr.ac.in', 'has_voted': False}, {'email': 'pragya_b@me.iitr.ac.in', 'has_voted': False}, {'email': 'rishi_t@me.iitr.ac.in', 'has_voted': False}, {'email': 'rudra_ps@me.iitr.ac.in', 'has_voted': False}, {'email': 'sanat_kj@me.iitr.ac.in', 'has_voted': False}, {'email': 'neel_sp@me.iitr.ac.in', 'has_voted': False}, {'email': 'satyam_p@me.iitr.ac.in', 'has_voted': False}, {'email': 'saumya_n@me.iitr.ac.in', 'has_voted': False}, {'email': 'shrey_d@me.iitr.ac.in', 'has_voted': False}, {'email': 'shubham_a@me.iitr.ac.in', 'has_voted': False}, {'email': 'siddharth_c1@me.iitr.ac.in', 'has_voted': False}, {'email': 'khushi_sv@me.iitr.ac.in', 'has_voted': False}, {'email': 'subhra_jd@me.iitr.ac.in', 'has_voted': False}, {'email': 'suhani_r@me.iitr.ac.in', 'has_voted': False}, {'email': 'suyash_j@me.iitr.ac.in', 'has_voted': False}, {'email': 'tushar_k@me.iitr.ac.in', 'has_voted': False}, {'email': 'vinayak_r@me.iitr.ac.in', 'has_voted': False}, {'email': 'yatharth_g@me.iitr.ac.in', 'has_voted': False}])
    if votes_collection.count_documents({"type": "options"}) == 0:
        votes_collection.insert_one({
            "type": "options",
            "options": ["Yatharth Goyal", "Devansh Chouksey", "Harsh Ninania", "None of the above"]
        })

ensure_mongodb_setup()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def is_email_allowed(email):
    user = allowed_emails_collection.find_one({"email": email})
    return user is not None and not user.get("has_voted", False)

def generate_otp():
    return ''.join(random.choice(string.digits) for _ in range(6))

def send_otp_email(email, otp):
    print(f"OTP for {email}: {otp}")
    msg = EmailMessage()
    msg.set_content(f"Your OTP for login is: {otp}\nLogin at https://voting-portal.onrender.com/verify-otp")
    msg['Subject'] = 'PnI Election: Voting Portal Login OTP'
    msg['From'] = 'pni28election@gmail.com'
    msg['To'] = email
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('pni28election@gmail.com', SMTP_PWD)
        smtp.send_message(msg)
    return True

def save_otp(email, otp):
    otp_collection.delete_many({"email": email})
    otp_collection.insert_one({
        "email": email,
        "otp": otp,
        "timestamp": datetime.now().timestamp()
    })

def verify_otp(email, entered_otp):
    otp_data = otp_collection.find_one({"email": email})
    if not otp_data:
        return False
    otp_time = otp_data["timestamp"]
    current_time = datetime.now().timestamp()
    if current_time - otp_time <= 600 and otp_data["otp"] == entered_otp:
        otp_collection.delete_one({"email": email})
        return True
    return False

def save_vote(option, email):
    highest_vote = votes_collection.find_one(
        {"type": "vote"}, 
        sort=[("s_no", -1)]
    )
    sno = 1
    if highest_vote and "s_no" in highest_vote:
        sno = highest_vote["s_no"] + 1
    votes_collection.insert_one({
        "type": "vote",
        "s_no": sno,
        "option": option,
        "timestamp": datetime.now().timestamp()
    })
    allowed_emails_collection.update_one(
        {"email": email},
        {"$set": {"has_voted": True}}
    )


if IS_LIVE:

    @app.route('/')
    def home():
        if 'email' in session:
            return redirect(url_for('voting_page'))
        return redirect(url_for('login'))

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
            otp = generate_otp()
            save_otp(email, otp)
            send_otp_email(email, otp)
            session['temp_email'] = email
            return redirect(url_for('verify_otp_route'))
        return render_template('login.html')

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
                session.pop('temp_email', None)
                session['email'] = email
                flash('Logged in successfully!', 'success')
                return redirect(url_for('voting_page'))
            else:
                flash('Invalid or expired OTP. Please try again.', 'danger')
                return render_template('verify_otp.html')
        return render_template('verify_otp.html')

    @app.route('/vote', methods=['GET', 'POST'])
    @login_required
    def voting_page():
        options_data = votes_collection.find_one({"type": "options"})
        options = options_data["options"] if options_data else []
        if request.method == 'POST':
            selected_option = request.form.get('option')
            if not selected_option or selected_option not in options:
                flash('Please select a valid option.', 'danger')
                return render_template('vote.html', options=options)
            save_vote(selected_option, session['email'])
            flash('Your vote has been recorded. Thank you!', 'success')
            return redirect(url_for('thank_you'))
        return render_template('vote.html', options=options)



    @app.route('/thank-you')
    def thank_you():
        session.clear()
        return render_template('thank_you.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))

else:
    @app.route('/')
    def home():
        return render_template_string('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PnI Voting Portal</title>
</head>
<body>
    <h1 style="text-align: center; margin-top: 50px;">Voting has not started yet</h1>
</body>
</html>''')