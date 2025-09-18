import os
import json
import pandas as pd
import numpy as np
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from mongodb_connection import get_collection
import sys

# Load environment variables
load_dotenv()

class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class RecommendationEngine:
    def __init__(self):
        self.product_data = {}
        self.user_activities = {}
        self.user_preferences = {}
        self.similarity_matrix = {}
        self.recommendations = {}
        
        # MongoDB connection
        self.mongo_uri = os.getenv('MONGODB_URI')
        self.client = None
        self.db = None
        
        # Use exact collection names
        self.activities = get_collection('useractivities')
        self.products = get_collection('products')
        self.user_preferences = get_collection('userpreferences')
        
        # Load product data from JSON files
        self.load_product_data()
        
    def connect_to_mongodb(self):
        """Connect to MongoDB database"""
        try:
            print(f"Connecting to MongoDB with URI: {self.mongo_uri}")
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client.get_database('Pricely')
            print(f"Connected to MongoDB: {self.db.name}")
            
            # List all collections
            collections = self.db.list_collection_names()
            print(f"Available collections: {collections}")
            
            return True
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            return False
            
    def load_product_data(self):
        """Load product data from JSON files into MongoDB"""
        try:
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            
            # Define file paths
            amazon_path = os.path.join(project_root, "Amazon", "amazon_products.json")
            croma_path = os.path.join(project_root, "Croma", "croma_mobiles_2.json")
            flipkart_path = os.path.join(project_root, "Home", "flipkart_mobiles_2.json")
            
            # Clear existing products
            self.products.delete_many({})
            
            # Load Amazon products
            with open(amazon_path, 'r', encoding='utf-8') as f:
                amazon_products = json.load(f)
                for product in amazon_products:
                    self.products.insert_one({
                        'id': product.get('Product Link', ''),
                        'name': product.get('Product Name', ''),
                        'brand': product.get('Brand', ''),
                        'price': float(str(product.get('Price', '0')).replace('₹', '').replace(',', '').strip() or 0),
                        'source': 'Amazon',
                        'image_url': product.get('Image URL', ''),
                        'product_url': product.get('Product Link', ''),
                        'category': 'mobile'
                    })
            
            # Load Croma products
            with open(croma_path, 'r', encoding='utf-8') as f:
                croma_products = json.load(f)
                for product in croma_products:
                    self.products.insert_one({
                        'id': product.get('Product Link', ''),
                        'name': product.get('Product Name', ''),
                        'brand': product.get('Brand', ''),
                        'price': float(str(product.get('Price', '0')).replace('₹', '').replace(',', '').strip() or 0),
                        'source': 'Croma',
                        'image_url': product.get('Image URL', ''),
                        'product_url': product.get('Product Link', ''),
                        'category': 'mobile'
                    })
            
            # Load Flipkart products
            with open(flipkart_path, 'r', encoding='utf-8') as f:
                flipkart_products = json.load(f)
                for product in flipkart_products:
                    self.products.insert_one({
                        'id': product.get('Product Link', ''),
                        'name': product.get('Product Name', ''),
                        'brand': product.get('Brand', ''),
                        'price': float(str(product.get('Price', '0')).replace('₹', '').replace(',', '').strip() or 0),
                        'source': 'Flipkart',
                        'image_url': product.get('Image URL', ''),
                        'product_url': product.get('Product Link', ''),
                        'category': 'mobile'
                    })
        except Exception as e:
            print(f"Error loading product data: {str(e)}", file=sys.stderr)
            raise
            
    def load_user_activities(self):
        """Load user activities from MongoDB"""
        try:
            if self.db is None:
                if not self.connect_to_mongodb():
                    return False
                    
            print("Loading user activities from MongoDB...")
            collection = self.db.useractivities
            
            # Count documents
            count = collection.count_documents({})
            print(f"Found {count} activity documents")
            
            # Get all user activities
            activities = list(collection.find({}))
            print(f"Retrieved {len(activities)} activities")
            
            # Debug: Print first activity structure
            if activities:
                print("Sample activity structure:")
                print(json.dumps(activities[0], indent=2, cls=MongoJSONEncoder))
            
            # Group activities by email
            self.user_activities = {}
            for activity in activities:
                email = activity.get('email', 'anonymous')
                if email not in self.user_activities:
                    self.user_activities[email] = []
                self.user_activities[email].append(activity)
                
            print(f"Grouped activities for {len(self.user_activities)} users")
            print(f"User emails: {list(self.user_activities.keys())}")
            
            # Initialize empty activities list for users with no activities
            if 'anonymous' not in self.user_activities:
                self.user_activities['anonymous'] = []
            
            return True
        except Exception as e:
            print(f"Error loading user activities: {e}")
            # Initialize empty activities for anonymous user even on error
            self.user_activities = {'anonymous': []}
            return True
            
    def extract_user_preferences(self):
        """Extract user preferences from activities"""
        try:
            # Initialize preferences for all users, including anonymous
            self.user_preferences = {}
            
            for user_id, activities in self.user_activities.items():
                # Initialize user preferences
                self.user_preferences[user_id] = {
                    'viewed_products': {},
                    'clicked_products': {},
                    'viewed_brands': {},
                    'viewed_categories': {},
                    'phone_views': {}
                }
                
                # Debug: Print number of activities for this user
                print(f"\nProcessing {len(activities)} activities for user {user_id}")
                
                # Process each activity
                for activity in activities:
                    product_id = activity.get('metadata', {}).get('productId') or activity.get('metadata', {}).get('phoneId')
                    
                    if not product_id:
                        continue
                        
                    # Track viewed products
                    if activity.get('action') in ['product_click', 'phone_view']:
                        if product_id not in self.user_preferences[user_id]['viewed_products']:
                            self.user_preferences[user_id]['viewed_products'][product_id] = 0
                        self.user_preferences[user_id]['viewed_products'][product_id] += 1
                        
                        # Track clicked products
                        if activity.get('action') == 'product_click':
                            if product_id not in self.user_preferences[user_id]['clicked_products']:
                                self.user_preferences[user_id]['clicked_products'][product_id] = 0
                            self.user_preferences[user_id]['clicked_products'][product_id] += 1
                            
                        # Track phone views
                        if activity.get('action') == 'phone_view':
                            phone_name = activity.get('metadata', {}).get('phoneName')
                            if phone_name:
                                if phone_name not in self.user_preferences[user_id]['phone_views']:
                                    self.user_preferences[user_id]['phone_views'][phone_name] = 0
                                self.user_preferences[user_id]['phone_views'][phone_name] += 1
                                
                        # Track brands and categories if available
                        product = self.product_data.get(product_id)
                        if product:
                            if product.get('brand'):
                                brand = product['brand']
                                if brand not in self.user_preferences[user_id]['viewed_brands']:
                                    self.user_preferences[user_id]['viewed_brands'][brand] = 0
                                self.user_preferences[user_id]['viewed_brands'][brand] += 1
                                
                            if product.get('category'):
                                category = product['category']
                                if category not in self.user_preferences[user_id]['viewed_categories']:
                                    self.user_preferences[user_id]['viewed_categories'][category] = 0
                                self.user_preferences[user_id]['viewed_categories'][category] += 1
                                
                # Debug: Print extracted preferences for this user
                print(f"\nExtracted preferences for {user_id}:")
                print(json.dumps(self.user_preferences[user_id], indent=2, cls=MongoJSONEncoder))
                
            print(f"Extracted preferences for {len(self.user_preferences)} users")
            return True
        except Exception as e:
            print(f"Error extracting user preferences: {e}")
            # Initialize empty preferences for anonymous user even on error
            self.user_preferences = {
                'anonymous': {
                    'viewed_products': {},
                    'clicked_products': {},
                    'viewed_brands': {},
                    'viewed_categories': {},
                    'phone_views': {}
                }
            }
            return True
            
    def content_based_filtering(self, user_id):
        """Generate content-based recommendations"""
        try:
        if user_id not in self.user_preferences:
                print(f"No preferences found for user {user_id}")
            return []
                
            preferences = self.user_preferences[user_id]
            
            # If user has no preferences, return popular products
            if not any(preferences.values()):
                print(f"User {user_id} has no preferences, returning popular products")
                return self.get_popular_products()
                
            # Calculate product scores based on user preferences
            product_scores = {}
            
            for product_id, product in self.product_data.items():
                score = 0
                
                # Brand preference
                if product.get('brand') in preferences['viewed_brands']:
                    score += preferences['viewed_brands'][product['brand']] * 2
                    
                # Category preference
                if product.get('category') in preferences['viewed_categories']:
                    score += preferences['viewed_categories'][product['category']] * 1.5
                    
                # Phone name preference
                for phone_name, count in preferences['phone_views'].items():
                    if phone_name.lower() in product.get('name', '').lower():
                        score += count * 3
                        
                if score > 0:
                    product_scores[product_id] = score
                    
            # Sort products by score
            sorted_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Return top 5 products
            return [product_id for product_id, _ in sorted_products[:5]]
            
        except Exception as e:
            print(f"Error in content-based filtering: {e}")
            return self.get_popular_products()
        
    def collaborative_filtering(self, user_id):
        """Generate collaborative filtering recommendations"""
        try:
        if user_id not in self.user_preferences:
                print(f"No preferences found for user {user_id}")
            return []
            
            preferences = self.user_preferences[user_id]
            
            # If user has no preferences, return popular products
            if not any(preferences.values()):
                print(f"User {user_id} has no preferences, returning popular products")
                return self.get_popular_products()
                
            # Calculate product scores based on user preferences
            product_scores = {}
            
            for product_id, product in self.product_data.items():
                score = 0
                
                # Viewed products
                if product_id in preferences['viewed_products']:
                    score += preferences['viewed_products'][product_id] * 2
                    
                # Clicked products
                if product_id in preferences['clicked_products']:
                    score += preferences['clicked_products'][product_id] * 3
                    
                if score > 0:
                    product_scores[product_id] = score
                    
            # Sort products by score
            sorted_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Return top 5 products
            return [product_id for product_id, _ in sorted_products[:5]]
            
        except Exception as e:
            print(f"Error in collaborative filtering: {e}")
            return self.get_popular_products()
        
    def hybrid_recommendation(self, user_id):
        """Generate hybrid recommendations combining content-based and collaborative filtering"""
        try:
            if user_id not in self.user_preferences:
                print(f"No preferences found for user {user_id}")
                return []
                
            preferences = self.user_preferences[user_id]
            
            # If user has no preferences, return popular products
            if not any(preferences.values()):
                print(f"User {user_id} has no preferences, returning popular products")
                return self.get_popular_products()
                
            # Get content-based recommendations
            content_recs = self.content_based_filtering(user_id)
            
            # Get collaborative recommendations
            collab_recs = self.collaborative_filtering(user_id)
            
            # Combine recommendations with weights
            combined_scores = {}
            
            # Add content-based recommendations with weight 0.6
            for product_id in content_recs:
                if product_id not in combined_scores:
                    combined_scores[product_id] = 0
                combined_scores[product_id] += 0.6
                
            # Add collaborative recommendations with weight 0.4
            for product_id in collab_recs:
                if product_id not in combined_scores:
                    combined_scores[product_id] = 0
                combined_scores[product_id] += 0.4
                
            # Sort by combined score
            sorted_products = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Return top 5 products
            return [product_id for product_id, _ in sorted_products[:5]]
            
        except Exception as e:
            print(f"Error in hybrid recommendation: {e}")
            return self.get_popular_products()
        
    def generate_recommendations(self, user_id):
        """Generate recommendations for a user"""
        try:
            # Load data if not already loaded
            if not self.product_data:
                if not self.load_product_data():
                    return self._get_default_recommendations()
                    
            if not self.user_activities:
                if not self.load_user_activities():
                    return self._get_default_recommendations()
                    
            # Extract user preferences if not already extracted
            if not self.user_preferences:
                self.extract_user_preferences()
                
            # If user has no preferences, provide different default recommendations
            if not self.user_preferences.get(user_id, {}).get('viewed_products'):
                return self._get_default_recommendations()
                
            # Generate recommendations using different algorithms
            content_based_recs = self.content_based_filtering(user_id) or []
            collaborative_recs = self.collaborative_filtering(user_id) or []
            hybrid_recs = self.hybrid_recommendation(user_id) or []
            
            # If any algorithm returns no recommendations, use defaults
            if not content_based_recs:
                content_based_recs = self._get_default_recommendations()['content_based']
            if not collaborative_recs:
                collaborative_recs = self._get_default_recommendations()['collaborative']
            if not hybrid_recs:
                hybrid_recs = self._get_default_recommendations()['hybrid']
            
            # Store recommendations
            self.recommendations[user_id] = {
                'content_based': content_based_recs,
                'collaborative': collaborative_recs,
                'hybrid': hybrid_recs
            }
            
            return self.recommendations[user_id]
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return self._get_default_recommendations()
            
    def _get_default_recommendations(self):
        """Get default recommendations when no user preferences are available"""
        products = list(self.product_data.values())
        
        # Remove duplicates based on name and brand
        unique_products = {}
        for p in products:
            key = f"{p['name']}_{p['brand']}"
            if key not in unique_products:
                unique_products[key] = p
        products = list(unique_products.values())
        
        # Content-based default: Sort by brand popularity
        brand_counts = {}
        for p in products:
            brand = p['brand']
            brand_counts[brand] = brand_counts.get(brand, 0) + 1
            
        content_based_products = sorted(products, 
            key=lambda x: (brand_counts.get(x['brand'], 0), -x['price']), 
            reverse=True
        )[:10]
        
        # Collaborative default: Sort by price (most affordable)
        collaborative_products = sorted(products, 
            key=lambda x: x['price']
        )[:10]
        
        # Hybrid default: Sort by brand popularity and price
        hybrid_products = sorted(products,
            key=lambda x: (brand_counts.get(x['brand'], 0) * 0.7, -x['price'] * 0.3),
            reverse=True
        )[:10]
        
        # Ensure all products have required fields
        def validate_product(p):
            return all(key in p for key in ['id', 'name', 'brand', 'price', 'source'])
            
        content_based_products = [p for p in content_based_products if validate_product(p)]
        collaborative_products = [p for p in collaborative_products if validate_product(p)]
        hybrid_products = [p for p in hybrid_products if validate_product(p)]
        
        # Ensure unique products across all recommendation types
        seen_ids = set()
        unique_content_based = []
        unique_collaborative = []
        unique_hybrid = []
        
        # Process hybrid recommendations first
        for p in hybrid_products:
            if p['id'] not in seen_ids:
                seen_ids.add(p['id'])
                unique_hybrid.append(p)
                
        # Then content-based
        for p in content_based_products:
            if p['id'] not in seen_ids:
                seen_ids.add(p['id'])
                unique_content_based.append(p)
                
        # Finally collaborative
        for p in collaborative_products:
            if p['id'] not in seen_ids:
                seen_ids.add(p['id'])
                unique_collaborative.append(p)
        
        return {
            'content_based': [{
                'product_id': p['id'],
                'product': p,
                'score': 1.0,
                'algorithm': 'content-based-default'
            } for p in unique_content_based],
            'collaborative': [{
                'product_id': p['id'],
                'product': p,
                'score': 1.0,
                'algorithm': 'collaborative-default'
            } for p in unique_collaborative],
            'hybrid': [{
                'product_id': p['id'],
                'product': p,
                'score': 1.0,
                'algorithm': 'hybrid-default'
            } for p in unique_hybrid]
        }
        
    def get_recommendations(self, user_id):
        """Get recommendations for a user"""
        try:
            print(f"\nGetting recommendations for user: {user_id}")
            
            # Load user activities and extract preferences
            if not self.load_user_activities():
                print("Failed to load user activities, using default recommendations")
                return self._get_default_recommendations()
                
            if not self.extract_user_preferences():
                print("Failed to extract user preferences, using default recommendations")
                return self._get_default_recommendations()
                
            # Check if user has any activity
            if user_id not in self.user_activities or not self.user_activities[user_id]:
                print(f"No activities found for user {user_id}")
                return self._get_default_recommendations()
                
            # Get user preferences
            user_prefs = self.user_preferences[user_id]
            print(f"User preferences: {json.dumps(user_prefs, indent=2, cls=MongoJSONEncoder)}")
            
            # Get recommendations using hybrid approach
            recommendations = self.hybrid_recommendation(user_id)
            
            # If no recommendations from hybrid, try content-based
            if not recommendations:
                print("No hybrid recommendations, trying content-based")
                recommendations = self.content_based_filtering(user_id)
                
            # If still no recommendations, try collaborative
            if not recommendations:
                print("No content-based recommendations, trying collaborative")
                recommendations = self.collaborative_filtering(user_id)
                
            # If still no recommendations, use default
            if not recommendations:
                print("No recommendations found, using default")
                recommendations = self._get_default_recommendations()
                
            # Convert recommendations to list and remove duplicates
            seen_ids = set()
            unique_recommendations = []
            for rec in recommendations:
                if rec['id'] not in seen_ids:
                    seen_ids.add(rec['id'])
                    unique_recommendations.append(rec)
                    
            # Limit to 5 recommendations
            return unique_recommendations[:5]
            
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return self._get_default_recommendations()
        
    def get_user_preferences(self, user_id):
        """Get user preferences based on their activity"""
        # Get user activities from the last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        user_activities = list(self.activities.find({
            'user_id': user_id,
            'timestamp': {'$gte': thirty_days_ago}
        }))
        
        if not user_activities:
            return None
        
        # Extract preferences
        preferences = {
            'viewed_products': [],
            'clicked_products': [],
            'brands': {},
            'categories': {},
            'price_range': {'min': float('inf'), 'max': 0}
        }
        
        for activity in user_activities:
            product_id = activity.get('product_id')
            action = activity.get('action')
            
            if product_id:
                product = self.products.find_one({'id': product_id})
                if product:
                    if action == 'view':
                        preferences['viewed_products'].append(product_id)
                    elif action == 'click':
                        preferences['clicked_products'].append(product_id)
                    
                    # Track brand preferences
                    brand = product.get('brand')
                    if brand:
                        preferences['brands'][brand] = preferences['brands'].get(brand, 0) + 1
                    
                    # Track price range
                    price = product.get('price', 0)
                    preferences['price_range']['min'] = min(preferences['price_range']['min'], price)
                    preferences['price_range']['max'] = max(preferences['price_range']['max'], price)
        
        # Store preferences
        self.user_preferences.update_one(
            {'user_id': user_id},
            {'$set': preferences},
            upsert=True
        )
        
        return preferences 

    def get_popular_products(self):
        """Get popular products based on user activities"""
        try:
            # Count product views across all users
            product_views = {}
            for user_id, activities in self.user_activities.items():
                for activity in activities:
                    if activity.get('action') == 'view':
                        product_id = activity.get('product_id')
                        if product_id:
                            product_views[product_id] = product_views.get(product_id, 0) + 1
                            
            # Sort products by view count
            sorted_products = sorted(product_views.items(), key=lambda x: x[1], reverse=True)
            
            # Return top 5 most viewed products
            return [product_id for product_id, _ in sorted_products[:5]]
            
        except Exception as e:
            print(f"Error getting popular products: {e}")
            # Fallback to default recommendations if there's an error
            return self._get_default_recommendations() 