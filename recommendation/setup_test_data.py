import os
import json
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timedelta
import random

def load_json_file(filepath):
    """Load data from a JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return []

def convert_price(price_str):
    """Convert price string to float"""
    if not price_str or price_str == 'N/A':
        return 0.0
    try:
        # Remove currency symbol and commas
        price_str = price_str.replace('₹', '').replace(',', '').strip()
        return float(price_str)
    except (ValueError, TypeError):
        return 0.0

def is_mobile_phone(name):
    """Check if product is a mobile phone"""
    mobile_keywords = ['phone', 'mobile', 'smartphone', '5g', '4g']
    accessory_keywords = ['case', 'cover', 'charger', 'cable', 'stand', 'holder', 
                         'sticker', 'pouch', 'screen', 'protector', 'tempered', 
                         'glass', 'battery', 'power bank']
    
    name_lower = name.lower()
    return any(keyword in name_lower for keyword in mobile_keywords) and \
           not any(keyword in name_lower for keyword in accessory_keywords)

def setup_test_data():
    """Set up test data in MongoDB"""
    try:
        # Load environment variables
        load_dotenv()
        mongodb_uri = os.getenv('MONGODB_URI')
        
        if not mongodb_uri:
            print("Error: MONGODB_URI not found in .env file")
            return
            
        print(f"Connecting to MongoDB...")
        client = MongoClient(mongodb_uri)
        db = client.pricely
        
        # Drop existing collections
        db.products.drop()
        db.useractivities.drop()
        
        # Load product data
        products = []
        
        # Load Amazon data
        amazon_data = load_json_file('../Amazon/amazon_products.json')
        for item in amazon_data:
            name = item.get('Product Name', '')
            if not is_mobile_phone(name):
                continue
                
            price = convert_price(item.get('Price', '0'))
            if price <= 0:
                continue
                
            products.append({
                'name': name,
                'brand': name.split()[0],
                'category': 'Mobile',
                'price': price,
                'image_url': item.get('Image Link', ''),
                'product_url': item.get('Product Link', ''),
                'source': 'Amazon'
            })
            
        # Load Croma data
        croma_data = load_json_file('../Croma/croma_mobiles_2.json')
        for item in croma_data:
            name = item.get('Product Name', '')
            if not is_mobile_phone(name):
                continue
                
            price = convert_price(item.get('Price', '0'))
            if price <= 0:
                continue
                
            products.append({
                'name': name,
                'brand': name.split()[0],
                'category': 'Mobile',
                'price': price,
                'image_url': item.get('Image Link', ''),
                'product_url': item.get('Product Link', ''),
                'source': 'Croma'
            })
            
        # Load Flipkart data
        flipkart_data = load_json_file('../Home/flipkart_mobiles_2.json')
        for item in flipkart_data:
            name = item.get('Product Name', '')
            if not is_mobile_phone(name):
                continue
                
            price = convert_price(item.get('Price', '0'))
            if price <= 0:
                continue
                
            products.append({
                'name': name,
                'brand': name.split()[0],
                'category': 'Mobile',
                'price': price,
                'image_url': item.get('Image Link', ''),
                'product_url': item.get('Product Link', ''),
                'source': 'Flipkart'
            })
            
        # Insert products
        if products:
            result = db.products.insert_many(products)
            print(f"Inserted {len(result.inserted_ids)} products")
            
        # Generate test activities
        test_users = [
            {'userId': 'admin@gmail.com', 'username': 'Admin'},
            {'userId': 'test@example.com', 'username': 'Test User'}
        ]
        
        activities = []
        now = datetime.now()
        
        for user in test_users:
            # Get random products for this user
            user_products = random.sample(products, min(10, len(products)))
            
            for product in user_products:
                # Generate view activity
                view_time = now - timedelta(days=random.randint(1, 30))
                activities.append({
                    'userId': user['userId'],
                    'username': user['username'],
                    'action': 'product_view',
                    'timestamp': view_time,
                    'metadata': {
                        'productId': str(product['_id']),
                        'productName': product['name'],
                        'price': product['price']
                    }
                })
                
                # 50% chance of clicking
                if random.random() < 0.5:
                    click_time = view_time + timedelta(minutes=random.randint(1, 10))
                    activities.append({
                        'userId': user['userId'],
                        'username': user['username'],
                        'action': 'product_click',
                        'timestamp': click_time,
                        'metadata': {
                            'productId': str(product['_id']),
                            'productName': product['name'],
                            'price': product['price']
                        }
                    })
                    
                # 30% chance of phone view
                if random.random() < 0.3:
                    phone_time = view_time + timedelta(minutes=random.randint(1, 10))
                    activities.append({
                        'userId': user['userId'],
                        'username': user['username'],
                        'action': 'phone_view',
                        'timestamp': phone_time,
                        'metadata': {
                            'productId': str(product['_id']),
                            'productName': product['name'],
                            'price': product['price']
                        }
                    })
                    
        # Insert activities
        if activities:
            result = db.useractivities.insert_many(activities)
            print(f"Inserted {len(result.inserted_ids)} activities")
            
    except Exception as e:
        print(f"Error setting up test data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    setup_test_data() 