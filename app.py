from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import random
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

# Use PostgreSQL URL from environment variable, fall back to SQLite for local development
database_url = os.getenv('DATABASE_URL', 'sqlite:///restaurants.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    restaurants = Restaurant.query.order_by(Restaurant.date_added.desc()).all()
    return render_template('index.html', restaurants=restaurants)

@app.route('/add', methods=['POST'])
def add_restaurant():
    name = request.form['name']
    new_restaurant = Restaurant(name=name)
    db.session.add(new_restaurant)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_restaurant(id):
    restaurant = Restaurant.query.get_or_404(id)
    db.session.delete(restaurant)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/spin')
def spin_roulette():
    restaurants = Restaurant.query.all()
    if not restaurants:
        return jsonify({'error': 'No restaurants added yet!'})
    
    chosen = random.choice(restaurants)
    return jsonify({
        'name': chosen.name
    })

if __name__ == '__main__':
    app.run(debug=True)
