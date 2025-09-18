// app.js
const express = require('express');
const path = require('path');
const cors = require('cors');
const dotenv = require('dotenv');
const { connectToMongoDB, closeConnection } = require('./mongodb');

// Load environment variables
dotenv.config();

const app = express();

// Middleware
app.use(cors({
  origin: '*', // Allow all origins for testing
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files from the Login directory
app.use(express.static(path.join(__dirname)));

// Import routes
const activityRoutes = require('./activity');
const activityTrackerRoutes = require('./activityTracker');
const { router: authRoutes } = require('./auth-handler');

// API routes
app.use('/api/activity', activityRoutes);
app.use('/api/activity-tracker', activityTrackerRoutes);
app.use('/api/auth', authRoutes);

// Default route - redirect to login page
app.get('/', (req, res) => {
    res.redirect('/login.html');
});

// Activity dashboard route
app.get('/dashboard', (req, res) => {
    res.sendFile(path.join(__dirname, 'activity-dashboard.html'));
});

// Test route to verify MongoDB connection
app.get('/api/test-connection', async (req, res) => {
  try {
    const db = await connectToMongoDB();
    res.json({ 
      status: 'success', 
      message: 'Connected to MongoDB',
      database: db.name
    });
  } catch (error) {
    res.status(500).json({ 
      status: 'error', 
      message: 'Failed to connect to MongoDB',
      error: error.message 
    });
  }
});

// Test route to view stored activities
app.get('/api/activities', async (req, res) => {
  try {
    const db = await connectToMongoDB();
    const activities = await db.collection('useractivities').find({}).limit(10).toArray();
    res.json(activities);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ 
    status: 'error', 
    message: 'Something went wrong!',
    error: process.env.NODE_ENV === 'development' ? err.message : 'Internal server error'
  });
});

// Start server
const PORT = process.env.PORT || 3000;

// Connect to MongoDB before starting the server
connectToMongoDB()
  .then(() => {
    app.listen(PORT, () => {
      console.log(`Server is running on port ${PORT}`);
      console.log(`Environment: ${process.env.NODE_ENV}`);
      console.log(`Access your application at: http://localhost:${PORT}/login.html`);
    });
  })
  .catch(err => {
    console.error('Failed to connect to MongoDB:', err);
    process.exit(1);
  });

// Handle graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received. Closing HTTP server and MongoDB connection...');
  await closeConnection();
  process.exit(0);
});
