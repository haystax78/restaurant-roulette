from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import os
import random
import asyncio
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

async def get_restaurants():
    result = await postgrest.from_("restaurants").select("*").execute()
    return result.data

async def add_restaurant_to_db(name):
    await postgrest.from_("restaurants").insert({
        "name": name,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

async def delete_restaurant_from_db(id):
    await postgrest.from_("restaurants").delete().eq("id", id).execute()

@app.route('/')
def index():
    restaurants = asyncio.run(get_restaurants())
    return render_template('index.html', restaurants=restaurants)

@app.route('/add', methods=['POST'])
def add_restaurant():
    name = request.form['name']
    asyncio.run(add_restaurant_to_db(name))
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_restaurant(id):
    asyncio.run(delete_restaurant_from_db(id))
    return redirect(url_for('index'))

@app.route('/spin')
def spin_roulette():
    restaurants = asyncio.run(get_restaurants())
    
    if not restaurants:
        return jsonify({'error': 'No restaurants added yet!'})
    
    chosen = random.choice(restaurants)
    return jsonify({
        'name': chosen['name']
    })

if __name__ == '__main__':
    app.run(debug=True)
