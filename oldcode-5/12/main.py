from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import google.generativeai as genai
from fpdf import FPDF
import pyttsx3
import datetime
import os
import speech_recognition as sr
import threading

app = Flask(__name__)
CORS(app)  # Allow frontend to access backend

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Set to female voice

# Function to make the system speak
def speak(text):
    engine.say(text)
    engine.runAndWait()
    
    threading.Thread(target=run, daemon=True).start()

# Configure Google AI model
genai.configure(api_key="AIzaSyDXElDtxbr05w8k79oTlmryYOhRLfhCOZM")

# Initialize Speech Recognition
model = genai.GenerativeModel("gemini-1.5-flash")
recognizer = sr.Recognizer()

def get_voice_input():
    """Capture voice input and convert to text."""
    with sr.Microphone() as source:
        print("Listening for your answer...")
        speak("Please answer the question.")
        recognizer.adjust_for_ambient_noise(source)
        
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower().strip()
        except sr.UnknownValueError:
            speak("Sorry, I couldn't understand your response.")
            return ""
        except sr.RequestError:
            speak("There was an issue with the speech recognition service.")
            return ""

course_prompts = {
    "software testing": {
        "beginner": "Generate a beginner-level software testing question.",
        "intermediate": "Generate an intermediate-level software testing question.",
        "advanced": "Generate an advanced-level software testing question."
    },
    "data science": {
        "beginner": "Generate a beginner-level Data Science question.",
        "intermediate": "Generate an intermediate-level Data Science question.",
        "advanced": "Generate an advanced-level Data Science question."
    }
}

correct_answers = {
    "software testing": {
        "beginner": "Correct answer for beginner software testing",
        "intermediate": "Correct answer for intermediate software testing",
        "advanced": "Correct answer for advanced software testing"
    },
    "data science": {
        "beginner": "Correct answer for beginner Data Science",
        "intermediate": "Correct answer for intermediate Data Science",
        "advanced": "Correct answer for advanced Data Science"
    }
}

def generate_question(prompt):
    """Generate a question using Google Generative AI."""
    try:
        response = model.generate_content(prompt)
        question = response.text.strip()
        return question
    except Exception as e:
        print("Error generating question:", e)
        return f"Error generating question: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')  # Ensure 'templates/voice.html' exists



@app.route("/generate_questions", methods=["POST"])
def generate_questions():
    """Generate and speak interview questions."""
    try:
        data = request.json
        course = data.get("course", "").lower()
        level = data.get("level", "").lower()
        num_questions = int(data.get("num_questions", 5))

        if course not in course_prompts or level not in course_prompts[course]:
            return jsonify({"error": "Invalid course or level"}), 400

        prompt = course_prompts[course][level]
        questions = [generate_question(prompt) for _ in range(num_questions)]
        
        def speak_questions():
            for question in questions:
                speak(question)
        
        thread = threading.Thread(target=speak_questions)
        thread.start()
        
        return jsonify({"questions": questions})
        speak(question)  # Speak the question after generating it


    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/check_answers", methods=["POST"])
def check_answers():
    """Check user answers against predefined correct answers."""
    try:
        data = request.json
        course = data.get("course", "").lower()
        level = data.get("level", "").lower()
        user_answers = data.get("answers", [])

        correct_answer = correct_answers.get(course, {}).get(level, "")
        correct_count = sum(1 for ans in user_answers if ans.strip().lower() == correct_answer.strip().lower())
        incorrect_count = len(user_answers) - correct_count

        return jsonify({
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "total_questions": len(user_answers)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/generate_report", methods=["POST"])
def generate_report():
    """Generate a PDF report of interview results."""
    try:
        data = request.json
        course = data.get("course", "").capitalize()
        level = data.get("level", "").capitalize()
        correct_count = data.get("correct_count", 0)
        incorrect_count = data.get("incorrect_count", 0)
        total_questions = data.get("total_questions", 0)

        # Ensure reports directory exists
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)

        # Generate a unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = os.path.join(reports_dir, f"interview_report_{timestamp}.pdf")

        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt=f"Interview Report for {course} - {level} Level", ln=True, align="C")
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Correct Answers: {correct_count}", ln=True)
        pdf.cell(200, 10, txt=f"Incorrect Answers: {incorrect_count}", ln=True)
        pdf.ln(10)

        percentage = (correct_count / total_questions) * 100 if total_questions else 0
        pdf.cell(200, 10, txt=f"Percentage Correct: {percentage:.2f}%", ln=True)

        pdf.output(pdf_filename)
        return jsonify({"message": "PDF generated", "filename": pdf_filename})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download_report/<filename>", methods=["GET"])
def download_report(filename):
    """Allow users to download the generated PDF report."""
    try:
        file_path = os.path.join("reports", filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/voice_interaction", methods=["POST"])
def voice_interaction():
    """Ask a question and capture the user's answer via voice."""
    try:
        data = request.json
        course = data.get("course", "").lower()
        level = data.get("level", "").lower()

        if course not in course_prompts or level not in course_prompts[course]:
            return jsonify({"error": "Invalid course or level"}), 400

        prompt = course_prompts[course][level]
        question = generate_question(prompt)
        answer = get_voice_input()

        return jsonify({"question": question, "answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
