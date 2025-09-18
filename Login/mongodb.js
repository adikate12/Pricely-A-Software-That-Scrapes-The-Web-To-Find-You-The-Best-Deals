// Login/mongodb.js
const mongoose = require('mongoose');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// MongoDB connection URI from environment variables
const uri = process.env.MONGODB_URI;

if (!uri) {
  throw new Error('MONGODB_URI environment variable is not defined');
}

// Connect to MongoDB
async function connectToMongoDB() {
  try {
    if (mongoose.connection.readyState === 1) {
      console.log('Using existing database connection');
      return mongoose.connection;
    }

    // Remove deprecated options
    await mongoose.connect(uri, {
      serverSelectionTimeoutMS: 5000,
    });

    console.log('✅ Connected to MongoDB Atlas');
    console.log(`✅ Database: ${mongoose.connection.name}`);
    
    return mongoose.connection;
  } catch (error) {
    console.error('❌ MongoDB connection error:', error);
    throw error;
  }
}

// Get database instance
function getDb() {
  if (mongoose.connection.readyState !== 1) {
    throw new Error('Database not initialized. Call connectToMongoDB() first.');
  }
  return mongoose.connection;
}

// Close the database connection
async function closeConnection() {
  try {
    await mongoose.connection.close();
    console.log('MongoDB connection closed');
  } catch (error) {
    console.error('Error closing MongoDB connection:', error);
    throw error;
  }
}

module.exports = {
  connectToMongoDB,
  getDb,
  closeConnection,
  mongoose
};
