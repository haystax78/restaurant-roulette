from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import os
import random
import asyncio
from dotenv import load_dotenv
from postgrest import AsyncPostgrestClient
import httpx

load_dotenv()

app = Flask(__name__)

# Initialize PostgREST client
postgrest_url = f"{os.getenv('SUPABASE_URL')}/rest/v1"

async def get_client():
    async with httpx.AsyncClient() as client:
        postgrest = AsyncPostgrestClient(
            base_url=postgrest_url,
            headers={
                "apikey": os.getenv('SUPABASE_KEY'),
                "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}"
            },
            session=client
        )
        return postgrest

async def get_restaurants():
    client = await get_client()
    result = await client.from_("restaurants").select("*").execute()
    return result.data

async def add_restaurant_to_db(name):
    client = await get_client()
    await client.from_("restaurants").insert({
        "name": name,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

async def delete_restaurant_from_db(id):
    client = await get_client()
    await client.from_("restaurants").delete().eq("id", id).execute()

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@app.route('/')
def index():
    restaurants = run_async(get_restaurants())
    return render_template('index.html', restaurants=restaurants)

@app.route('/add', methods=['POST'])
def add_restaurant():
    name = request.form['name']
    run_async(add_restaurant_to_db(name))
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_restaurant(id):
    run_async(delete_restaurant_from_db(id))
    return redirect(url_for('index'))

@app.route('/spin')
def spin_roulette():
    restaurants = run_async(get_restaurants())
    
    if not restaurants:
        return jsonify({'error': 'No restaurants added yet!'})
    
    chosen = random.choice(restaurants)
    return jsonify({
        'name': chosen['name']
    })

if __name__ == '__main__':
    app.run(debug=True)
