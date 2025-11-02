# app.py - Complete Flask Backend for Plant Disease Detection System
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import json
from datetime import datetime

app = Flask(_name_)
app.secret_key = secrets.token_hex(16)
CORS(app)

# In-memory databases (use PostgreSQL/MySQL in production)
users_db = {}
search_history_db = {}

# Complete Disease Database with detailed information
DISEASES = {
    "early_blight": {
        "id": "early_blight",
        "name": "Early Blight",
        "scientific_name": "Alternaria solani",
        "plant": "Tomato, Potato",
        "symptoms": [
            "Dark brown spots with concentric rings (target-like pattern)",
            "Yellowing of leaves around the spots",
            "Premature leaf drop starting from lower leaves",
            "Lesions may appear on stems and fruits",
            "Reduced fruit size and quality"
        ],
        "severity": "Moderate to High",
        "causes": "Fungal infection, favored by warm humid weather",
        "treatment": [
            "Remove and destroy infected plant parts",
            "Apply fungicides containing chlorothalonil or copper",
            "Practice crop rotation",
            "Ensure proper plant spacing for air circulation"
        ],
        "prevention": [
            "Use disease-resistant varieties",
            "Mulch around plants to prevent soil splash",
            "Water at the base of plants, avoid wetting foliage",
            "Remove plant debris at end of season"
        ]
    },
    "late_blight": {
        "id": "late_blight",
        "name": "Late Blight",
        "scientific_name": "Phytophthora infestans",
        "plant": "Tomato, Potato",
        "symptoms": [
            "Water-soaked spots on leaves that turn brown",
            "White fuzzy growth on leaf undersides",
            "Rapid spreading during humid conditions",
            "Brown lesions on stems and petioles",
            "Fruit develops brown, greasy-looking spots"
        ],
        "severity": "Very High",
        "causes": "Oomycete pathogen, spreads rapidly in cool, wet conditions",
        "treatment": [
            "Apply fungicides immediately (mancozeb, chlorothalonil)",
            "Remove all infected plants to prevent spread",
            "Improve air circulation",
            "Avoid overhead irrigation"
        ],
        "prevention": [
            "Plant resistant varieties",
            "Monitor weather conditions closely",
            "Apply preventive fungicides during susceptible periods",
            "Maintain proper plant spacing"
        ]
    },
    "powdery_mildew": {
        "id": "powdery_mildew",
        "name": "Powdery Mildew",
        "scientific_name": "Various species",
        "plant": "Various crops",
        "symptoms": [
            "White or gray powdery coating on leaves",
            "Starts on upper leaf surfaces",
            "Leaves may curl and become distorted",
            "Stunted plant growth",
            "Premature leaf senescence"
        ],
        "severity": "Moderate",
        "causes": "Fungal infection, favored by dry conditions and high humidity",
        "treatment": [
            "Apply sulfur or potassium bicarbonate sprays",
            "Use neem oil or horticultural oils",
            "Prune affected areas",
            "Improve air circulation"
        ],
        "prevention": [
            "Choose resistant varieties",
            "Avoid overhead watering",
            "Ensure adequate spacing between plants",
            "Apply preventive fungicides early in season"
        ]
    },
    "bacterial_spot": {
        "id": "bacterial_spot",
        "name": "Bacterial Spot",
        "scientific_name": "Xanthomonas spp.",
        "plant": "Tomato, Pepper",
        "symptoms": [
            "Small, dark brown to black spots with yellow halos",
            "Spots may merge to form larger lesions",
            "Leaf tissue may crack and fall out",
            "Fruit develops raised dark spots",
            "Defoliation in severe cases"
        ],
        "severity": "High",
        "causes": "Bacterial pathogen, spreads through water splash and contaminated tools",
        "treatment": [
            "Apply copper-based bactericides",
            "Remove infected plants",
            "Avoid working with plants when wet",
            "Sanitize tools between uses"
        ],
        "prevention": [
            "Use disease-free seeds and transplants",
            "Practice crop rotation (3-4 years)",
            "Use drip irrigation instead of overhead",
            "Plant resistant varieties when available"
        ]
    },
    "septoria_leaf_spot": {
        "id": "septoria_leaf_spot",
        "name": "Septoria Leaf Spot",
        "scientific_name": "Septoria lycopersici",
        "plant": "Tomato",
        "symptoms": [
            "Circular spots with gray centers and dark borders",
            "Small black dots (pycnidia) in center of spots",
            "Starts on lower leaves and moves upward",
            "Extensive yellowing and defoliation",
            "Fruit remains unaffected but exposed to sunscald"
        ],
        "severity": "Moderate to High",
        "causes": "Fungal pathogen, spreads through water splash",
        "treatment": [
            "Apply fungicides containing chlorothalonil",
            "Remove lower infected leaves",
            "Mulch to prevent soil splash",
            "Stake plants for better air circulation"
        ],
        "prevention": [
            "Rotate crops annually",
            "Remove plant debris",
            "Water at soil level",
            "Space plants adequately"
        ]
    },
    "mosaic_virus": {
        "id": "mosaic_virus",
        "name": "Mosaic Virus",
        "scientific_name": "Tobacco mosaic virus (TMV)",
        "plant": "Tomato, Cucumber, Tobacco",
        "symptoms": [
            "Mottled light and dark green pattern on leaves",
            "Leaf distortion and curling",
            "Stunted plant growth",
            "Reduced fruit production",
            "Fruit may show color mottling"
        ],
        "severity": "High",
        "causes": "Viral infection, transmitted by aphids and contaminated tools",
        "treatment": [
            "No cure available - remove infected plants",
            "Control aphid populations",
            "Sanitize tools with 10% bleach solution",
            "Wash hands before handling plants"
        ],
        "prevention": [
            "Use virus-resistant varieties",
            "Control aphid vectors",
            "Avoid tobacco products near plants",
            "Purchase certified disease-free plants"
        ]
    },
    "leaf_curl": {
        "id": "leaf_curl",
        "name": "Leaf Curl",
        "scientific_name": "Tomato leaf curl virus",
        "plant": "Tomato, Chili",
        "symptoms": [
            "Severe upward or downward curling of leaves",
            "Yellowing of leaf margins",
            "Thickening and brittleness of leaves",
            "Stunted plant growth",
            "Reduced flowering and fruit set"
        ],
        "severity": "Very High",
        "causes": "Viral disease transmitted by whiteflies",
        "treatment": [
            "Remove and destroy infected plants",
            "Control whitefly populations with insecticides",
            "Use yellow sticky traps",
            "Apply neem oil sprays"
        ],
        "prevention": [
            "Use virus-resistant varieties",
            "Install insect-proof nets",
            "Control whitefly populations early",
            "Remove weeds that harbor whiteflies"
        ]
    },
    "black_rot": {
        "id": "black_rot",
        "name": "Black Rot",
        "scientific_name": "Guignardia bidwellii",
        "plant": "Grape, Cabbage",
        "symptoms": [
            "Circular tan to brown lesions on leaves",
            "V-shaped yellow lesions at leaf margins",
            "Black veins within lesions",
            "Fruit shrivels and turns black (mummification)",
            "Dark streaks on stems"
        ],
        "severity": "High",
        "causes": "Fungal pathogen, survives in mummified fruit and plant debris",
        "treatment": [
            "Apply fungicides during susceptible growth stages",
            "Remove and destroy mummified fruit",
            "Prune for air circulation",
            "Remove infected plant parts"
        ],
        "prevention": [
            "Sanitation - remove all plant debris",
            "Prune vines to improve air flow",
            "Apply preventive fungicides",
            "Choose resistant varieties"
        ]
    },
    "rust": {
        "id": "rust",
        "name": "Rust Disease",
        "scientific_name": "Puccinia spp.",
        "plant": "Wheat, Bean, Rose",
        "symptoms": [
            "Orange, yellow, or reddish-brown pustules on leaves",
            "Pustules may appear on stems and pods",
            "Leaf yellowing and premature drop",
            "Reduced photosynthesis",
            "Weakened plant structure"
        ],
        "severity": "Moderate to High",
        "causes": "Fungal pathogen, favored by moisture and moderate temperatures",
        "treatment": [
            "Apply sulfur or copper-based fungicides",
            "Remove infected leaves",
            "Improve air circulation",
            "Avoid overhead watering"
        ],
        "prevention": [
            "Plant rust-resistant varieties",
            "Proper plant spacing",
            "Water in morning to allow foliage to dry",
            "Remove plant debris"
        ]
    },
    "anthracnose": {
        "id": "anthracnose",
        "name": "Anthracnose",
        "scientific_name": "Colletotrichum spp.",
        "plant": "Mango, Strawberry, Bean",
        "symptoms": [
            "Sunken dark brown to black lesions on fruit",
            "Water-soaked spots that turn brown",
            "Fruit rot and premature drop",
            "Circular spots on leaves with dark borders",
            "Twig dieback in severe cases"
        ],
        "severity": "High",
        "causes": "Fungal pathogen, favored by warm, wet conditions",
        "treatment": [
            "Apply copper-based fungicides",
            "Remove infected fruit and plant parts",
            "Prune to improve air circulation",
            "Collect and destroy fallen fruit"
        ],
        "prevention": [
            "Plant resistant varieties",
            "Ensure proper drainage",
            "Apply preventive fungicides before flowering",
            "Maintain tree health through proper fertilization"
        ]
    },
    "downy_mildew": {
        "id": "downy_mildew",
        "name": "Downy Mildew",
        "scientific_name": "Peronospora spp.",
        "plant": "Grape, Lettuce, Cucumber",
        "symptoms": [
            "Yellow spots on upper leaf surface",
            "Gray or purple fuzzy growth on undersides",
            "Leaf curling and distortion",
            "Premature leaf drop",
            "Stunted plant growth"
        ],
        "severity": "High",
        "causes": "Oomycete pathogen, favored by cool, moist conditions",
        "treatment": [
            "Apply fungicides containing copper or mancozeb",
            "Improve air circulation",
            "Remove infected leaves",
            "Avoid overhead irrigation"
        ],
        "prevention": [
            "Use resistant varieties",
            "Proper plant spacing",
            "Water early in day",
            "Apply preventive fungicides in wet weather"
        ]
    },
    "fusarium_wilt": {
        "id": "fusarium_wilt",
        "name": "Fusarium Wilt",
        "scientific_name": "Fusarium oxysporum",
        "plant": "Tomato, Banana, Cotton",
        "symptoms": [
            "Yellowing of lower leaves progressing upward",
            "Wilting during hot days, recovery at night initially",
            "Brown discoloration in vascular tissue",
            "Stunted growth and poor fruit development",
            "Eventual plant death"
        ],
        "severity": "Very High",
        "causes": "Soil-borne fungal pathogen, persists in soil for years",
        "treatment": [
            "No effective cure - remove infected plants",
            "Solarize soil before replanting",
            "Use disease-free soil or containers",
            "Consider resistant rootstocks"
        ],
        "prevention": [
            "Plant resistant varieties (VF, VFN labeled)",
            "Practice long crop rotations (5+ years)",
            "Maintain soil pH around 6.5-7.0",
            "Avoid moving contaminated soil"
        ]
    },
    "cercospora_leaf_spot": {
        "id": "cercospora_leaf_spot",
        "name": "Cercospora Leaf Spot",
        "scientific_name": "Cercospora beticola",
        "plant": "Sugar Beet, Soybean",
        "symptoms": [
            "Small circular spots with tan centers",
            "Purple to reddish-brown borders",
            "Spots may coalesce into larger lesions",
            "Premature defoliation",
            "Reduced photosynthetic capacity"
        ],
        "severity": "Moderate",
        "causes": "Fungal pathogen, spreads through wind and rain",
        "treatment": [
            "Apply triazole or strobilurin fungicides",
            "Scout fields regularly",
            "Time applications based on disease threshold",
            "Rotate fungicide classes"
        ],
        "prevention": [
            "Plant resistant varieties",
            "Practice crop rotation",
            "Bury crop residue",
            "Monitor disease development closely"
        ]
    },
    "verticillium_wilt": {
        "id": "verticillium_wilt",
        "name": "Verticillium Wilt",
        "scientific_name": "Verticillium dahliae",
        "plant": "Tomato, Eggplant, Strawberry",
        "symptoms": [
            "Yellowing and wilting of lower leaves",
            "V-shaped yellow areas at leaf margins",
            "Brown streaks in stems when cut",
            "One-sided wilting of plant",
            "Stunted growth and reduced yield"
        ],
        "severity": "High",
        "causes": "Soil-borne fungal pathogen, survives as microsclerotia",
        "treatment": [
            "Remove and destroy infected plants",
            "Do not compost infected material",
            "Solarize soil in summer",
            "Use fumigation in severe cases"
        ],
        "prevention": [
            "Use resistant varieties (V marked)",
            "Long crop rotations with non-host crops",
            "Maintain plant vigor",
            "Avoid planting in infested soil"
        ]
    },
    "alternaria_leaf_spot": {
        "id": "alternaria_leaf_spot",
        "name": "Alternaria Leaf Spot",
        "scientific_name": "Alternaria brassicae",
        "plant": "Brassicas, Carrot",
        "symptoms": [
            "Dark brown to black spots with yellow halos",
            "Target-like concentric rings in lesions",
            "Spots enlarge and merge together",
            "Leaf yellowing and drop",
            "May affect stems and flowers"
        ],
        "severity": "Moderate",
        "causes": "Fungal pathogen, favored by warm humid conditions",
        "treatment": [
            "Apply fungicides containing azoxystrobin",
            "Remove infected plant parts",
            "Improve air circulation",
            "Rotate crops"
        ],
        "prevention": [
            "Use disease-free seeds",
            "Practice 2-3 year crop rotation",
            "Destroy crop residues",
            "Apply preventive fungicides if needed"
        ]
    }
}

# Routes for Authentication
@app.route('/')
def home():
    """Main landing page - redirect to login if not authenticated"""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not email or not username or not password:
            return jsonify({
                'success': False, 
                'message': 'All fields are required'
            }), 400
        
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 6 characters'
            }), 400
        
        if email in users_db:
            return jsonify({
                'success': False, 
                'message': 'Email already exists'
            }), 400
        
        # Create user
        users_db[email] = {
            'username': username,
            'password': generate_password_hash(password),
            'created_at': datetime.now().isoformat()
        }
        
        # Initialize search history for user
        search_history_db[email] = []
        
        # Set session
        session['user'] = username
        session['email'] = email
        session['is_guest'] = False
        
        return jsonify({
            'success': True, 
            'message': 'Registration successful',
            'user': {'username': username, 'email': email}
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Registration error: {str(e)}'
        }), 500

@app.route('/login', methods=['POST'])
def login():
    """Login existing user"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({
                'success': False, 
                'message': 'Email and password required'
            }), 400
        
        if email not in users_db:
            return jsonify({
                'success': False, 
                'message': 'Invalid email or password'
            }), 401
        
        user = users_db[email]
        if not check_password_hash(user['password'], password):
            return jsonify({
                'success': False, 
                'message': 'Invalid email or password'
            }), 401
        
        # Set session
        session['user'] = user['username']
        session['email'] = email
        session['is_guest'] = False
        
        return jsonify({
            'success': True, 
            'message': 'Login successful',
            'user': {'username': user['username'], 'email': email}
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Login error: {str(e)}'
        }), 500

@app.route('/guest-login', methods=['POST'])
def guest_login():
    """Login as guest user"""
    session['user'] = 'Guest User'
    session['is_guest'] = True
    session['email'] = None
    
    return jsonify({
        'success': True, 
        'message': 'Logged in as guest'
    })

@app.route('/logout')
def logout():
    """Logout current user"""
    session.clear()
    return redirect(url_for('home'))

# Routes for Disease Detection
@app.route('/dashboard')
def dashboard():
    """Main dashboard page"""
    if 'user' not in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html')

@app.route('/api/diseases', methods=['GET'])
def get_diseases():
    """Get all diseases"""
    return jsonify({
        'success': True,
        'count': len(DISEASES),
        'diseases': DISEASES
    })

@app.route('/api/disease/<disease_id>', methods=['GET'])
def get_disease(disease_id):
    """Get specific disease by ID"""
    if disease_id in DISEASES:
        return jsonify({
            'success': True,
            'disease': DISEASES[disease_id]
        })
    return jsonify({
        'success': False,
        'message': 'Disease not found'
    }), 404

@app.route('/api/search-diseases', methods=['POST'])
def search_diseases():
    """Search diseases by plant name or disease name"""
    try:
        data = request.json
        query = data.get('query', '').lower().strip()
        
        if not query:
            return jsonify({
                'success': False,
                'message': 'Search query required'
            }), 400
        
        results = []
        for disease_id, disease in DISEASES.items():
            if (query in disease['name'].lower() or 
                query in disease['plant'].lower() or
                query in disease.get('scientific_name', '').lower()):
                results.append(disease)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'results': results
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Search error: {str(e)}'
        }), 500

@app.route('/api/match-symptoms', methods=['POST'])
def match_symptoms():
    """Match user symptoms with diseases"""
    try:
        data = request.json
        user_input = data.get('symptoms', '').lower().strip()
        
        if not user_input:
            return jsonify({
                'success': False,
                'message': 'Symptoms description required'
            }), 400
        
        # Save to search history if user is logged in
        if 'email' in session and session['email']:
            email = session['email']
            if email not in search_history_db:
                search_history_db[email] = []
            
            search_history_db[email].append({
                'symptoms': user_input,
                'timestamp': datetime.now().isoformat()
            })
        
        results = []
        for disease_id, disease in DISEASES.items():
            match_count = 0
            matched_symptoms = []
            
            # Check each symptom
            for symptom in disease['symptoms']:
                symptom_words = symptom.lower().split()
                symptom_match = False
                
                # Check if significant words from symptom appear in user input
                for word in symptom_words:
                    if len(word) > 3 and word in user_input:
                        symptom_match = True
                        break
                
                if symptom_match:
                    match_count += 1
                    matched_symptoms.append(symptom)
            
            if match_count > 0:
                match_percentage = round((match_count / len(disease['symptoms'])) * 100)
                results.append({
                    'disease_id': disease_id,
                    'disease': disease,
                    'match_count': match_count,
                    'total_symptoms': len(disease['symptoms']),
                    'match_percentage': match_percentage,
                    'matched_symptoms': matched_symptoms
                })
        
        # Sort by match percentage
        results.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'results': results
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Matching error: {str(e)}'
        }), 500

@app.route('/api/user-info', methods=['GET'])
def user_info():
    """Get current user information"""
    if 'user' in session:
        return jsonify({
            'success': True,
            'user': {
                'username': session['user'],
                'email': session.get('email'),
                'is_guest': session.get('is_guest', True)
            }
        })
    return jsonify({
        'success': False,
        'message': 'Not logged in'
    }), 401

@app.route('/api/search-history', methods=['GET'])
def get_search_history():
    """Get user's search history"""
    if 'email' not in session or not session['email']:
        return jsonify({
            'success': False,
            'message': 'Search history only available for registered users'
        }), 403
    
    email = session['email']
    history = search_history_db.get(email, [])
    
    return jsonify({
        'success': True,
        'count': len(history),
        'history': history
    })

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get system statistics"""
    return jsonify({
        'success': True,
        'statistics': {
            'total_diseases': len(DISEASES),
            'total_users': len(users_db),
            'severity_distribution': {
                'Very High': sum(1 for d in DISEASES.values() if d['severity'] == 'Very High'),
                'High': sum(1 for d in DISEASES.values() if d['severity'] == 'High'),
                'Moderate to High': sum(1 for d in DISEASES.values() if d['severity'] == 'Moderate to High'),
                'Moderate': sum(1 for d in DISEASES.values() if d['severity'] == 'Moderate')
            }
        }
    })

@app.route('/api/diseases-by-plant/<plant_name>', methods=['GET'])
def get_diseases_by_plant(plant_name):
    """Get all diseases affecting a specific plant"""
    plant_name = plant_name.lower()
    results = []
    
    for disease_id, disease in DISEASES.items():
        if plant_name in disease['plant'].lower():
            results.append(disease)
    
    return jsonify({
        'success': True,
        'plant': plant_name,
        'count': len(results),
        'diseases': results
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Resource not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Plant Disease Detection API',
        'version': '1.0.0'
    })

if _name_ == '_main_':
    print("=" * 60)
    print("🌿 Plant Disease Detection System - Backend Server")
    print("=" * 60)
    print(f"✅ Loaded {len(DISEASES)} diseases into database")
    print("🚀 Server starting on http://127.0.0.1:5000")
    print("📝 API Documentation:")
    print("   - POST /register - Register new user")
    print("   - POST /login - Login user")
    print("   - POST /guest-login - Login as guest")
    print("   - GET /logout - Logout")
    print("   - GET /api/diseases - Get all diseases")
    print("   - GET /api/disease/<id> - Get specific disease")
    print("   - POST /api/match-symptoms - Match symptoms")
    print("   - POST /api/search-diseases - Search diseases")
    print("   - GET /api/user-info - Get current user")
    print("   - GET /api/search-history - Get search history")
    print("   - GET /api/statistics - Get system statistics")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)