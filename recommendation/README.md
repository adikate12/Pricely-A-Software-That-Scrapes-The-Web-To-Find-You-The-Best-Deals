# Product Recommendation System

A hybrid recommendation system that combines content-based and collaborative filtering approaches to provide personalized product recommendations based on user activity data.

## Features

- Content-based filtering using product attributes
- Collaborative filtering using user-item interactions
- Hybrid recommendation approach
- RESTful API endpoints
- MongoDB integration for data storage
- User preference tracking

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with the following variables:
```
MONGODB_URI=your_mongodb_connection_string
PORT=5000
```

3. Ensure your MongoDB database has the following collections:
- `useractivities`: Stores user interaction data
- `products`: Stores product information

4. Place your product data JSON files in the `../Home` directory:
- `amazon_data.json`
- `croma_data.json`
- `flipkart_data.json`

## Running the Application

Start the Flask server:
```bash
python app.py
```

The server will start on `http://localhost:5000` by default.

## API Endpoints

### Get All Recommendations
```
GET /api/recommendations/user/<user_id>
```

### Get Content-Based Recommendations
```
GET /api/recommendations/content-based/<user_id>
```

### Get Collaborative Recommendations
```
GET /api/recommendations/collaborative/<user_id>
```

### Get Hybrid Recommendations
```
GET /api/recommendations/hybrid/<user_id>
```

### Get User Preferences
```
GET /api/preferences/<user_id>
```

## Response Format

All endpoints return JSON responses in the following format:
```json
{
    "success": true,
    "data": {
        // Response data
    }
}
```

In case of errors:
```json
{
    "success": false,
    "error": "Error message"
}
```

## Architecture

The recommendation system consists of three main components:

1. **Content-Based Filtering**
   - Uses product attributes (brand, category, name)
   - Scores products based on user preferences
   - Good for cold-start scenarios

2. **Collaborative Filtering**
   - Uses user-item interaction matrix
   - Finds similar users using cosine similarity
   - Recommends products based on similar users' preferences

3. **Hybrid Approach**
   - Combines both content-based and collaborative filtering
   - Weights recommendations from both approaches
   - Provides more robust recommendations

## Error Handling

The system includes comprehensive error handling for:
- Database connection issues
- Missing or invalid data
- User not found
- Invalid recommendations

## Performance Considerations

- Recommendations are cached to improve response times
- Batch processing for large datasets
- Efficient MongoDB queries using indexes
- Asynchronous processing for heavy computations 