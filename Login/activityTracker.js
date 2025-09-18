// activityTracker.js - Server-side route handler for activity tracking
const express = require('express');
const router = express.Router();
const { getDb } = require('./mongodb');
const { verifyToken } = require('./auth-handler');

// Register a new session
router.post('/new-session', async (req, res) => {
  try {
    const db = getDb();
    const collection = db.collection('useractivities');
    
    const { userId, username, sessionId, timestamp } = req.body;
    
    // End any existing active sessions for this user
    await collection.updateMany(
      { userId: userId, isActive: true },
      { $set: { isActive: false, endTime: new Date() } }
    );
    
    // Create a session record
    const sessionRecord = {
      userId: userId,
      username: username,
      sessionId: sessionId,
      action: 'session_start',
      page: '/',
      timestamp: new Date(timestamp),
      isActive: true,
      startTime: new Date(timestamp),
      metadata: {
        userAgent: req.headers['user-agent'] || 'unknown',
        ip: req.ip || 'unknown'
      }
    };
    
    await collection.insertOne(sessionRecord);
    
    res.status(201).json({ 
      status: 'success', 
      message: 'New session registered',
      session: sessionRecord
    });
  } catch (error) {
    console.error('Error registering new session:', error);
    res.status(500).json({ 
      status: 'error', 
      message: 'Failed to register new session',
      error: error.message 
    });
  }
});

// Track user activity
router.post('/track', async (req, res) => {
  try {
    const db = getDb();
    const collection = db.collection('useractivities');

    // Extract user info and session from request body
    const userId = req.body.userId || 'anonymous';
    const username = req.body.username || 'anonymous';
    const sessionId = req.body.sessionId;

    // Check if this session exists and is active
    const existingSession = await collection.findOne({
      userId: userId,
      sessionId: sessionId,
      isActive: true
    });

    // If no active session found, create a new one
    if (!existingSession) {
      // End any existing active sessions for this user
      await collection.updateMany(
        { userId: userId, isActive: true },
        { $set: { isActive: false, endTime: new Date() } }
      );
      
      // Create a new session record
      const sessionRecord = {
        userId: userId,
        username: username,
        sessionId: sessionId,
        action: 'session_start',
        page: req.body.page || '/',
        timestamp: new Date(),
        isActive: true,
        startTime: new Date(),
        metadata: {
          userAgent: req.headers['user-agent'] || 'unknown',
          ip: req.ip || 'unknown'
        }
      };
      
      await collection.insertOne(sessionRecord);
    }

    // Create activity object
    const activity = {
      userId: userId,
      username: username,
      sessionId: sessionId,
      action: req.body.action,
      page: req.body.page,
      timestamp: req.body.timestamp ? new Date(req.body.timestamp) : new Date(),
      metadata: req.body.metadata || {},
      isActive: true // Mark this session as active
    };

    console.log('Storing activity:', activity);
    
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

// Get user session activities
router.get('/session/:sessionId', async (req, res) => {
  try {
    const db = getDb();
    const collection = db.collection('useractivities');
    
    const activities = await collection
      .find({ sessionId: req.params.sessionId })
      .sort({ timestamp: 1 })
      .toArray();

    res.json({ 
      status: 'success', 
      activities 
    });
  } catch (error) {
    console.error('Error fetching session activities:', error);
    res.status(500).json({ 
      status: 'error', 
      message: 'Failed to fetch session activities',
      error: error.message 
    });
  }
});

// Get active session for a user
router.get('/active-session/:userId', async (req, res) => {
  try {
    const db = getDb();
    const collection = db.collection('useractivities');
    
    const activeSession = await collection
      .findOne(
        { userId: req.params.userId, isActive: true },
        { sort: { timestamp: -1 } }
      );

    res.json({ 
      status: 'success', 
      session: activeSession 
    });
  } catch (error) {
    console.error('Error fetching active session:', error);
    res.status(500).json({ 
      status: 'error', 
      message: 'Failed to fetch active session',
      error: error.message 
    });
  }
});

// End user session
router.post('/end-session/:userId', async (req, res) => {
  try {
    const db = getDb();
    const collection = db.collection('useractivities');
    
    const { sessionId } = req.body;
    
    // Update query based on whether sessionId is provided
    const query = sessionId 
      ? { userId: req.params.userId, sessionId: sessionId, isActive: true }
      : { userId: req.params.userId, isActive: true };
    
    const result = await collection.updateMany(
      query,
      { $set: { isActive: false, endTime: new Date() } }
    );

    res.json({ 
      status: 'success', 
      message: 'Session ended successfully',
      modifiedCount: result.modifiedCount
    });
  } catch (error) {
    console.error('Error ending session:', error);
    res.status(500).json({ 
      status: 'error', 
      message: 'Failed to end session',
      error: error.message 
    });
  }
});

// Get user activity summary
router.get('/summary/:userId', async (req, res) => {
  try {
    const db = getDb();
    const collection = db.collection('useractivities');
    
    // Get activity counts by type
    const activityCounts = await collection.aggregate([
      { $match: { userId: req.params.userId } },
      { $group: { 
          _id: '$action', 
          count: { $sum: 1 } 
        } 
      }
    ]).toArray();
    
    // Get page view durations
    const pageDurations = await collection.aggregate([
      { $match: { 
          userId: req.params.userId,
          action: 'page_duration',
          'metadata.durationMs': { $exists: true }
        } 
      },
      { $group: { 
          _id: '$page', 
          avgDuration: { $avg: '$metadata.durationMs' },
          totalViews: { $sum: 1 }
        } 
      }
    ]).toArray();
    
    // Get most viewed phones
    const phoneViews = await collection.aggregate([
      { $match: { 
          userId: req.params.userId,
          action: 'phone_view'
        } 
      },
      { $group: { 
          _id: '$metadata.phoneId', 
          phoneName: { $first: '$metadata.phoneName' },
          count: { $sum: 1 },
          lastViewed: { $max: '$timestamp' }
        } 
      },
      { $sort: { count: -1 } },
      { $limit: 10 }
    ]).toArray();
    
    // Get most viewed products
    const productViews = await collection.aggregate([
      { $match: { 
          userId: req.params.userId,
          action: 'product_click'
        } 
      },
      { $group: { 
          _id: '$metadata.productId', 
          productName: { $first: '$metadata.productName' },
          count: { $sum: 1 }
        } 
      },
      { $sort: { count: -1 } },
      { $limit: 10 }
    ]).toArray();
    
    // Get most clicked buttons
    const buttonClicks = await collection.aggregate([
      { $match: { 
          userId: req.params.userId,
          action: 'button_click'
        } 
      },
      { $group: { 
          _id: '$metadata.buttonId', 
          buttonText: { $first: '$metadata.buttonText' },
          count: { $sum: 1 }
        } 
      },
      { $sort: { count: -1 } },
      { $limit: 10 }
    ]).toArray();
    
    res.json({ 
      status: 'success',
      summary: {
        activityCounts,
        pageDurations,
        phoneViews,
        productViews,
        buttonClicks
      }
    });
  } catch (error) {
    console.error('Error fetching activity summary:', error);
    res.status(500).json({ 
      status: 'error', 
      message: 'Failed to fetch activity summary',
      error: error.message 
    });
  }
});

// Get phone view history for a user
router.get('/phone-history/:userId', async (req, res) => {
  try {
    const db = getDb();
    const collection = db.collection('useractivities');
    
    const phoneHistory = await collection.aggregate([
      { $match: { 
          userId: req.params.userId,
          action: 'phone_view'
        } 
      },
      { $sort: { timestamp: -1 } },
      { $group: {
          _id: '$metadata.phoneId',
          phoneName: { $first: '$metadata.phoneName' },
          viewCount: { $sum: 1 },
          firstViewed: { $min: '$timestamp' },
          lastViewed: { $max: '$timestamp' },
          sessions: { $addToSet: '$sessionId' }
        } 
      },
      { $project: {
          _id: 1,
          phoneName: 1,
          viewCount: 1,
          firstViewed: 1,
          lastViewed: 1,
          sessionCount: { $size: '$sessions' }
        } 
      },
      { $sort: { viewCount: -1 } }
    ]).toArray();
    
    res.json({ 
      status: 'success', 
      phoneHistory 
    });
  } catch (error) {
    console.error('Error fetching phone history:', error);
    res.status(500).json({ 
      status: 'error', 
      message: 'Failed to fetch phone history',
      error: error.message 
    });
  }
});

// Get all activities for a user
router.get('/user/:userId', async (req, res) => {
  try {
    const db = getDb();
    const collection = db.collection('useractivities');
    
    const activities = await collection
      .find({ userId: req.params.userId })
      .sort({ timestamp: -1 })
      .limit(100)
      .toArray();
    
    res.json({ 
      status: 'success', 
      activities 
    });
  } catch (error) {
    console.error('Error fetching user activities:', error);
    res.status(500).json({ 
      status: 'error', 
      message: 'Failed to fetch user activities',
      error: error.message 
    });
  }
});

// Get all activities for a specific page
router.get('/page/:pagePath', async (req, res) => {
  try {
    const db = getDb();
    const collection = db.collection('useractivities');
    
    const activities = await collection
      .find({ page: req.params.pagePath })
      .sort({ timestamp: -1 })
      .limit(100)
      .toArray();
    
    res.json({ 
      status: 'success', 
      activities 
    });
  } catch (error) {
    console.error('Error fetching page activities:', error);
    res.status(500).json({ 
      status: 'error', 
      message: 'Failed to fetch page activities',
      error: error.message 
    });
  }
});

module.exports = router;