import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, UserMixin, RoleMixin, SQLAlchemyUserDatastore, current_user, login_required, logout_user
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'developerskie')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reviews.db'
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECURITY_PASSWORD_SALT', 'sol-deweloperska')
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False


db = SQLAlchemy(app)

roles_user = db.Table(
    'roles_users',
    db.Column('user_id', db.ForeignKey('user.id')),
    db.Column('role_id', db.ForeignKey('role.id')),
)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    review = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('reviews', lazy=True))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    description = db.Column(db.String(128))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    confirmed_at = db.Column(db.DateTime)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    roles = db.relationship('Role', secondary=roles_user, backref=db.backref('users'))

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        if not self.fs_uniquifier:
            import uuid
            self.fs_uniquifier = str(uuid.uuid4())


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

@app.route("/", methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        title = request.form.get('title')
        review_text = request.form.get('review')
        rating = request.form.get('rating')
        
        new_review = Review(title=title, review=review_text, rating=rating, user_id=current_user.id)
        db.session.add(new_review)
        db.session.commit()
        
        return redirect(url_for('index'))
    
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template("index.html", reviews=reviews)

@app.route("/delete/<int:id>", methods=['POST'])
@login_required
def delete_review(id):
    review = Review.query.get_or_404(id)
    db.session.delete(review)
    db.session.commit()
    return redirect(url_for('index'))


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
