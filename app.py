from flask import Flask, request, jsonify, render_template
import google.generativeai as genai

app = Flask(__name__)

# Gemini API Key (Replace with your own API Key)
genai.configure(api_key="AIzaSyAiaHQLk6jhZDR5HJ8PI9M1XWVncAh-Z_o")

# Initialize Speech Recognition
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to generate AI questions
def generate_question(course, level, num_questions):
    questions = []
    for i in range(num_questions):
        prompt = f"Generate a {level} interview level question for {course}."
        response = model.generate_content(prompt)
        questions.append(response.text)
        print("question", questions)
    return questions

# Function to check answer and provide correct response
def check_answer(question, user_answer):
    prompt = f"Question: {question}\nUser Answer: {user_answer}\n Is the answer correct? If wrong, give a short correct answer."
    response = model.generate_content(prompt)
    return response.text

@app.route("/")
def home():
    return render_template("app.html")

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
        num_questions = 15  # Increase by 5 for intermediate
    elif level == "advanced":
        num_questions = 20  # Increase by 5 for advanced
    else:
        num_questions = 10  # Default to 10 if level is not defined
    
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
