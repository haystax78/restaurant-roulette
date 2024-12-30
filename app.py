from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import os
import random
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

app = Flask(__name__)

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

@app.route('/')
def index():
    # Fetch all restaurants
    response = supabase.table('restaurants').select('*').execute()
    restaurants = response.data
    return render_template('index.html', restaurants=restaurants)

@app.route('/add', methods=['POST'])
def add_restaurant():
    name = request.form['name']
    # Insert new restaurant
    supabase.table('restaurants').insert({
        'name': name,
        'created_at': datetime.utcnow().isoformat()
    }).execute()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_restaurant(id):
    # Delete restaurant
    supabase.table('restaurants').delete().eq('id', id).execute()
    return redirect(url_for('index'))

@app.route('/spin')
def spin_roulette():
    # Get all restaurants
    response = supabase.table('restaurants').select('*').execute()
    restaurants = response.data
    
    if not restaurants:
        return jsonify({'error': 'No restaurants added yet!'})
    
    chosen = random.choice(restaurants)
    return jsonify({
        'name': chosen['name']
    })

if __name__ == '__main__':
    app.run(debug=True)
