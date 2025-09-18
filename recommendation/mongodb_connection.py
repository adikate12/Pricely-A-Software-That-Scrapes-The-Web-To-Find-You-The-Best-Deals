from pymongo import MongoClient
from dotenv import load_dotenv
import os
import sys

def get_mongodb_client():
    """Get MongoDB client with connection from environment variables"""
    load_dotenv()
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/Pricely')
    
    try:
        client = MongoClient(mongodb_uri)
        # Test the connection
        client.admin.command('ping')
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}", file=sys.stderr)
        raise

def get_database():
    """Get the Pricely database"""
    client = get_mongodb_client()
    return client['Pricely']

def get_collection(collection_name):
    """Get a specific collection from the database"""
    db = get_database()
    return db[collection_name] 