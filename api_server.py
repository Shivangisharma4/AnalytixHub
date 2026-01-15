import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import DatabaseManager

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize database manager
db = DatabaseManager()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "database": "connected" if db.is_postgres else "sqlite",
        "supports_categories": True
    }), 200

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all available categories"""
    try:
        categories = db.get_categories()
        return jsonify(categories)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories/<slug>', methods=['GET'])
def get_category(slug):
    """Get a specific category by slug"""
    try:
        category = db.get_category_by_slug(slug)
        if not category:
            return jsonify({"error": "Category not found"}), 404
        return jsonify(category)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/services', methods=['GET'])
def get_services():
    try:
        name = request.args.get('name')
        category = request.args.get('category')
        
        if name:
            service = db.get_service_with_features(name)
            if not service:
                return jsonify({"error": "Service not found"}), 404
            return jsonify(service)
        
        # Support filtering by category slug
        services = db.get_all_services(category_slug=category)
        return jsonify(services)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/rankings/<context>', methods=['GET'])
def get_rankings(context):
    try:
        rankings = db.get_rankings(context)
        return jsonify(rankings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/compare', methods=['GET'])
def get_comparison():
    try:
        category = request.args.get('category')
        comparison = db.get_feature_comparison(category_slug=category)
        return jsonify(comparison)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/recommend', methods=['GET'])
def get_recommendations():
    try:
        context = request.args.get('context', 'personal_use')
        category = request.args.get('category')
        free_tier = request.args.get('free_tier') == 'true'
        collaboration = request.args.get('collaboration') == 'true'
        offline_mode = request.args.get('offline_mode') == 'true'
        api_available = request.args.get('api_available') == 'true'
        
        # This mirrors the logic in main.py recommendation
        from ranking_system import RankingSystem
        rs = RankingSystem(db)
        
        requirements = {}
        if request.args.get('free_tier') is not None: requirements['free_tier'] = free_tier
        if request.args.get('collaboration') is not None: requirements['collaboration'] = collaboration
        if request.args.get('offline_mode') is not None: requirements['offline_mode'] = offline_mode
        if request.args.get('api_available') is not None: requirements['api_available'] = api_available
        
        recommendations = rs.recommend_service(requirements, context, category_slug=category)
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', 'False').lower() == 'true')
