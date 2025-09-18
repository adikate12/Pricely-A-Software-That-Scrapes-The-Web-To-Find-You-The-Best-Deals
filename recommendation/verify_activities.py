from pymongo import MongoClient
import os
from dotenv import load_dotenv

def verify_activities():
    """Verify the generated activities in the database"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Connect to MongoDB
        mongo_uri = os.getenv('MONGODB_URI')
        client = MongoClient(mongo_uri)
        db = client.get_database()
        collection = db.useractivities
        
        # Get statistics
        total_activities = collection.count_documents({})
        unique_users = collection.distinct("userId")
        activity_types = collection.distinct("action")
        
        print(f"\nDatabase Verification Results:")
        print(f"Total activities: {total_activities}")
        print(f"Unique users: {len(unique_users)}")
        print(f"Activity types: {activity_types}")
        
        # Get sample activities
        print("\nSample activities:")
        for doc in collection.find().limit(3):
            print(f"\nUser: {doc.get('username', 'Unknown')}")
            print(f"Action: {doc.get('action')}")
            print(f"Timestamp: {doc.get('timestamp')}")
            print(f"Metadata: {doc.get('metadata', {})}")
            
        return True
        
    except Exception as e:
        print(f"Error verifying activities: {e}")
        return False

if __name__ == "__main__":
    verify_activities() 