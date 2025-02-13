
function startVideo() {
    const videoContainer = document.getElementById('videoContainer')
    const cameraFeed = document.getElementById('cameraFeed')
    document.getElementById('form-group').style.display = 'none'
    document.getElementById('level').style.display = 'none'
    document.getElementById('start').style.display = 'none'
    document.getElementById('heading').style.display = 'none'
    document.getElementById('right-card').style.display = 'none'
    document.getElementById('left').style.display = 'none'
    document.getElementById('right').style.width = '100vw'
    document.getElementById('getQuestion').style.display = 'block'
    document.getElementById('logout-btn').style.display = 'block'

    navigator.mediaDevices
        .getUserMedia({ video: true })
        .then((stream) => {
            cameraFeed.srcObject = stream
            videoContainer.style.display = 'block' // Show the card
        })
        .catch((error) => {
            console.error('Error accessing the camera:', error)
        })
}

function moveVideo() {
    document.getElementById('videoContainer').classList.add('move-top-right')

    // Delay showing 'checkAnswer' by 2 seconds (2000ms)
    setTimeout(() => {
        document.getElementById('checkAnswer').style.display = 'block'
        document.getElementById('anser').style.display = 'block'
        document.getElementById('questionText').style.display = 'block'
    }, 2000)
}

// Speech Recognition Setup
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)()
recognition.lang = 'en-US'
recognition.interimResults = false
recognition.maxAlternatives = 1

// Speech Synthesis Setup (Female Voice)
const synth = window.speechSynthesis
const voices = synth.getVoices()
let femaleVoice = voices.find((voice) => voice.name.includes('female')) || voices[0]

function speakText(text) {
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.voice = femaleVoice
    synth.speak(utterance)
}

document.getElementById('nextQuestion').addEventListener('click', function () {
    // Stop speech synthesis before moving to the next question
    synth.cancel()

    // Clear user input field
    document.getElementById('userAnswer').value = ''

    // Hide feedback message when moving to the next question
    document.getElementById('feedback').textContent = ''
    document.getElementById('feedback').style.display = 'none'
})

document.getElementById('getQuestion').addEventListener('click', function () {
    const course = document.getElementById('course').value
    const level = document.getElementById('level').value
    const loader = document.getElementById('loader') // Get the loader element
    const questionText = document.getElementById('questionText') // Question display element
    const nextQuestionBtn = document.getElementById('nextQuestion') // Next button
    document.getElementById('nextQuestion').style.display = 'block'
    document.getElementById('img').style.display = 'none'

    // Show loader and clear previous question
    loader.style.display = 'block'
    questionText.textContent = ''
    nextQuestionBtn.style.display = 'none' // Hide next button initially

    fetch('/quiz', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ course: course, level: level })
    })
        .then((response) => response.json())
        .then((data) => {
            loader.style.display = 'none' // Hide loader after fetching
            const questions = data.questions
            let questionIndex = 0

            function showNextQuestion() {
                if (questionIndex < questions.length) {
                    questionText.textContent = questions[questionIndex]
                    speakText(questions[questionIndex])
                    questionIndex++
                } else {
                    questionText.textContent = 'No more questions.'
                    nextQuestionBtn.style.display = 'none' // Hide button when no more questions
                }
            }

            showNextQuestion()
            nextQuestionBtn.style.display = 'block' // Show next button
            nextQuestionBtn.addEventListener('click', showNextQuestion)
        })
        .catch((error) => {
            loader.style.display = 'none' // Hide loader on error
            questionText.textContent = 'Failed to load question.'
            console.error('Error fetching questions:', error)
        })
})

document.getElementById('checkAnswer').addEventListener('click', function () {
    const speakInstruction = document.getElementById('speakInstruction')
    speakInstruction.textContent = 'Please speak your answer...'
    speakInstruction.style.display = 'block'

    // Speak the instruction aloud
    speakText('Please speak your answer')

    // Start speech recognition
    recognition.continuous = false // Ensure it stops after one result
    recognition.interimResults = false // Get only final result
    recognition.start()

    recognition.onresult = function (event) {
        const userAnswer = event.results[0][0].transcript
        document.getElementById('userAnswer').value = userAnswer

        const question = document.getElementById('questionText').textContent

        // Stop recognition before processing answer
        recognition.stop()

        fetch('/answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: question, answer: userAnswer })
        })
            .then((response) => response.json())
            .then((data) => {
                const feedback = data.feedback
                document.getElementById('feedback').textContent = feedback
                document.getElementById('feedback').style.display = 'block'

                // Speak the correct answer feedback
                speakText(feedback)

                // Hide instruction after getting answer
                speakInstruction.style.display = 'none'
            })
            .catch((error) => {
                console.error('Error submitting answer:', error)
            })
    }

    recognition.onerror = function (event) {
        alert('Error occurred in recognition: ' + event.error)
    }
})

window.onload = function () {
    // Stop any ongoing speech synthesis on page refresh
    synth.cancel()

    // Stop speech recognition if it was running
    if (recognition && recognition.stop) {
        recognition.stop()
    }
}