import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'developerskie')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reviews.db'


db = SQLAlchemy(app)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    review = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form.get('title')
        review_text = request.form.get('review')
        rating = request.form.get('rating')
        
        new_review = Review(title=title, review=review_text, rating=rating)
        db.session.add(new_review)
        db.session.commit()
        
        return redirect(url_for('index'))
    
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template("index.html", reviews=reviews)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
