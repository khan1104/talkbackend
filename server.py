#main server file
from flask import Flask, request, jsonify
import smtplib
import secrets
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd

import googletrans

app = Flask(__name__)

file_paths = [
    "C:/Hackathon/en.csv",
    "C:/Hackathon/es.csv",
    "C:/Hackathon/fr.csv",
    "C:/Hackathon/hindi_bad_words.csv",
]

# Load all bad words into a set
bad_words_set = set()

for file in file_paths:
    try:
        df = pd.read_csv(file, header=None, names=['bad_word'], encoding="utf-8")
        bad_words_set.update(df['bad_word'].astype(str).str.lower().str.strip())  # Convert words to lowercase & strip spaces
    except Exception as e:
        print(f"Error loading {file}: {e}")

print(f"🔥 Loaded {len(bad_words_set)} bad words across multiple languages.")

# Function to censor bad words
def censor_message(message):
    words = message.split()
    censored_words = []

    for word in words:
        lowercase_word = word.lower()
        censored_word = word

        for bad_word in bad_words_set:
            if bad_word in lowercase_word:
                censored_word = lowercase_word.replace(bad_word, '*' * len(bad_word))

        censored_words.append(censored_word)

    return ' '.join(censored_words)

# In-memory storage for OTPs (in a real application, use a database)
otp_storage = {}

def generate_otp(length=6):
    """Generate a secure OTP."""
    return ''.join(secrets.choice('0123456789') for _ in range(length))

def send_email(subject, body, to_email, from_email, smtp_server, smtp_port, username, password):
    """Send an email using SMTP."""
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  
        server.login(username, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.json
    to_email = data.get('mail')
    if not to_email:
        return jsonify({'error': 'Email is required'}), 400
    
    # Generate OTP
    otp = generate_otp()
    
    # Store OTP
    otp_storage[to_email] = {'otp': otp}
    
    # Email settings
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    username = '<your gmail id>'
    password = 'your app password'
    from_email = username
    subject = 'Your OTP Code'
    body = f'Hello, your OTP code is {otp}.'
    
    # Send OTP email
    send_email(subject, body, to_email, from_email, smtp_server, smtp_port, username, password)
    
    return jsonify({'message':otp}), 200
#translation part
@app.route('/trans', methods=['POST'])
def receive_data():
    
    data = request.json
    
    
    if 'targetlan' in data and 'msg' in data:
        targetlan = data['targetlan']
        msg = data['msg']
        translator=googletrans.Translator()
        translation=translator.translate(msg,dest=targetlan)
        return jsonify({"translated": translation.text}), 200
    else:
        return jsonify({"error": "Invalid data"}), 400


@app.route("/censor", methods=["POST"])
def censor_api():
    data = request.get_json()
    
    if "message" not in data:
        return jsonify({"error": "Message field is required"}), 400
    
    original_message = data["message"]
    censored_message = censor_message(original_message)
    
    return jsonify({
        # "original": original_message,
        "censored": censored_message
    })

if __name__ == '__main__':
    app.run(debug=True,host="192.168.190.3",threaded=True) #replace with your actuall ip address
