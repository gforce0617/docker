from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    questions_text = db.Column(db.String(200), nullable=False)
    answer_text = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, questions_text, answer_text):
        self.questions_text = questions_text
        self.answer_text = answer_text


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        questions_number = int(request.form['questions_number'])
        print(questions_number)
        for i in range(questions_number):
            response = requests.get('https://opentdb.com/api.php?amount=1')
            buff = response.json()
            buff = buff["results"][0]
            questions_text = buff['question']
            answer_text = buff['correct_answer']

            if Questions.query.filter_by(questions_text=questions_text).first() is None:
                question = Questions(questions_text=questions_text, answer_text=answer_text)
                try:
                    db.session.add(question)
                    db.session.commit()
                    ques = Questions.query.all()
                except:
                    return render_template("index.html")
        answer = {
            "id": Questions.query.all()[-questions_number-1].id,
            "questions_text": Questions.query.all()[-questions_number-1].questions_text,
            "answer_text": Questions.query.all()[-questions_number-1].answer_text,
            "date": Questions.query.all()[-questions_number-1].date
        }
        return answer
    else:
        return render_template("index.html")


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
