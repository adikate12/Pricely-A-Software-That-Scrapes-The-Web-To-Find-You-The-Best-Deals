//activity.js
const express = require('express');
const router = express.Router();
const { getDb } = require('./mongodb');

// Import the verifyToken middleware from auth-handler
const { verifyToken } = require('./auth-handler');

// Track user activity
router.post('/track', verifyToken, async (req, res) => {
  try {
    const db = getDb();
    const collection = db.collection('useractivities');

    const activity = {
      userId: req.user.id,
      email: req.user.email,
      username: req.user.username,
      action: req.body.action,
      page: req.body.page,
      timestamp: new Date(),
      metadata: {
        productId: req.body.productId,
        productName: req.body.productName,
        brand: req.body.brand,
        category: req.body.category,
        price: req.body.price,
        source: req.body.source
      }
    };

    await collection.insertOne(activity);
    res.status(201).json({ 
      status: 'success', 
      message: 'Activity tracked successfully',
      activity 
    });
  } catch (error) {
    console.error('Error tracking activity:', error);
    res.status(500).json({ 
      status: 'error', 
      message: 'Failed to track activity',
      error: error.message 
    });
  }
});

// Get user activities
router.get('/user/:userId', verifyToken, async (req, res) => {
  try {
    const db = getDb();
    const collection = db.collection('useractivities');
    
    const activities = await collection
      .find({ userId: req.params.userId })
      .sort({ timestamp: -1 })
      .limit(50)
      .toArray();

    res.json({ 
      status: 'success', 
      activities 
    });
  } catch (error) {
    console.error('Error fetching activities:', error);
    res.status(500).json({ 
      status: 'error', 
      message: 'Failed to fetch activities',
      error: error.message 
    });
  }
});

// Get recent activities
router.get('/recent', verifyToken, async (req, res) => {
  try {
    const db = getDb();
    const collection = db.collection('useractivities');
    
    const activities = await collection
      .find()
      .sort({ timestamp: -1 })
      .limit(20)
      .toArray();

    res.json({ 
      status: 'success', 
      activities 
    });
  } catch (error) {
    console.error('Error fetching recent activities:', error);
    res.status(500).json({ 
      status: 'error', 
      message: 'Failed to fetch recent activities',
      error: error.message 
    });
  }
});

module.exports = router;
