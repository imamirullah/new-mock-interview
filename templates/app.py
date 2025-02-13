from flask import Flask, request, jsonify, render_template, url_for,session
import google.generativeai as genai
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
import certifi

app = Flask(__name__)

# Gemini API Key (Replace with your own API Key)
genai.configure(api_key="AIzaSyC99R1OssC4kyL16IDCYzTyHq87A0KThUM")

# Initialize Speech Recognition
model = genai.GenerativeModel("gemini-1.5-flash")



app.config["MONGO_URI"] = "mongodb+srv://amiruncodemy:fhievPdPS0IkYRKD@cluster0.cqkwj.mongodb.net/user-data?retryWrites=true&w=majority"
mongo = PyMongo(app, tlsCAFile=certifi.where())

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



@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')

    if users_collection.find_one({"$or" : [{"email": email, "phone": phone}]}):
        return jsonify({"error": "User already registered"}), 400

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

    user = users_collection.find_one({"email": email })

    if user and bcrypt.check_password_hash(user['password'], password):
        return jsonify({"redirect": url_for('app_page')})  # ✅ Return redirect URL in JSON
    else:
        return jsonify({"error": "Invalid credentials"}), 401


 

 
app.secret_key = "sdfghjklfghjfghj"  # Required for session handling

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)  # Remove user session
    return jsonify({"message": "Logged out successfully"})





# Function to generate AI questions
def generate_question(course, level, num_questions):
    questions = []
    for i in range(num_questions):
        prompt = f"Generate a {level} interview level question for {course}.Please don't provide those question which have list and also don't provide same and same question again."
        response = model.generate_content(prompt)
        questions.append(response.text)
        print("question", questions)
    return questions

# Function to check answer and provide correct response
def check_answer(question, user_answer):
    prompt = f"Question: {question}\nUser Answer: {user_answer}\n Is the answer correct? If wrong, give a short correct answer."
    response = model.generate_content(prompt)
    return response.text

# @app.route("/")
# def home():
#     return render_template("app.html")

@app.route('/')
def home():
    return render_template('index.html')



@app.route('/app')
def app_page():
    return render_template('app.html')


@app.route("/quiz", methods=["POST"])
def quiz():
    data = request.json
    print("data aa rha h", data)
    course = data.get("course")
    level = data.get("level")
    
    # Determine number of questions based on level
    if level == "beginner":
        num_questions = 10
    elif level == "intermediate":
        num_questions = 15    #  Increase by 5 for intermediate
    elif level == "advanced":
        num_questions = 20    # Increase by 5 for advanced
    else:
        num_questions = 10    # Default to 10 if level is not defined
    
    questions = generate_question(course, level, num_questions)
    return jsonify({"questions": questions})

@app.route("/answer", methods=["POST"]) 
def answer():
    data = request.json
    question = data.get("question")
    user_answer = data.get("answer")
    feedback = check_answer(question, user_answer)
    return jsonify({"feedback": feedback})


if __name__ == "__main__":
    app.run(debug=True)