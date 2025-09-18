from pymongo import MongoClient
from dotenv import load_dotenv
import os

def check_mongodb():
    """Check MongoDB connection and collections"""
    try:
        # Load environment variables
        load_dotenv()
        mongo_uri = os.getenv('MONGODB_URI')
        
        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        db = client.get_database()
        
        print(f"\nConnected to MongoDB: {db.name}")
        
        # List all collections
        collections = db.list_collection_names()
        print("\nAvailable collections:")
        for collection in collections:
            count = db[collection].count_documents({})
            print(f"- {collection}: {count} documents")
            
            # Show sample document structure
            if count > 0:
                sample = db[collection].find_one()
                print(f"  Sample document structure:")
                print(f"  {sample}")
                
        return True
        
    except Exception as e:
        print(f"Error checking MongoDB: {e}")
        return False

if __name__ == "__main__":
    check_mongodb() 