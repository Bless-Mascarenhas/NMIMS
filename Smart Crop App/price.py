from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import random
import os

app = Flask(_name_)
CORS(app)  # Enable CORS for frontend communication

# Database file to store prices (in production, use a proper database like PostgreSQL)
DATA_FILE = 'market_prices.json'

# Initialize sample data structure
def initialize_data():
    """Initialize market data with 30+ vegetables and fruits"""
    
    vegetables = [
        {"name": "Tomato", "icon": "🍅", "base_price": 45},
        {"name": "Potato", "icon": "🥔", "base_price": 25},
        {"name": "Onion", "icon": "🧅", "base_price": 35},
        {"name": "Carrot", "icon": "🥕", "base_price": 40},
        {"name": "Cabbage", "icon": "🥬", "base_price": 30},
        {"name": "Cauliflower", "icon": "🥦", "base_price": 50},
        {"name": "Broccoli", "icon": "🥦", "base_price": 60},
        {"name": "Spinach", "icon": "🥬", "base_price": 35},
        {"name": "Bell Pepper", "icon": "🫑", "base_price": 70},
        {"name": "Cucumber", "icon": "🥒", "base_price": 38},
        {"name": "Eggplant", "icon": "🍆", "base_price": 42},
        {"name": "Pumpkin", "icon": "🎃", "base_price": 28},
        {"name": "Green Beans", "icon": "🫘", "base_price": 55},
        {"name": "Peas", "icon": "🫛", "base_price": 48},
        {"name": "Corn", "icon": "🌽", "base_price": 32},
    ]
    
    fruits = [
        {"name": "Apple", "icon": "🍎", "base_price": 120},
        {"name": "Banana", "icon": "🍌", "base_price": 50},
        {"name": "Orange", "icon": "🍊", "base_price": 80},
        {"name": "Mango", "icon": "🥭", "base_price": 90},
        {"name": "Grapes", "icon": "🍇", "base_price": 100},
        {"name": "Watermelon", "icon": "🍉", "base_price": 35},
        {"name": "Pineapple", "icon": "🍍", "base_price": 65},
        {"name": "Strawberry", "icon": "🍓", "base_price": 150},
        {"name": "Papaya", "icon": "🫐", "base_price": 55},
        {"name": "Pomegranate", "icon": "🍎", "base_price": 110},
        {"name": "Kiwi", "icon": "🥝", "base_price": 180},
        {"name": "Pear", "icon": "🍐", "base_price": 95},
        {"name": "Peach", "icon": "🍑", "base_price": 105},
        {"name": "Lemon", "icon": "🍋", "base_price": 70},
        {"name": "Avocado", "icon": "🥑", "base_price": 140},
    ]
    
    data = {
        "last_updated": datetime.now().isoformat(),
        "items": []
    }
    
    # Generate historical data for each item
    for item_list, item_type in [(vegetables, "vegetables"), (fruits, "fruits")]:
        for item in item_list:
            price_history = generate_price_history(item["base_price"])
            data["items"].append({
                "name": item["name"],
                "type": item_type,
                "icon": item["icon"],
                "current": price_history["current"],
                "yesterday": price_history["yesterday"],
                "week": price_history["week"],
                "month": price_history["month"],
                "year": price_history["year"]
            })
    
    save_data(data)
    return data

def generate_price_history(base_price):
    """Generate realistic price variations"""
    # Current price with small random variation
    current = round(base_price * random.uniform(0.95, 1.05))
    
    # Yesterday: slight variation
    yesterday = round(current * random.uniform(0.97, 1.03))
    
    # Last week: moderate variation
    week = round(current * random.uniform(0.92, 1.08))
    
    # Last month: larger variation
    month = round(current * random.uniform(0.88, 1.12))
    
    # Last year: seasonal variation
    year = round(current * random.uniform(0.80, 1.15))
    
    return {
        "current": current,
        "yesterday": yesterday,
        "week": week,
        "month": month,
        "year": year
    }

def load_data():
    """Load data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return initialize_data()

def save_data(data):
    """Save data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def update_daily_prices():
    """Update prices daily with realistic market fluctuations"""
    data = load_data()
    
    for item in data["items"]:
        # Shift historical prices
        item["year"] = item["month"]
        item["month"] = item["week"]
        item["week"] = item["yesterday"]
        item["yesterday"] = item["current"]
        
        # Generate new current price with realistic variation
        change_percent = random.uniform(-0.05, 0.05)  # -5% to +5% daily change
        item["current"] = round(item["current"] * (1 + change_percent))
        
        # Ensure prices don't go too low
        if item["current"] < 10:
            item["current"] = 10
    
    data["last_updated"] = datetime.now().isoformat()
    save_data(data)
    return data

# API Routes

@app.route('/api/prices', methods=['GET'])
def get_prices():
    """Get all market prices"""
    data = load_data()
    return jsonify(data)

@app.route('/api/prices/<item_name>', methods=['GET'])
def get_item_price(item_name):
    """Get price for a specific item"""
    data = load_data()
    item = next((i for i in data["items"] if i["name"].lower() == item_name.lower()), None)
    
    if item:
        return jsonify(item)
    return jsonify({"error": "Item not found"}), 404

@app.route('/api/update', methods=['POST'])
def update_prices():
    """Manually trigger price update (for testing)"""
    data = update_daily_prices()
    return jsonify({
        "message": "Prices updated successfully",
        "last_updated": data["last_updated"]
    })

@app.route('/api/filter', methods=['GET'])
def filter_items():
    """Filter items by type or price change"""
    data = load_data()
    
    item_type = request.args.get('type')  # vegetables, fruits
    change = request.args.get('change')    # gaining, losing
    
    filtered_items = data["items"]
    
    if item_type and item_type in ['vegetables', 'fruits']:
        filtered_items = [i for i in filtered_items if i["type"] == item_type]
    
    if change == 'gaining':
        filtered_items = [i for i in filtered_items if i["current"] > i["yesterday"]]
    elif change == 'losing':
        filtered_items = [i for i in filtered_items if i["current"] < i["yesterday"]]
    
    return jsonify({
        "items": filtered_items,
        "count": len(filtered_items)
    })

@app.route('/api/search', methods=['GET'])
def search_items():
    """Search items by name"""
    query = request.args.get('q', '').lower()
    data = load_data()
    
    results = [i for i in data["items"] if query in i["name"].lower()]
    
    return jsonify({
        "items": results,
        "count": len(results)
    })

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get market statistics"""
    data = load_data()
    
    gaining = sum(1 for i in data["items"] if i["current"] > i["yesterday"])
    losing = sum(1 for i in data["items"] if i["current"] < i["yesterday"])
    stable = sum(1 for i in data["items"] if i["current"] == i["yesterday"])
    
    avg_change = sum((i["current"] - i["yesterday"]) / i["yesterday"] * 100 
                     for i in data["items"]) / len(data["items"])
    
    return jsonify({
        "total_items": len(data["items"]),
        "gaining": gaining,
        "losing": losing,
        "stable": stable,
        "average_change_percent": round(avg_change, 2),
        "last_updated": data["last_updated"]
    })

@app.route('/')
def index():
    """API information"""
    return jsonify({
        "name": "Market Price Tracker API",
        "version": "1.0",
        "endpoints": {
            "/api/prices": "Get all market prices",
            "/api/prices/<item_name>": "Get specific item price",
            "/api/update": "Manually update prices",
            "/api/filter?type=vegetables&change=gaining": "Filter items",
            "/api/search?q=tomato": "Search items",
            "/api/statistics": "Get market statistics"
        }
    })

if _name_ == '_main_':
    # Initialize data if not exists
    if not os.path.exists(DATA_FILE):
        initialize_data()
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)