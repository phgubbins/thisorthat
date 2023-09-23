from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS 
import random

app = Flask(__name__)
CORS(app) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///votes.db'
app.config['WTF_CSRF_ENABLED'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    votes = db.relationship('Vote', backref='option', lazy=True)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    option_id = db.Column(db.Integer, db.ForeignKey('option.id'), nullable=False)
    value = db.Column(db.Integer, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vote', methods=['POST'])
def vote():
    data = request.json
    selected_option_id = data['selected_option_id']
    non_selected_option_id = data['non_selected_option_id']

    # Record a positive vote for the selected option
    selected_vote = Vote(option_id=selected_option_id, value=100)
    db.session.add(selected_vote)
    
    # Record a negative vote for the non-selected option
    non_selected_vote = Vote(option_id=non_selected_option_id, value=-100)
    db.session.add(non_selected_vote)

    db.session.commit()

    return jsonify({"message": f"You voted for option {selected_option_id}!"})

@app.route('/user_add_option', methods=['POST'])
def user_add_option():
    data = request.json
    existing_option = Option.query.filter_by(name=data['name']).first()
    if existing_option:
        return jsonify({"message": "Option already exists!"}), 400
    new_option = Option(name=data['name'])
    db.session.add(new_option)
    db.session.commit()
    return jsonify({"message": "Option added successfully!"}), 201

@app.route('/scores', methods=['GET'])
def scores():
    options = Option.query.all()
    scores = {}
    for option in options:
        total_value = sum(vote.value for vote in option.votes)
        average_value = total_value / len(option.votes) if option.votes else 0
        scores[option.name] = average_value
    sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))
    return render_template('results.html', scores=sorted_scores)

@app.route('/random_options', methods=['GET'])
def random_options():
    options = Option.query.all()
    option1, option2 = random.sample(options, 2)
    return jsonify({option1.id: option1.name, option2.id: option2.name})

if __name__ == "__main__":
    app.run(debug=True)
