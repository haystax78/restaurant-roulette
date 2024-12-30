from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from datetime import datetime
import os
import random
import asyncio
from dotenv import load_dotenv
from postgrest import AsyncPostgrestClient
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')  # Change this to a secure key
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'your-password-here')  # Change this to your desired password

# Initialize PostgREST client
postgrest_url = f"{os.getenv('SUPABASE_URL')}/rest/v1"
client = AsyncPostgrestClient(
    base_url=postgrest_url,
    headers={
        "apikey": os.getenv('SUPABASE_KEY'),
        "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}"
    }
)

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('authenticated'):
            flash('Please login first', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

async def get_restaurants():
    result = await client.from_("restaurants").select("*").execute()
    return result.data

async def add_restaurant_to_db(name):
    await client.from_("restaurants").insert({
        "name": name,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

async def delete_restaurant_from_db(id):
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
    return render_template('index.html', restaurants=restaurants, authenticated=session.get('authenticated', False))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == ADMIN_PASSWORD:
            session['authenticated'] = True
            flash('Successfully logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    flash('Successfully logged out!', 'success')
    return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
@requires_auth
def add_restaurant():
    name = request.form['name']
    run_async(add_restaurant_to_db(name))
    flash('Restaurant added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
@requires_auth
def delete_restaurant(id):
    run_async(delete_restaurant_from_db(id))
    flash('Restaurant deleted successfully!', 'success')
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
