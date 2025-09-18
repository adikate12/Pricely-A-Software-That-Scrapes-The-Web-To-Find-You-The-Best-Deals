import os
import sys
from dotenv import load_dotenv
from enhanced_recommendation_engine import EnhancedRecommendationEngine

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize recommendation engine with correct paths
    print("Initializing recommendation engine...")
    engine = EnhancedRecommendationEngine(
        amazon_path="../Amazon/amazon_products.json",
        croma_path="../Croma/croma_mobiles_2.json",
        flipkart_path="../Home/flipkart_mobiles_2.json"
    )
    
    # Test user
    test_user = "admin@gmail.com"
    
    # Get user preferences
    print(f"\nGetting preferences for user: {test_user}")
    preferences = engine.user_preferences[test_user]
    print("User preferences:")
    print(f"Viewed products: {preferences['viewed_products']}")
    print(f"Clicked products: {preferences['clicked_products']}")
    print(f"Viewed brands: {preferences['viewed_brands']}")
    print(f"Viewed categories: {preferences['viewed_categories']}")
    
    # Test content-based recommendations
    print("\nTesting content-based recommendations...")
    content_recs = engine.content_based_filtering(test_user)
    print("\nContent-based recommendations:")
    for rec in content_recs:
        print(f"- {rec['name']} ({rec['brand']}) - ₹{rec['price']}")
    
    # Test collaborative recommendations
    print("\nTesting collaborative recommendations...")
    collab_recs = engine.collaborative_filtering(test_user)
    print("\nCollaborative recommendations:")
    for rec in collab_recs:
        print(f"- {rec['name']} ({rec['brand']}) - ₹{rec['price']}")
    
    # Test hybrid recommendations
    print("\nTesting hybrid recommendations...")
    hybrid_recs = engine.get_recommendations(test_user)
    print("\nHybrid recommendations:")
    for rec in hybrid_recs:
        print(f"- {rec['name']} ({rec['brand']}) - ₹{rec['price']}")

if __name__ == "__main__":
    main() 