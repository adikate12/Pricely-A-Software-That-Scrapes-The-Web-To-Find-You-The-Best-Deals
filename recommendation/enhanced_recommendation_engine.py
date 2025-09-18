import os
import json
import numpy as np
from bson import ObjectId
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta
from dotenv import load_dotenv
from collections import defaultdict
import re

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class EnhancedRecommendationEngine:
    def __init__(self, amazon_path='Amazon/amazon_products.json', 
                 croma_path='Croma/croma_mobiles_2.json', 
                 flipkart_path='Home/flipkart_mobiles_2.json'):
        self.products = []
        self.user_preferences = {}
        self.amazon_path = amazon_path
        self.croma_path = croma_path
        self.flipkart_path = flipkart_path
        self._load_products_from_json()
        
        # Connect to MongoDB for user activities
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client.Pricely
        self._load_user_activities()
        
    def _load_products_from_json(self):
        """Load products from JSON files instead of MongoDB"""
        def load_json_file(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")
                return []
        
        def convert_price(price_str):
            try:
                # Remove currency symbol and commas
                if not price_str or price_str == 'N/A':
                    return 0.0
                price_str = price_str.replace('₹', '').replace(',', '').strip()
                return float(price_str)
            except:
                return 0.0

        def convert_rating(rating_str):
            try:
                if not rating_str or rating_str == 'N/A' or rating_str == 'No rating':
                    return 0.0
                return float(rating_str)
            except:
                return 0.0
        
        def extract_brand(name):
            """Extract brand from product name"""
            common_brands = ['Redmi', 'POCO', 'OnePlus', 'SAMSUNG', 'Samsung', 'vivo', 'VIVO', 'realme', 'OPPO', 'Oppo', 'iQOO', 'Nothing']
            name_parts = name.split()
            for brand in common_brands:
                if brand.lower() in name.lower():
                    return brand
            return name_parts[0] if name_parts else 'Unknown'
        
        def is_mobile_phone(product):
            # Check if product is a mobile phone (not an accessory)
            name = product.get('Product Name', '').lower()
            
            # List of accessory keywords to exclude
            accessory_keywords = [
                'case', 'cover', 'charger', 'cable', 'headphone', 'earphone',
                'screen guard', 'protector', 'tempered glass', 'battery',
                'power bank', 'adapter', 'stand', 'holder', 'mount', 'dock',
                'stylus', 'pen', 'memory card', 'sim card', 'pop socket',
                'grip', 'skin', 'wrap', 'film', 'shield', 'bag', 'pouch',
                'sleeve', 'strap', 'lanyard', 'keychain', 'ring', 'loop',
                'p', 'pro', 'max', 'plus', 'lite', 'mini', 'ultra', 'edge'
            ]
            
            # List of mobile phone keywords to include
            phone_keywords = [
                'smartphone', 'mobile phone', 'iphone', 'android phone',
                '5g phone', '4g phone', 'dual sim phone', 'android mobile',
                'smart phone', 'cellular phone', 'handset', 'device',
                'samsung galaxy', 'oneplus', 'redmi', 'poco', 'vivo',
                'oppo', 'realme', 'motorola', 'nokia', 'xiaomi', 'iqoo',
                'nothing phone'
            ]
            
            # Check if it's an accessory
            if any(acc in name for acc in accessory_keywords):
                return False
                
            # Check if it's a mobile phone
            return any(phone in name for phone in phone_keywords)
        
        # Load products from different sources
        amazon_products = load_json_file(self.amazon_path)
        croma_products = load_json_file(self.croma_path)
        flipkart_products = load_json_file(self.flipkart_path)
        
        print(f"Loaded Amazon products: {len(amazon_products)}")
        print(f"Loaded Croma products: {len(croma_products)}")
        print(f"Loaded Flipkart products: {len(flipkart_products)}")
        
        # Process and combine products
        for source, products in [
            ('Amazon', amazon_products),
            ('Croma', croma_products),
            ('Flipkart', flipkart_products)
        ]:
            for product in products:
                if not is_mobile_phone(product):
                    continue
                    
                name = product.get('Product Name', '')
                price = convert_price(product.get('Price', '0'))
                if price <= 0:
                    continue
                    
                # Create standardized product structure
                standardized_product = {
                    'id': str(len(self.products) + 1),  # Generate unique ID
                    'name': name,
                    'brand': extract_brand(name),
                    'price': price,
                    'source': source,
                    'category': 'Mobile',
                    'rating': convert_rating(product.get('Rating', '0')),
                    'image_url': product.get('Image URL', ''),
                    'product_url': product.get('Product Link', '')
                }
                
                self.products.append(standardized_product)
        
        print(f"Processed and loaded {len(self.products)} valid products")
        if self.products:
            print("Sample product:", json.dumps(self.products[0], indent=2, cls=JSONEncoder))
        
    def _load_user_activities(self):
        """Load user activities from MongoDB"""
        activities = list(self.db.useractivities.find())
        print(f"Found {len(activities)} activity documents")
        
        # Group activities by user
        for activity in activities:
            user_id = activity.get('userId')
            if not user_id:
                continue
                
            if user_id not in self.user_preferences:
                self.user_preferences[user_id] = {
                    'viewed_products': {},
                    'clicked_products': {},
                    'viewed_brands': {},
                    'viewed_categories': {},
                    'phone_views': {}
                }
            
            # Update preferences based on activity type
            action = activity.get('action', '')
            metadata = activity.get('metadata', {})
            
            if action == 'product_view':
                product_id = metadata.get('productId')
                if product_id:
                    self.user_preferences[user_id]['viewed_products'][product_id] = \
                        self.user_preferences[user_id]['viewed_products'].get(product_id, 0) + 1
                    
                    # Track brand and category
                    product = next((p for p in self.products if p['id'] == product_id), None)
                    if product:
                        self.user_preferences[user_id]['viewed_brands'][product['brand']] = \
                            self.user_preferences[user_id]['viewed_brands'].get(product['brand'], 0) + 1
                        self.user_preferences[user_id]['viewed_categories'][product['category']] = \
                            self.user_preferences[user_id]['viewed_categories'].get(product['category'], 0) + 1
                        self.user_preferences[user_id]['phone_views'][product['name']] = \
                            self.user_preferences[user_id]['phone_views'].get(product['name'], 0) + 1
            
            elif action == 'product_click':
                product_id = metadata.get('productId')
                if product_id:
                    self.user_preferences[user_id]['clicked_products'][product_id] = \
                        self.user_preferences[user_id]['clicked_products'].get(product_id, 0) + 1
        
        print(f"Retrieved {len(activities)} activities")
        print("Sample activity structure:", json.dumps(activities[0], indent=2, cls=JSONEncoder))
        print(f"Grouped activities for {len(self.user_preferences)} users")
        print("User IDs:", list(self.user_preferences.keys()))
        
    def get_recommendations(self, user_id, n=5):
        """Get recommendations for a user using hybrid approach"""
        if user_id not in self.user_preferences:
            return self._get_default_recommendations(n)
            
        preferences = self.user_preferences[user_id]
        print(f"\nProcessing {len(preferences['viewed_products'])} activities for user {user_id}")
        print("\nExtracted preferences:", json.dumps(preferences, indent=2, cls=JSONEncoder))
        
        # Get content-based recommendations
        content_recs = self.content_based_filtering(user_id, n * 2)  # Get more recommendations
        
        # Get collaborative recommendations
        collab_recs = self.collaborative_filtering(user_id, n * 2)  # Get more recommendations
        
        # Combine and deduplicate recommendations
        seen_models = set()
        final_recommendations = []
        
        # Helper function to get base model name
        def get_base_model(name):
            # Remove color variants and storage variants
            name = name.lower()
            # Remove color variants
            colors = ['red', 'blue', 'green', 'black', 'white', 'pink', 'purple', 'gold', 'silver']
            for color in colors:
                name = name.replace(f' - {color}', '').replace(f' ({color})', '')
            # Remove storage variants
            storage_patterns = ['gb ram', 'gb storage', 'gb']
            for pattern in storage_patterns:
                name = re.sub(r'\d+\s*' + pattern, '', name)
            return name.strip()
        
        # Group recommendations by source
        source_groups = {
            'Amazon': [],
            'Croma': [],
            'Flipkart': []
        }
        
        # Add recommendations to source groups
        for rec in content_recs + collab_recs:
            base_model = get_base_model(rec['name'])
            if base_model not in seen_models:
                seen_models.add(base_model)
                source_groups[rec['source']].append(rec)
        
        # Distribute recommendations evenly across sources
        max_per_source = (n + 2) // 3  # Round up division
        for source in ['Amazon', 'Croma', 'Flipkart']:
            source_recs = source_groups[source][:max_per_source]
            final_recommendations.extend(source_recs)
            if len(final_recommendations) >= n:
                break
        
        # If we don't have enough recommendations, fill with remaining ones
        if len(final_recommendations) < n:
            remaining = n - len(final_recommendations)
            for rec in content_recs + collab_recs:
                if rec not in final_recommendations:
                    final_recommendations.append(rec)
                    remaining -= 1
                    if remaining == 0:
                        break
        
        return final_recommendations[:n]  # Ensure we return exactly n recommendations
        
    def content_based_filtering(self, user_id, n=5):
        """Generate content-based recommendations"""
        if not self.products or user_id not in self.user_preferences:
            return self._get_default_recommendations(n)
            
        preferences = self.user_preferences[user_id]
        
        # Get viewed and clicked products to exclude
        viewed_products = set(preferences['viewed_products'].keys())
        clicked_products = set(preferences['clicked_products'].keys())
        excluded_products = viewed_products.union(clicked_products)
        
        # Calculate average price of interacted products
        interacted_prices = []
        for product in self.products:
            if product['id'] in excluded_products:
                interacted_prices.append(product['price'])
        avg_price = sum(interacted_prices) / len(interacted_prices) if interacted_prices else 0
        
        # Score products based on brand and category preferences
        scored_products = []
        for product in self.products:
            if product['id'] in excluded_products:
                continue
                
            score = 0
            
            # Brand preference score
            brand_score = preferences['viewed_brands'].get(product['brand'], 0)
            score += brand_score * 2  # Weight brand preference more heavily
            
            # Category preference score
            category_score = preferences['viewed_categories'].get(product['category'], 0)
            score += category_score
            
            # Price range score (prefer products within 20% of average price)
            if avg_price > 0:
                price_diff = abs(product['price'] - avg_price) / avg_price
                if price_diff <= 0.2:  # Within 20% of average price
                    score += 1
            
            # Rating score
            score += product['rating']
            
            scored_products.append((score, product))
        
        # Sort by score and return top N recommendations
        scored_products.sort(reverse=True, key=lambda x: x[0])
        recommendations = [product for score, product in scored_products[:n]]
        
        return recommendations if recommendations else self._get_default_recommendations(n)
        
    def collaborative_filtering(self, user_id, n=5):
        """Generate collaborative recommendations"""
        if len(self.user_preferences) < 2:
            return self._get_default_recommendations(n)
            
        # Get current user's preferences
        current_user = self.user_preferences[user_id]
        current_viewed = set(current_user['viewed_products'].keys())
        
        # Find similar users
        similar_users = []
        for other_user_id, other_preferences in self.user_preferences.items():
            if other_user_id == user_id:
                continue
                
            # Calculate similarity based on viewed products
            other_viewed = set(other_preferences['viewed_products'].keys())
            common_products = current_viewed.intersection(other_viewed)
            
            if common_products:
                similarity = len(common_products) / len(current_viewed.union(other_viewed))
                similar_users.append((other_user_id, similarity))
                
        # Sort by similarity
        similar_users.sort(key=lambda x: x[1], reverse=True)
        
        # Get recommendations from similar users
        recommendations = []
        for other_user_id, similarity in similar_users[:3]:  # Top 3 similar users
            other_preferences = self.user_preferences[other_user_id]
            other_viewed = set(other_preferences['viewed_products'].keys())
            
            # Get products viewed by similar user but not by current user
            new_products = other_viewed - current_viewed
            for product_id in new_products:
                product = next((p for p in self.products if p['id'] == product_id), None)
                if product:
                    recommendations.append((product, similarity))
                    
        # Sort by similarity and get top n
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return [p[0] for p in recommendations[:n]]
        
    def _combine_recommendations(self, content_recs, collab_recs, n=5):
        """Combine content-based and collaborative recommendations"""
        # Create a set of product IDs to avoid duplicates
        seen_ids = set()
        combined = []
        
        # Add content-based recommendations first
        for product in content_recs:
            if product['id'] not in seen_ids:
                combined.append(product)
                seen_ids.add(product['id'])
                
        # Add collaborative recommendations
        for product in collab_recs:
            if product['id'] not in seen_ids:
                combined.append(product)
                seen_ids.add(product['id'])
                
        return combined[:n]
        
    def _get_default_recommendations(self, n=5):
        """Get default recommendations when no user preferences are available"""
        # Sort products by price and return top n
        sorted_products = sorted(self.products, key=lambda x: x['price'])
        return sorted_products[:n] 