import json
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def convert_price(price_str):
    """Convert price string to float, handling various formats and invalid values"""
    if not price_str or price_str == 'N/A':
        return 0.0
    try:
        # Remove currency symbol and commas
        price_str = price_str.replace('₹', '').replace(',', '').strip()
        return float(price_str)
    except (ValueError, TypeError):
        return 0.0

def generate_test_activities():
    """Generate test user activities with different preferences"""
    try:
        # Connect to MongoDB Atlas
        mongo_uri = os.getenv('MONGODB_URI')
        client = MongoClient(mongo_uri)
        db = client.get_database()
        
        # Load product data
        product_data = {}
        
        # Load Amazon data
        with open('../Amazon/amazon_products.json', 'r', encoding='utf-8') as f:
            amazon_data = json.load(f)
            for item in amazon_data:
                product_id = str(len(product_data) + 1)
                product_data[product_id] = {
                    'id': product_id,
                    'name': item.get('Product Name', ''),
                    'brand': item.get('Product Name', '').split()[0],
                    'price': convert_price(item.get('Price'))
                }
                
        # Load Croma data
        with open('../Croma/croma_mobiles_2.json', 'r', encoding='utf-8') as f:
            croma_data = json.load(f)
            for item in croma_data:
                product_id = str(len(product_data) + 1)
                product_data[product_id] = {
                    'id': product_id,
                    'name': item.get('Product Name', ''),
                    'brand': item.get('Product Name', '').split()[0],
                    'price': convert_price(item.get('Price'))
                }
                
        # Load Flipkart data
        with open('../Home/flipkart_mobiles_2.json', 'r', encoding='utf-8') as f:
            flipkart_data = json.load(f)
            for item in flipkart_data:
                product_id = str(len(product_data) + 1)
                product_data[product_id] = {
                    'id': product_id,
                    'name': item.get('Product Name', ''),
                    'brand': item.get('Product Name', '').split()[0],
                    'price': convert_price(item.get('Price'))
                }
                
        # Get existing users from MongoDB
        collection = db.useractivities
        existing_users = collection.distinct('userId')
        
        if not existing_users:
            print("No existing users found in the database")
            return False
            
        # Generate activities for each existing user
        activities = []
        base_time = datetime.now() - timedelta(days=30)
        
        for user_id in existing_users:
            # Get user's username
            user_doc = collection.find_one({'userId': user_id})
            username = user_doc.get('username', user_id)
            
            # Generate 3-5 sessions per user
            num_sessions = random.randint(3, 5)
            
            for session in range(num_sessions):
                session_id = f"{int(base_time.timestamp() * 1000)}-{random.randint(1000, 9999)}"
                session_start = base_time + timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                # Add session start activity
                activities.append({
                    'userId': user_id,
                    'username': username,
                    'sessionId': session_id,
                    'action': 'session_start',
                    'page': '/Pricely/Home/index.html',
                    'timestamp': session_start.isoformat(),
                    'isActive': False,
                    'startTime': session_start.isoformat(),
                    'metadata': {
                        'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'ip': '127.0.0.1'
                    },
                    'endTime': (session_start + timedelta(minutes=random.randint(5, 30))).isoformat()
                })
                
                # Generate 10-20 activities per session
                num_activities = random.randint(10, 20)
                
                for i in range(num_activities):
                    # Select a random product
                    product = random.choice(list(product_data.values()))
                    timestamp = session_start + timedelta(
                        minutes=random.randint(1, 30),
                        seconds=random.randint(0, 59)
                    )
                    
                    # Generate random activity type
                    activity_type = random.choice([
                        'phone_view',
                        'product_click',
                        'button_click',
                        'navigation',
                        'scroll_depth'
                    ])
                    
                    if activity_type == 'phone_view':
                        activities.append({
                            'userId': user_id,
                            'username': username,
                            'sessionId': session_id,
                            'action': 'phone_view',
                            'page': '/Pricely/Home/index.html',
                            'timestamp': timestamp.isoformat(),
                            'isActive': False,
                            'metadata': {
                                'productId': product['id'],
                                'phoneName': product['name'],
                                'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                                'ip': '127.0.0.1'
                            }
                        })
                    elif activity_type == 'product_click':
                        activities.append({
                            'userId': user_id,
                            'username': username,
                            'sessionId': session_id,
                            'action': 'product_click',
                            'page': '/Pricely/Home/index.html',
                            'timestamp': timestamp.isoformat(),
                            'isActive': False,
                            'metadata': {
                                'productId': product['id'],
                                'productName': product['name'],
                                'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                                'ip': '127.0.0.1'
                            }
                        })
                    elif activity_type == 'button_click':
                        activities.append({
                            'userId': user_id,
                            'username': username,
                            'sessionId': session_id,
                            'action': 'button_click',
                            'page': '/Pricely/Home/index.html',
                            'timestamp': timestamp.isoformat(),
                            'isActive': False,
                            'metadata': {
                                'buttonId': f'btn_{random.randint(1, 10)}',
                                'buttonText': random.choice(['View Details', 'Compare', 'Add to Cart', 'Buy Now']),
                                'buttonClass': 'btn btn-primary',
                                'buttonType': 'button',
                                'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                                'ip': '127.0.0.1'
                            }
                        })
                    elif activity_type == 'navigation':
                        activities.append({
                            'userId': user_id,
                            'username': username,
                            'sessionId': session_id,
                            'action': 'navigation',
                            'page': '/Pricely/Home/index.html',
                            'timestamp': timestamp.isoformat(),
                            'isActive': False,
                            'metadata': {
                                'linkText': random.choice(['Home', 'Products', 'About', 'Contact']),
                                'linkHref': random.choice(['/Pricely/Home/index.html', '/Pricely/Home/products.html', '/Pricely/Home/about.html', '/Pricely/Home/contact.html']),
                                'linkId': f'nav_{random.randint(1, 5)}',
                                'linkClass': 'nav-link',
                                'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                                'ip': '127.0.0.1'
                            }
                        })
                    elif activity_type == 'scroll_depth':
                        activities.append({
                            'userId': user_id,
                            'username': username,
                            'sessionId': session_id,
                            'action': 'scroll_depth',
                            'page': '/Pricely/Home/index.html',
                            'timestamp': timestamp.isoformat(),
                            'isActive': False,
                            'metadata': {
                                'depth': random.choice([25, 50, 75, 100]),
                                'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                                'ip': '127.0.0.1'
                            }
                        })
                        
        # Insert activities into MongoDB
        collection.insert_many(activities)
        
        print(f"Generated {len(activities)} test activities for {len(existing_users)} users")
        return True
        
    except Exception as e:
        print(f"Error generating test activities: {e}")
        return False

if __name__ == "__main__":
    generate_test_activities() 