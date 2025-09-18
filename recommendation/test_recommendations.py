from recommendation_engine import RecommendationEngine
import os
from dotenv import load_dotenv

def print_recommendations(title, recs):
    """Helper function to print recommendations"""
    print(f"\n{title}:")
    if not recs:
        print("No recommendations available")
        return
        
    for i, rec in enumerate(recs[:5], 1):
        try:
            product = rec['product']
            score = rec.get('final_score', rec.get('score', 0))
            print(f"{i}. {product['name']} (₹{product['price']:,.2f})")
            print(f"   Brand: {product['brand']}")
            print(f"   Source: {product['source']}")
            print(f"   Score: {score:.2f}")
        except Exception as e:
            print(f"Error displaying recommendation {i}: {e}")

def test_recommendations():
    """Test the recommendation engine with the new activity data"""
    try:
        # Initialize the recommendation engine
        engine = RecommendationEngine()
        
        # Connect to MongoDB and load data
        if not engine.connect_to_mongodb():
            print("Failed to connect to MongoDB")
            return False
            
        if not engine.load_product_data():
            print("Failed to load product data")
            return False
            
        if not engine.load_user_activities():
            print("Failed to load user activities")
            return False
            
        # Extract user preferences
        engine.extract_user_preferences()
        
        # Get recommendations for the admin user
        user_id = "admin@gmail.com"
        print(f"\nGenerating recommendations for user: {user_id}")
        
        # Generate recommendations
        recommendations = engine.generate_recommendations(user_id)
        
        # Print recommendations
        print_recommendations("Content-Based Recommendations", recommendations['content_based'])
        print_recommendations("Collaborative Recommendations", recommendations['collaborative'])
        print_recommendations("Hybrid Recommendations", recommendations['hybrid'])
        
        return True
        
    except Exception as e:
        print(f"Error testing recommendations: {e}")
        return False

if __name__ == "__main__":
    test_recommendations() 