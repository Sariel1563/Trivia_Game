from flask import Flask, request, render_template, redirect, url_for, session
import uuid
import random
import math

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Global variables to hold game data
scores = {}  # {question_uuid: [predictions]}
entries = {}  # {user_uuid: {question_uuid: guess}}
questions = [
    ("What is 1+1?", "2"),
    ("What is the capital of France?", "Paris"),
    ("What is 3*3?", "9")
]
answers = [1, 1, 1]  # Simulated answers where GPT-4 got all these right

@app.route('/home')
def home():
    # Start the session for a new user
    user_id = str(uuid.uuid4())
    session['user_id'] = user_id
    entries[user_id] = {}
    return render_template('home.html', user_id=user_id)

@app.route('/question')
def question():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('home'))

    question_id = request.args.get('id')
    if not question_id or question_id not in [str(i) for i in range(len(questions))]:
        return redirect(url_for('home'))

    question_index = int(question_id)
    question, expected_answer = questions[question_index]

    return render_template('question.html', question=question, question_id=question_id)

@app.route('/score', methods=['POST'])
def score():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('home'))

    # Retrieve the data from the POST request
    question_id = request.form['id']
    guess = float(request.form['guess'])

    question_index = int(question_id)
    correct_answer = answers[question_index]  # Simulated GPT-4 response: 1 for correct, 0 for incorrect
    
    # Store the guess in the global scores and entries dictionaries
    if question_id not in scores:
        scores[question_id] = []
    scores[question_id].append(guess)

    if user_id not in entries:
        entries[user_id] = {}
    entries[user_id][question_id] = guess

    # Calculate log loss for this question
    log_loss = - (correct_answer * math.log(guess) + (1 - correct_answer) * math.log(1 - guess))

    # Calculate comparison to other users
    all_scores = scores[question_id]
    average_log_loss = sum([- (correct_answer * math.log(p) + (1 - correct_answer) * math.log(1 - p)) for p in all_scores]) / len(all_scores)

    return render_template('score.html', log_loss=log_loss, average_log_loss=average_log_loss, correct_answer=correct_answer)

@app.route('/next_question')
def next_question():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('home'))

    # Check the last answered question and get the next one
    user_entries = entries.get(user_id, {})
    if not user_entries:
        next_question_id = 0
    else:
        last_question_id = max(int(q_id) for q_id in user_entries.keys())
        next_question_id = last_question_id + 1
    
    if next_question_id >= len(questions):
        return "Game Over! You've completed all the questions."
    
    return redirect(url_for('question', id=str(next_question_id)))

if __name__ == '__main__':
    app.run(debug=True)
