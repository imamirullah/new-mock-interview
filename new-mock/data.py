from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt

app = Flask(__name__)

# MongoDB Configuration (Replace with your actual connection string)
app.config["MONGO_URI"] = "mongodb+srv://amiruncodemy:fhievPdPS0IkYRKD@cluster0.cqkwj.mongodb.net/user-data"

print("Connecting to MongoDB...")
mongo = PyMongo(app)  # Initialize PyMongo
bcrypt = Bcrypt(app)

# Ensure the database connection is available before using it
if mongo.db is None:
    print("Failed to connect to MongoDB.")
else:
    print("MongoDB Connected Successfully!")

# Define users collection **after** initializing mongo
users_collection = mongo.db.users  

@app.route('/')
def home():
    return render_template('database.html')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    users_collection.insert_one({
        "username": username,
        "email": email,
        "phone": phone,
        "password": hashed_password
    })

    return jsonify({"message": "User registered successfully"}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({"email": email})

    if user and bcrypt.check_password_hash(user['password'], password):
        return jsonify({"redirect": url_for('app_page')})  # ✅ Return redirect URL in JSON
    else:
        return jsonify({"error": "Invalid credentials"}), 401


@app.route('/app')
def app_page():
    return render_template('app.html')

if __name__ == '__main__':
    app.run(debug=True)
