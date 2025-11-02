# app.py - Flask Backend
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import base64
import json
import requests
from datetime import datetime
import heatmap as heatmap_module

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Weather API Key (OpenWeatherMap - Free tier)
WEATHER_API_KEY = "your_api_key_here"  # Get free key from openweathermap.org

# Crop recommendation database based on soil type, pH, season, and region
CROP_DATABASE = {
    "Punjab": {
        "Kharif": {
            "Clay": {"crops": ["Rice", "Cotton", "Maize"], "ph_range": [6.0, 7.5], "water": "high"},
            "Loamy": {"crops": ["Rice", "Sugarcane", "Maize", "Cotton"], "ph_range": [6.5, 7.5], "water": "high"},
            "Sandy": {"crops": ["Bajra", "Groundnut", "Maize"], "ph_range": [6.0, 7.0], "water": "medium"}
        },
        "Rabi": {
            "Clay": {"crops": ["Wheat", "Mustard", "Gram"], "ph_range": [6.5, 7.5], "water": "medium"},
            "Loamy": {"crops": ["Wheat", "Barley", "Mustard", "Potato"], "ph_range": [6.5, 7.5], "water": "medium"},
            "Sandy": {"crops": ["Wheat", "Barley", "Gram"], "ph_range": [6.0, 7.0], "water": "low"}
        }
    },
    "Uttar Pradesh": {
        "Kharif": {
            "Clay": {"crops": ["Rice", "Sugarcane", "Cotton"], "ph_range": [6.0, 7.5], "water": "high"},
            "Loamy": {"crops": ["Rice", "Sugarcane", "Maize", "Soybean"], "ph_range": [6.5, 7.5], "water": "high"},
            "Sandy": {"crops": ["Bajra", "Maize", "Groundnut"], "ph_range": [6.0, 7.0], "water": "medium"}
        },
        "Rabi": {
            "Clay": {"crops": ["Wheat", "Potato", "Mustard"], "ph_range": [6.5, 7.5], "water": "medium"},
            "Loamy": {"crops": ["Wheat", "Potato", "Peas", "Mustard"], "ph_range": [6.5, 7.5], "water": "medium"},
            "Sandy": {"crops": ["Wheat", "Gram", "Barley"], "ph_range": [6.0, 7.0], "water": "low"}
        }
    },
    "Maharashtra": {
        "Kharif": {
            "Clay": {"crops": ["Cotton", "Soybean", "Sorghum"], "ph_range": [6.0, 7.5], "water": "medium"},
            "Loamy": {"crops": ["Cotton", "Soybean", "Sugarcane", "Sorghum"], "ph_range": [6.5, 7.5], "water": "high"},
            "Sandy": {"crops": ["Bajra", "Groundnut", "Sorghum"], "ph_range": [6.0, 7.0], "water": "low"}
        },
        "Rabi": {
            "Clay": {"crops": ["Wheat", "Gram", "Onion"], "ph_range": [6.5, 7.5], "water": "medium"},
            "Loamy": {"crops": ["Wheat", "Onion", "Gram", "Jowar"], "ph_range": [6.5, 7.5], "water": "medium"},
            "Sandy": {"crops": ["Jowar", "Gram", "Groundnut"], "ph_range": [6.0, 7.0], "water": "low"}
        }
    }
}

# Crop yield estimates (quintals per acre)
CROP_YIELDS = {
    "Rice": {"yield": 20, "price_per_quintal": 2000},
    "Wheat": {"yield": 18, "price_per_quintal": 2100},
    "Cotton": {"yield": 12, "price_per_quintal": 5500},
    "Sugarcane": {"yield": 350, "price_per_quintal": 350},
    "Maize": {"yield": 22, "price_per_quintal": 1800},
    "Soybean": {"yield": 12, "price_per_quintal": 4000},
    "Bajra": {"yield": 15, "price_per_quintal": 1700},
    "Groundnut": {"yield": 15, "price_per_quintal": 5000},
    "Mustard": {"yield": 10, "price_per_quintal": 5500},
    "Gram": {"yield": 8, "price_per_quintal": 5000},
    "Potato": {"yield": 150, "price_per_quintal": 1000},
    "Onion": {"yield": 200, "price_per_quintal": 1500},
    "Barley": {"yield": 16, "price_per_quintal": 1600},
    "Sorghum": {"yield": 18, "price_per_quintal": 1900},
    "Jowar": {"yield": 17, "price_per_quintal": 1800},
    "Peas": {"yield": 10, "price_per_quintal": 3000}
}

# Disease symptoms database
DISEASE_SYMPTOMS = {
    "leaf_spots": ["Fungal infection", "Apply fungicide", "Remove affected leaves"],
    "yellowing": ["Nutrient deficiency", "Apply nitrogen fertilizer", "Check soil pH"],
    "wilting": ["Water stress or root disease", "Check irrigation", "Improve drainage"],
    "brown_patches": ["Bacterial blight", "Use copper-based spray", "Ensure proper spacing"],
    "holes_in_leaves": ["Pest infestation", "Apply organic pesticide", "Use neem oil"]
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_weather_data(region):
    """Fetch weather data from OpenWeatherMap API"""
    try:
        # Map regions to cities
        city_map = {
            "Punjab": "Ludhiana",
            "Uttar Pradesh": "Lucknow",
            "Maharashtra": "Pune"
        }
        city = city_map.get(region, "Delhi")
        
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"]
            }
    except:
        pass
    
    # Return mock data if API fails
    return {
        "temperature": 28,
        "humidity": 65,
        "description": "partly cloudy"
    }

def analyze_crop_recommendation(data):
    """Analyze input data and recommend crops"""
    region = data.get('region')
    soil_type = data.get('soil_type')
    season = data.get('season')
    water_availability = data.get('water_availability')
    ph = float(data.get('ph', 7.0))
    acres = float(data.get('acres', 1))
    budget = float(data.get('budget', 10000))
    
    # Get suitable crops based on region, season, and soil type
    suitable_crops = []
    
    if region in CROP_DATABASE and season in CROP_DATABASE[region]:
        soil_data = CROP_DATABASE[region][season].get(soil_type, {})
        crops = soil_data.get('crops', [])
        ph_range = soil_data.get('ph_range', [6.0, 7.5])
        required_water = soil_data.get('water', 'medium')
        
        # Filter crops based on pH
        for crop in crops:
            ph_suitable = ph_range[0] <= ph <= ph_range[1]
            water_suitable = (
                (water_availability == 'High' and required_water in ['high', 'medium', 'low']) or
                (water_availability == 'Medium' and required_water in ['medium', 'low']) or
                (water_availability == 'Low' and required_water == 'low')
            )
            
            if ph_suitable and water_suitable:
                yield_data = CROP_YIELDS.get(crop, {"yield": 10, "price_per_quintal": 2000})
                total_yield = yield_data['yield'] * acres
                estimated_revenue = total_yield * yield_data['price_per_quintal']
                cost_per_acre = budget / acres if acres > 0 else budget
                profit = estimated_revenue - budget
                roi = (profit / budget * 100) if budget > 0 else 0
                
                suitable_crops.append({
                    "name": crop,
                    "yield_per_acre": yield_data['yield'],
                    "total_yield": total_yield,
                    "price_per_quintal": yield_data['price_per_quintal'],
                    "estimated_revenue": estimated_revenue,
                    "profit": profit,
                    "roi": round(roi, 2),
                    "suitability_score": round(85 + (roi / 100), 2)
                })
    
    # Sort by ROI
    suitable_crops.sort(key=lambda x: x['roi'], reverse=True)
    
    return suitable_crops

def analyze_disease(description, image_path=None):
    """Analyze disease symptoms from description and image"""
    recommendations = []
    description_lower = description.lower()
    
    # Check for symptoms in description
    for symptom, advice in DISEASE_SYMPTOMS.items():
        if any(word in description_lower for word in symptom.split('_')):
            recommendations.extend(advice)
    
    if not recommendations:
        recommendations = [
            "No specific disease detected",
            "Ensure proper irrigation and fertilization",
            "Monitor crop regularly"
        ]
    
    return list(set(recommendations))  # Remove duplicates

@app.route('/')
def index():
    # Serve the dashboard HTML directly from the project root
    return send_from_directory('.', 'main.html')


@app.route('/planner')
def planner():
    # Serve the crop planner HTML
    return send_from_directory('.', 'crop_planner.html')


@app.route('/heatmap')
def heatmap_page():
    # Serve the full heatmap page as its own route
    return send_from_directory('.', 'heatmap.html')


@app.route('/weather')
def weather_page():
    # Serve the weather HTML page (static HTML in project root)
    # The supplied weather.html uses relative static links so we can send the file directly.
    return send_from_directory('.', 'weather.html')


@app.route('/schemes')
def schemes_page():
    # Serve the government schemes page
    return send_from_directory('.', 'schemes.html')


@app.route('/advisory')
def advisory_page():
    # Serve market/advisory page
    return send_from_directory('.', 'advisory.html')


@app.route('/disease')
def disease_page():
    # Serve the disease detection UI
    return send_from_directory('.', 'disease.html')


@app.route('/api/market-prices', methods=['GET'])
def api_market_prices():
    """Return mocked market prices. Supports optional ?commodity= and ?state="""
    try:
        commodity = (request.args.get('commodity') or '').strip().lower()
        state = (request.args.get('state') or '').strip()

        # Mocked dataset
        base = [
            {'commodity': 'Wheat', 'mandi': 'Ludhiana Mandi', 'state': 'Punjab', 'price': 2150, 'unit': 'quintal', 'updated': datetime.now().strftime('%Y-%m-%d %H:%M')},
            {'commodity': 'Rice', 'mandi': 'Pune Mandi', 'state': 'Maharashtra', 'price': 1950, 'unit': 'quintal', 'updated': datetime.now().strftime('%Y-%m-%d %H:%M')},
            {'commodity': 'Maize', 'mandi': 'Lucknow Mandi', 'state': 'Uttar Pradesh', 'price': 1800, 'unit': 'quintal', 'updated': datetime.now().strftime('%Y-%m-%d %H:%M')},
            {'commodity': 'Wheat', 'mandi': 'Amritsar Mandi', 'state': 'Punjab', 'price': 2120, 'unit': 'quintal', 'updated': datetime.now().strftime('%Y-%m-%d %H:%M')},
            {'commodity': 'Cotton', 'mandi': 'Nagpur Mandi', 'state': 'Maharashtra', 'price': 5600, 'unit': 'quintal', 'updated': datetime.now().strftime('%Y-%m-%d %H:%M')}
        ]

        filtered = []
        for r in base:
            if commodity and commodity not in r['commodity'].lower():
                continue
            if state and state.lower() != 'all' and state != r['state']:
                continue
            filtered.append(r)

        # If nothing matched and no filters, return base
        out = filtered if (commodity or state) else base
        return jsonify({'prices': out})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Static file route (serve CSS/JS/images from project root)
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.form.to_dict()
        
        # Handle image upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(image_path)
        
        # Get weather data
        weather = get_weather_data(data.get('region'))
        
        # Analyze crop recommendations
        crop_recommendations = analyze_crop_recommendation(data)
        
        # Analyze disease symptoms
        disease_analysis = []
        if data.get('symptoms'):
            disease_analysis = analyze_disease(data.get('symptoms'), image_path)
        
        # pH analysis
        ph = float(data.get('ph', 7.0))
        ph_status = "Optimal" if 6.5 <= ph <= 7.5 else "Needs Adjustment"
        ph_advice = ""
        if ph < 6.5:
            ph_advice = "Soil is acidic. Add lime to increase pH."
        elif ph > 7.5:
            ph_advice = "Soil is alkaline. Add organic matter or sulfur to decrease pH."
        else:
            ph_advice = "Soil pH is in optimal range for most crops."
        
        result = {
            "success": True,
            "weather": weather,
            "crop_recommendations": crop_recommendations[:5],  # Top 5 crops
            "disease_analysis": disease_analysis,
            "ph_analysis": {
                "value": ph,
                "status": ph_status,
                "advice": ph_advice
            },
            "planting_calendar": generate_planting_calendar(data.get('season'), crop_recommendations[:3])
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/api/heatmap', methods=['GET'])
def api_heatmap():
    """Return heatmap data as JSON by calling heatmap.get_heatmap_data()."""
    try:
        # First try the imported module
        try:
            data = heatmap_module.get_heatmap_data()
        except Exception:
            data = None

        # If data looks like a requests.Response or not serializable, load local file directly
        def _is_serializable(val):
            try:
                json.dumps(val)
                return True
            except Exception:
                return isinstance(val, (dict, list, str, int, float, type(None)))

        if not _is_serializable(data):
            # load the local heatmap.py explicitly to avoid package shadowing
            import importlib.util
            base = os.path.dirname(__file__)
            heatmap_path = os.path.join(base, 'heatmap.py')
            spec = importlib.util.spec_from_file_location('local_heatmap', heatmap_path)
            local_heatmap = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(local_heatmap)
            data = local_heatmap.get_heatmap_data()

        # Use json.dumps with default=str to avoid serialization errors for unknown objects
        return app.response_class(json.dumps(data, default=str), mimetype='application/json')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/alerts', methods=['GET'])
def api_alerts():
    """Return a short list of recent alerts (mocked). Accepts optional ?limit=N"""
    try:
        limit = int(request.args.get('limit', 6))
        base = []
        # Build alerts from heatmap data if available
        try:
            src = heatmap_module.get_heatmap_data()
        except Exception:
            src = []

        for i, item in enumerate(src):
            base.append({
                'id': i + 1,
                'disease': item.get('description', 'Unknown Disease'),
                'crop': item.get('crop', 'Mixed'),
                'state': item.get('region', 'Unknown'),
                'district': item.get('district', f"District {i+1}"),
                'severity': item.get('level', 'Medium').capitalize(),
                'affected_area': item.get('affected_area', (i + 1) * 10),
                'message': f"{item.get('description', 'Reported issue')} in {item.get('region', 'region')}",
                'date': datetime.now().isoformat()
            })

        # Add some extra mock alerts if heatmap source is small
        while len(base) < limit:
            idx = len(base) + 1
            base.append({
                'id': idx,
                'disease': 'Leaf Blight',
                'crop': 'Rice',
                'state': 'Punjab',
                'district': f'District {idx}',
                'severity': 'High' if idx % 2 == 0 else 'Medium',
                'affected_area': idx * 5,
                'message': 'Field reports of rapid leaf blight spread',
                'date': datetime.now().isoformat()
            })

        return jsonify({'alerts': base[:limit]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/heatmap-data', methods=['GET'])
def api_heatmap_data():
    """Return detailed heatmap zones, supports filters: state, district, crop, season"""
    try:
        state = request.args.get('state', 'all')
        district = request.args.get('district', 'all')
        crop = request.args.get('crop', 'all')
        season = request.args.get('season', None)

        try:
            src = heatmap_module.get_heatmap_data()
        except Exception:
            src = []

        zones = []
        # Convert simple heatmap entries into richer zone objects
        for i, item in enumerate(src):
            zone = {
                'state': item.get('region', 'Unknown'),
                'district': item.get('district', f'District {i+1}'),
                'crop': item.get('crop', 'Rice'),
                'risk_level': item.get('level', 'medium').capitalize(),
                'risk_score': 80 if item.get('level') == 'high' else (55 if item.get('level') == 'medium' else 20),
                'diseases': [item.get('description', 'Unknown')],
                'humidity': 60 + i,
                'temperature': 25 + i,
                'affected_area': 10 * (i + 1),
                'description': item.get('description', ''),
            }

            # Apply simple filters
            if (state != 'all' and zone['state'] != state):
                continue
            if (district != 'all' and zone['district'] != district):
                continue
            if (crop != 'all' and zone['crop'] != crop):
                continue

            zones.append(zone)

        return jsonify({'data': zones})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/region-details', methods=['GET'])
def api_region_details():
    """Return a detailed payload for one region/district/crop combination"""
    try:
        state = request.args.get('state', None)
        district = request.args.get('district', None)
        crop = request.args.get('crop', None)

        # For this dev version return a mocked detail object
        details = {
            'state': state or 'Unknown',
            'district': district or 'Unknown District',
            'crop': crop or 'Rice',
            'season': request.args.get('season', 'Kharif'),
            'risk_level': 'High',
            'risk_score': 82,
            'humidity': 72,
            'temperature': 29,
            'diseases': ['Leaf Blight', 'Rust'],
            'recommendations': [
                'Apply recommended fungicide (follow label instructions)',
                'Remove heavily infected plants and burn debris',
                'Rotate crop and improve drainage'
            ],
            'affected_area': 45,
            'last_updated': datetime.now().isoformat()
        }

        return jsonify(details)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/trend-data', methods=['GET'])
def api_trend_data():
    """Return monthly trend data for a crop in a state (mocked)"""
    try:
        state = request.args.get('state', 'All')
        crop = request.args.get('crop', 'Rice')

        labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        # Simple synthetic data that varies by crop
        base = {
            'Rice': [30, 28, 35, 40, 55, 70, 85, 78, 60, 50, 35, 30],
            'Wheat': [20, 18, 22, 30, 45, 50, 40, 35, 30, 25, 22, 20]
        }

        data = base.get(crop, [25 + (i % 6) * 5 for i in range(12)])

        return jsonify({'labels': labels, 'data': data, 'crop': crop})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/weather', methods=['GET'])
def api_weather():
    """Return weather data for a city. Uses OpenWeatherMap if API key configured; otherwise returns mocked data."""
    # Accept either a city (free text) or a region (state/district) mapped to a representative city
    city = request.args.get('city')
    region = request.args.get('region')
    district = request.args.get('district')

    # Priority: district > city > region mapping > default
    if district and district.strip():
        # Use district as the lookup city (best-effort). For more accuracy map districts to centroids.
        city = district
    elif city and city.strip():
        city = city
    elif region:
        # Map regions to representative cities (simple mapping for demo)
        city_map = {
            "Punjab": "Ludhiana",
            "Uttar Pradesh": "Lucknow",
            "Maharashtra": "Pune"
        }
        city = city_map.get(region, 'Mumbai')
    else:
        city = 'Mumbai'

    try:
        # If a real API key is configured, attempt to fetch live data
        if WEATHER_API_KEY and WEATHER_API_KEY != 'your_api_key_here':
            try:
                current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
                r = requests.get(current_url, timeout=5)
                if r.status_code != 200:
                    raise Exception('City not found')
                current = r.json()

                forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric"
                rf = requests.get(forecast_url, timeout=5)
                forecast_raw = rf.json()

                # Build simplified payload
                current_weather = {
                    'temperature': round(current['main']['temp']),
                    'feels_like': round(current['main']['feels_like']),
                    'humidity': current['main']['humidity'],
                    'pressure': current['main']['pressure'],
                    'wind_speed': round(current['wind']['speed'] * 3.6, 1),
                    'description': current['weather'][0]['description'].title(),
                    'icon': current['weather'][0]['icon'],
                    'city': current['name'],
                    'country': current['sys']['country'],
                    'sunrise': datetime.fromtimestamp(current['sys']['sunrise']).strftime('%H:%M'),
                    'sunset': datetime.fromtimestamp(current['sys']['sunset']).strftime('%H:%M'),
                    'visibility': current.get('visibility', 0) / 1000,
                    'clouds': current['clouds']['all']
                }

                # Extract a simple daily forecast (one item per day)
                daily_forecast = []
                processed = set()
                for item in forecast_raw.get('list', []):
                    d = datetime.fromtimestamp(item['dt']).date()
                    hr = datetime.fromtimestamp(item['dt']).hour
                    if d not in processed and 11 <= hr <= 14:
                        daily_forecast.append({
                            'date': d.strftime('%a, %b %d'),
                            'temp_max': round(item['main']['temp_max']),
                            'temp_min': round(item['main']['temp_min']),
                            'description': item['weather'][0]['description'].title(),
                            'icon': item['weather'][0]['icon'],
                            'humidity': item['main']['humidity'],
                            'wind_speed': round(item['wind']['speed'] * 3.6, 1),
                            'rain_probability': int(item.get('pop', 0) * 100)
                        })
                        processed.add(d)
                        if len(daily_forecast) >= 5:
                            break

                # Try to fetch alerts via OneCall (optional)
                alerts = []
                try:
                    lat = current['coord']['lat']
                    lon = current['coord']['lon']
                    onecall = requests.get(f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric", timeout=5).json()
                    for a in onecall.get('alerts', []):
                        alerts.append({
                            'event': a.get('event'),
                            'description': a.get('description'),
                            'start': datetime.fromtimestamp(a.get('start')).strftime('%Y-%m-%d %H:%M') if a.get('start') else '',
                            'end': datetime.fromtimestamp(a.get('end')).strftime('%Y-%m-%d %H:%M') if a.get('end') else ''
                        })
                except Exception:
                    # ignore onecall failures
                    pass

                recommendations = [
                    {'type': 'info', 'title': 'Live Data', 'message': 'Recommendations based on current conditions.'}
                ]

                return jsonify({'current': current_weather, 'forecast': daily_forecast, 'alerts': alerts, 'recommendations': recommendations, 'source': 'live'})
            except Exception:
                # If live fetch fails, fall back to mocked data below
                pass

        # Mocked response when API key not set or fetch failed
        current_weather = {
            'temperature': 29,
            'feels_like': 31,
            'humidity': 68,
            'pressure': 1012,
            'wind_speed': 12.3,
            'description': 'Partly Cloudy',
            'icon': '03d',
            'city': city,
            'country': 'IN',
            'sunrise': '06:10',
            'sunset': '18:00',
            'visibility': 10,
            'clouds': 40
        }

        daily_forecast = []
        from datetime import timedelta
        today = datetime.now().date()
        for i in range(5):
            d = today + timedelta(days=i)
            daily_forecast.append({
                'date': d.strftime('%a, %b %d'),
                'temp_max': 30 + i,
                'temp_min': 22 + i,
                'description': 'Partly Cloudy',
                'icon': '03d',
                'humidity': 60,
                'wind_speed': 10,
                'rain_probability': 20
            })

        alerts = []
        recommendations = [
            {'type': 'info', 'title': 'No severe weather', 'message': 'Conditions look favorable for most crops.'}
        ]

        return jsonify({'current': current_weather, 'forecast': daily_forecast, 'alerts': alerts, 'recommendations': recommendations, 'source': 'mock'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_planting_calendar(season, crops):
    """Generate planting calendar for recommended crops"""
    calendar = []
    
    if season == "Kharif":
        months = {
            "planting": "June-July",
            "harvest": "October-November"
        }
    else:  # Rabi
        months = {
            "planting": "October-November",
            "harvest": "March-April"
        }
    
    for crop_data in crops:
        calendar.append({
            "crop": crop_data['name'],
            "planting_time": months['planting'],
            "harvest_time": months['harvest'],
            "duration": "4-5 months"
        })
    
    return calendar

if __name__ == '__main__':
    app.run(debug=True, port=5000)


# Save this as: requirements.txt
"""
Flask==2.3.0
flask-cors==4.0.0
requests==2.31.0
Werkzeug==2.3.0
"""