// auth-handler.js - Server-side authentication handler
const express = require('express');
const router = express.Router();
const { getDb } = require('./mongodb');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

// Middleware to verify JWT token
const verifyToken = (req, res, next) => {
  const token = req.headers['x-access-token'] || req.headers['authorization'];
  
  if (!token) {
    return res.status(403).json({ 
      status: 'error',
      message: 'No token provided' 
    });
  }
  
  try {
    const decoded = jwt.verify(token.replace('Bearer ', ''), process.env.JWT_SECRET || 'your-secret-key');
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(401).json({ 
      status: 'error',
      message: 'Invalid or expired token' 
    });
  }
};

// Register new user
router.post('/register', async (req, res) => {
  try {
    const db = getDb();
    const users = db.collection('users');

    // Check if user already exists
    const existingUser = await users.findOne({ username: req.body.username });
    if (existingUser) {
      return res.status(400).json({ 
        status: 'error',
        message: 'Username already exists' 
      });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(req.body.password, 10);

    // Create new user
    const newUser = {
      username: req.body.username,
      password: hashedPassword,
      email: req.body.email,
      createdAt: new Date()
    };

    await users.insertOne(newUser);
    res.status(201).json({ 
      status: 'success',
      message: 'User registered successfully' 
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ 
      status: 'error',
      message: 'Failed to register user',
      error: error.message 
    });
  }
});

// Login user
router.post('/login', async (req, res) => {
  try {
    const db = getDb();
    const users = db.collection('users');

    // Find user
    const user = await users.findOne({ username: req.body.username });
    if (!user) {
      return res.status(401).json({ 
        status: 'error',
        message: 'Invalid username or password' 
      });
    }

    // Verify password
    const validPassword = await bcrypt.compare(req.body.password, user.password);
    if (!validPassword) {
      return res.status(401).json({ 
        status: 'error',
        message: 'Invalid username or password' 
      });
    }

    // Generate JWT token
    const token = jwt.sign(
      { id: user._id, username: user.username },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '24h' }
    );

    res.json({ 
      status: 'success',
      message: 'Login successful',
      token,
      user: {
        id: user._id,
        username: user.username,
        email: user.email
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ 
      status: 'error',
      message: 'Failed to login',
      error: error.message 
    });
  }
});

// Get user profile (protected route)
router.get('/profile', verifyToken, async (req, res) => {
  try {
    const db = getDb();
    const usersCollection = db.collection('users');
    
    const user = await usersCollection.findOne(
      { _id: req.user.id },
      { projection: { password: 0 } }
    );
    
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    
    res.status(200).json({ user });
  } catch (error) {
    console.error('Profile error:', error);
    res.status(500).json({ message: 'Server error fetching profile' });
  }
});

module.exports = {
  router,
  verifyToken
};
