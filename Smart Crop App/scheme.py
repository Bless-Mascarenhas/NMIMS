from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(_name_)
CORS(app)  # Enable CORS for frontend-backend communication

# Schemes database
SCHEMES = [
    {
        "id": 1,
        "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "category": "Financial Support",
        "description": "Direct income support of ₹6,000 per year to all landholding farmer families in three equal installments.",
        "benefits": ["₹2,000 every 4 months", "Direct bank transfer", "No application fee"],
        "eligibility": ["All landholding farmers", "Valid Aadhaar card", "Bank account linked to Aadhaar"],
        "how_to_apply": "Visit PM-KISAN portal or nearest CSC center",
        "documents": ["Aadhaar card", "Bank account details", "Land ownership documents"],
        "website": "https://pmkisan.gov.in",
        "eligible_for": ["small", "marginal", "medium", "large"]
    },
    {
        "id": 2,
        "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "category": "Insurance",
        "description": "Comprehensive crop insurance scheme protecting farmers against crop loss due to natural calamities, pests & diseases.",
        "benefits": ["Low premium rates", "Claims settled quickly", "Coverage for pre-sowing to post-harvest"],
        "eligibility": ["All farmers growing notified crops", "Sharecroppers and tenant farmers eligible"],
        "how_to_apply": "Through banks, CSCs, or insurance company agents",
        "documents": ["Aadhaar card", "Bank account", "Land records", "Sowing certificate"],
        "website": "https://pmfby.gov.in",
        "eligible_for": ["small", "marginal", "medium", "large"]
    },
    {
        "id": 3,
        "name": "Kisan Credit Card (KCC)",
        "category": "Credit",
        "description": "Provides farmers with timely access to credit for agriculture and allied activities at concessional interest rates.",
        "benefits": ["Interest subvention of 2%", "Flexible repayment", "Accident insurance coverage up to ₹50,000"],
        "eligibility": ["Individual/joint farmers", "Tenant farmers, oral lessees", "Self Help Groups"],
        "how_to_apply": "Visit nearest bank branch with documents",
        "documents": ["Identity proof", "Address proof", "Land records", "Passport size photo"],
        "website": "https://www.india.gov.in",
        "eligible_for": ["small", "marginal", "medium", "large"]
    },
    {
        "id": 4,
        "name": "PM Kisan Maan Dhan Yojana",
        "category": "Pension",
        "description": "Old age pension scheme for small and marginal farmers ensuring ₹3,000 monthly pension after 60 years.",
        "benefits": ["Guaranteed ₹3,000/month pension", "Low contribution (₹55-200/month)", "Family pension available"],
        "eligibility": ["Age 18-40 years", "Small & marginal farmers (up to 2 hectares)", "Not under other pension schemes"],
        "how_to_apply": "Through CSC centers with Aadhaar and bank details",
        "documents": ["Aadhaar card", "Bank passbook", "Land records"],
        "website": "https://maandhan.in",
        "eligible_for": ["small", "marginal"],
        "age_range": [18, 40]
    },
    {
        "id": 5,
        "name": "Soil Health Card Scheme",
        "category": "Agricultural Support",
        "description": "Provides soil health cards to farmers with information on nutrient status and recommendations on dosage of nutrients.",
        "benefits": ["Free soil testing", "Customized fertilizer recommendations", "Reduces input costs"],
        "eligibility": ["All farmers", "One card per land holding"],
        "how_to_apply": "Contact local agriculture department or soil testing lab",
        "documents": ["Land ownership proof", "Aadhaar card"],
        "website": "https://soilhealth.dac.gov.in",
        "eligible_for": ["small", "marginal", "medium", "large"]
    },
    {
        "id": 6,
        "name": "National Agriculture Market (e-NAM)",
        "category": "Marketing",
        "description": "Online trading platform for agricultural commodities ensuring better price discovery and transparent auction process.",
        "benefits": ["Better prices through competitive bidding", "Reduced transaction costs", "Online payment"],
        "eligibility": ["Registered farmers", "Traders", "Commission agents"],
        "how_to_apply": "Register on e-NAM portal with required documents",
        "documents": ["Aadhaar card", "Bank account", "Land records", "Mobile number"],
        "website": "https://www.enam.gov.in",
        "eligible_for": ["small", "marginal", "medium", "large"]
    },
    {
        "id": 7,
        "name": "Paramparagat Krishi Vikas Yojana (PKVY)",
        "category": "Organic Farming",
        "description": "Promotes organic farming through cluster approach with financial assistance of ₹50,000 per hectare for 3 years.",
        "benefits": ["₹50,000/hectare support", "Organic certification assistance", "Market linkage support"],
        "eligibility": ["Farmers willing to adopt organic farming", "Cluster of 50 acres minimum"],
        "how_to_apply": "Through State Agriculture Department",
        "documents": ["Land records", "Aadhaar card", "Bank account details"],
        "website": "https://pgsindia-ncof.gov.in",
        "eligible_for": ["small", "marginal", "medium", "large"]
    },
    {
        "id": 8,
        "name": "Modified Interest Subvention Scheme",
        "category": "Credit",
        "description": "Provides short-term crop loans up to ₹3 lakh at subsidized interest rates of 4% per annum to farmers.",
        "benefits": ["Interest rate of only 4%", "Additional 3% subvention on prompt repayment", "Coverage for allied activities"],
        "eligibility": ["All farmers availing crop loans", "Loan amount up to ₹3 lakh"],
        "how_to_apply": "Through scheduled commercial banks and cooperative banks",
        "documents": ["KCC/Loan documents", "Land records", "Identity proof"],
        "website": "https://dmi.gov.in",
        "eligible_for": ["small", "marginal", "medium", "large"]
    }
]

# Route: Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Route: Get All Schemes
@app.route('/api/schemes', methods=['GET'])
def get_schemes():
    """Return all schemes"""
    category = request.args.get('category', 'All')
    search = request.args.get('search', '').lower()
    
    filtered_schemes = SCHEMES
    
    # Filter by category
    if category != 'All':
        filtered_schemes = [s for s in filtered_schemes if s['category'] == category]
    
    # Filter by search term
    if search:
        filtered_schemes = [
            s for s in filtered_schemes 
            if search in s['name'].lower() or search in s['description'].lower()
        ]
    
    return jsonify({
        'success': True,
        'schemes': filtered_schemes,
        'total': len(filtered_schemes)
    })

# Route: Get Single Scheme
@app.route('/api/schemes/<int:scheme_id>', methods=['GET'])
def get_scheme(scheme_id):
    """Return details of a specific scheme"""
    scheme = next((s for s in SCHEMES if s['id'] == scheme_id), None)
    
    if scheme:
        return jsonify({
            'success': True,
            'scheme': scheme
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Scheme not found'
        }), 404

# Route: Check Eligibility
@app.route('/api/check-eligibility', methods=['POST'])
def check_eligibility():
    """Check eligibility for schemes based on farmer details"""
    try:
        data = request.get_json()
        
        land_size = data.get('land_size', 0)
        farmer_type = data.get('farmer_type', '')
        state = data.get('state', '')
        age = data.get('age', 0)
        
        # Determine farmer type based on land size if not provided
        if not farmer_type:
            if land_size <= 1:
                farmer_type = 'marginal'
            elif land_size <= 2:
                farmer_type = 'small'
            elif land_size <= 10:
                farmer_type = 'medium'
            else:
                farmer_type = 'large'
        
        # Filter eligible schemes
        eligible_schemes = []
        
        for scheme in SCHEMES:
            # Check farmer type eligibility
            if farmer_type not in scheme.get('eligible_for', []):
                continue
            
            # Check age eligibility if scheme has age restriction
            age_range = scheme.get('age_range')
            if age_range and (age < age_range[0] or age > age_range[1]):
                continue
            
            eligible_schemes.append(scheme)
        
        # Log eligibility check
        log_eligibility_check(data, len(eligible_schemes))
        
        return jsonify({
            'success': True,
            'eligible_schemes': eligible_schemes,
            'total_eligible': len(eligible_schemes),
            'farmer_profile': {
                'land_size': land_size,
                'farmer_type': farmer_type,
                'state': state,
                'age': age
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

# Route: Submit Application (placeholder)
@app.route('/api/apply', methods=['POST'])
def submit_application():
    """Handle scheme application submission"""
    try:
        data = request.get_json()
        
        scheme_id = data.get('scheme_id')
        farmer_name = data.get('farmer_name')
        contact = data.get('contact')
        aadhaar = data.get('aadhaar')
        
        # In a real application, you would:
        # 1. Validate the data
        # 2. Store in database
        # 3. Send confirmation email/SMS
        # 4. Generate application ID
        
        application_id = f"APP{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return jsonify({
            'success': True,
            'message': 'Application submitted successfully',
            'application_id': application_id,
            'scheme_id': scheme_id
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

# Route: Get Categories
@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Return all unique categories"""
    categories = list(set([s['category'] for s in SCHEMES]))
    return jsonify({
        'success': True,
        'categories': ['All'] + sorted(categories)
    })

# Route: Search Schemes
@app.route('/api/search', methods=['GET'])
def search_schemes():
    """Search schemes by keyword"""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({
            'success': False,
            'message': 'Search query is required'
        }), 400
    
    results = [
        s for s in SCHEMES 
        if query in s['name'].lower() or 
           query in s['description'].lower() or
           query in s['category'].lower()
    ]
    
    return jsonify({
        'success': True,
        'results': results,
        'total': len(results),
        'query': query
    })

# Helper function to log eligibility checks
def log_eligibility_check(data, eligible_count):
    """Log eligibility check for analytics"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'farmer_type': data.get('farmer_type'),
        'land_size': data.get('land_size'),
        'state': data.get('state'),
        'eligible_schemes_count': eligible_count
    }
    # In production, save to database or log file
    print(f"[LOG] Eligibility Check: {json.dumps(log_entry)}")

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

# Run the application
if _name_ == '_main_':
    app.run(debug=True, host='0.0.0.0', port=5000)