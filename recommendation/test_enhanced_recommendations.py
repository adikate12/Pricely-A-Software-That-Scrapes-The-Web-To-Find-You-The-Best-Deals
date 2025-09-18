import os
import sys
import json
from recommendation_engine import RecommendationEngine

def main():
    try:
        # Get user email from command line argument
        if len(sys.argv) < 2:
            print(json.dumps({'error': 'No user email provided'}), file=sys.stderr)
            return
            
        user_email = sys.argv[1]
        print(f"Processing recommendations for user: {user_email}", file=sys.stderr)
        
        # Initialize recommendation engine
        engine = RecommendationEngine()
        
        # Get recommendations
        recommendations = engine.get_recommendations(user_email)
        
        # If no recommendations, return empty list
        if not recommendations:
            print(json.dumps([]))
            return
            
        print(f"Found {len(recommendations)} recommendations", file=sys.stderr)
        
        # Convert recommendations to JSON-serializable format
        serializable_recommendations = []
        for rec in recommendations:
            try:
                serializable_rec = {
                    'id': str(rec.get('id', '')),
                    'name': str(rec.get('name', '')),
                    'brand': str(rec.get('brand', '')),
                    'price': float(str(rec.get('price', '0')).replace('₹', '').replace(',', '').strip() or 0),
                    'source': str(rec.get('source', '')),
                    'image_url': str(rec.get('image_url', '')),
                    'product_url': str(rec.get('product_url', ''))
                }
                serializable_recommendations.append(serializable_rec)
            except Exception as e:
                print(f'Error processing recommendation: {str(e)}', file=sys.stderr)
                continue
        
        # Output as JSON
        result = json.dumps(serializable_recommendations)
        print(result)
        
    except Exception as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr)
        print(json.dumps([]))  # Return empty list on error
        
if __name__ == "__main__":
    main() 