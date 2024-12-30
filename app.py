from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import os
import random
from dotenv import load_dotenv
from postgrest import PostgrestClient

load_dotenv()

app = Flask(__name__)

# Initialize PostgREST client
postgrest_url = f"{os.getenv('SUPABASE_URL')}/rest/v1"
postgrest = PostgrestClient(
    base_url=postgrest_url,
    headers={
        "apikey": os.getenv('SUPABASE_KEY'),
        "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}"
    }
)

@app.route('/')
def index():
    # Fetch all restaurants
    restaurants = postgrest.from_("restaurants").select("*").execute().data
    return render_template('index.html', restaurants=restaurants)

@app.route('/add', methods=['POST'])
def add_restaurant():
    name = request.form['name']
    # Insert new restaurant
    postgrest.from_("restaurants").insert({
        "name": name,
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_restaurant(id):
    # Delete restaurant
    postgrest.from_("restaurants").delete().eq("id", id).execute()
    return redirect(url_for('index'))

@app.route('/spin')
def spin_roulette():
    # Get all restaurants
    restaurants = postgrest.from_("restaurants").select("*").execute().data
    
    if not restaurants:
        return jsonify({'error': 'No restaurants added yet!'})
    
    chosen = random.choice(restaurants)
    return jsonify({
        'name': chosen['name']
    })

if __name__ == '__main__':
    app.run(debug=True)
