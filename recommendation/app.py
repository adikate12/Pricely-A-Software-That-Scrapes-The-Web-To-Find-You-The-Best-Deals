from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from recommendation_engine import RecommendationEngine
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize recommendation engine
engine = RecommendationEngine()

# HTML template for the root page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Recommendation API</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        h2 {
            color: #3498db;
            margin-top: 30px;
        }
        code {
            background-color: #f8f9fa;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: monospace;
        }
        pre {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        .endpoint {
            margin-bottom: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .method {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-weight: bold;
            margin-right: 10px;
        }
        .get {
            background-color: #d4edda;
            color: #155724;
        }
        .post {
            background-color: #cce5ff;
            color: #004085;
        }
    </style>
</head>
<body>
    <h1>Product Recommendation API</h1>
    <p>Welcome to the Product Recommendation API. This API provides personalized product recommendations based on user activity data.</p>
    
    <h2>Available Endpoints</h2>
    
    <div class="endpoint">
        <span class="method get">GET</span>
        <code>/api/recommendations/user/&lt;user_id&gt;</code>
        <p>Get all recommendations for a specific user.</p>
    </div>
    
    <div class="endpoint">
        <span class="method get">GET</span>
        <code>/api/recommendations/content-based/&lt;user_id&gt;</code>
        <p>Get content-based recommendations for a specific user.</p>
    </div>
    
    <div class="endpoint">
        <span class="method get">GET</span>
        <code>/api/recommendations/collaborative/&lt;user_id&gt;</code>
        <p>Get collaborative recommendations for a specific user.</p>
    </div>
    
    <div class="endpoint">
        <span class="method get">GET</span>
        <code>/api/recommendations/hybrid/&lt;user_id&gt;</code>
        <p>Get hybrid recommendations (combining content-based and collaborative) for a specific user.</p>
    </div>
    
    <div class="endpoint">
        <span class="method get">GET</span>
        <code>/api/preferences/&lt;user_id&gt;</code>
        <p>Get user preferences based on their activity data.</p>
    </div>
    
    <h2>Example Response</h2>
    <pre>{
  "success": true,
  "data": {
    "content_based": [...],
    "collaborative": [...],
    "hybrid": [...]
  }
}</pre>
    
    <h2>Testing the API</h2>
    <p>You can test the API using tools like Postman, cURL, or by making fetch requests from your frontend application.</p>
    <p>Example cURL command:</p>
    <pre>curl -X GET "http://localhost:5000/api/recommendations/user/user_123"</pre>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the API documentation page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/recommendations/user/<user_id>', methods=['GET'])
def get_user_recommendations(user_id):
    """Get all recommendations for a user"""
    try:
        print(f"Generating recommendations for user: {user_id}")
        
        # Check if product data is loaded
        if not engine.product_data:
            print("Product data not loaded. Loading now...")
            engine.load_product_data()
            print(f"Loaded {len(engine.product_data)} products")
        
        # Check if user activities are loaded
        if not engine.user_activities:
            print("User activities not loaded. Loading now...")
            engine.load_user_activities()
            print(f"Loaded activities for {len(engine.user_activities)} users")
        
        # Generate recommendations
        recommendations = engine.generate_recommendations(user_id)
        print(f"Generated recommendations: {recommendations}")
        
        return jsonify({
            'success': True,
            'data': recommendations
        })
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recommendations/content-based/<user_id>', methods=['GET'])
def get_content_based_recommendations(user_id):
    """Get content-based recommendations for a user"""
    try:
        recommendations = engine.content_based_filtering(user_id)
        return jsonify({
            'success': True,
            'data': recommendations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recommendations/collaborative/<user_id>', methods=['GET'])
def get_collaborative_recommendations(user_id):
    """Get collaborative recommendations for a user"""
    try:
        recommendations = engine.collaborative_filtering(user_id)
        return jsonify({
            'success': True,
            'data': recommendations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recommendations/hybrid/<user_id>', methods=['GET'])
def get_hybrid_recommendations(user_id):
    """Get hybrid recommendations for a user"""
    try:
        recommendations = engine.hybrid_recommendation(user_id)
        return jsonify({
            'success': True,
            'data': recommendations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/preferences/<user_id>', methods=['GET'])
def get_user_preferences(user_id):
    """Get user preferences"""
    try:
        preferences = engine.get_user_preferences(user_id)
        return jsonify({
            'success': True,
            'data': preferences
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 