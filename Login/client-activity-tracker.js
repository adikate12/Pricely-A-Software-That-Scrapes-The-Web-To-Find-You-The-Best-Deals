// client-activity-tracker.js - Client-side activity tracking
class ActivityTracker {
  constructor(id, username) {
    this.id = id;
    this.username = username;
    
    // Check if there's an existing session in sessionStorage
    this.sessionId = sessionStorage.getItem('activity_session_id');
    
    // If no session exists, create a new one
    if (!this.sessionId) {
      this.sessionId = this.generateSessionId();
      sessionStorage.setItem('activity_session_id', this.sessionId);
      
      // Notify server about new session
      this.notifyNewSession();
    }
    
    this.pageLoadTime = new Date();
    this.lastActivityTime = this.pageLoadTime;
    this.currentPage = window.location.pathname;
    this.setupEventListeners();
    console.log(`Activity tracker initialized for user: ${username} (ID: ${id}, Session: ${this.sessionId})`);
    
    // Track initial page view
    this.trackPageView();
  }
  
  generateSessionId() {
    return Date.now() + '-' + Math.random().toString(36).substring(2, 15);
  }
  
  // Notify server about new session
  notifyNewSession() {
    fetch('http://localhost:3000/api/activity-tracker/new-session', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        userId: this.id,
        username: this.username,
        sessionId: this.sessionId,
        timestamp: new Date().toISOString()
      })
    })
    .then(response => response.json())
    .then(data => console.log('New session registered:', data))
    .catch(error => console.error('Error registering new session:', error));
  }
  
  // Add method to clear session
  static clearSession() {
    const userId = sessionStorage.getItem('user_email');
    const sessionId = sessionStorage.getItem('activity_session_id');
    
    if (userId && sessionId) {
      // End the session on the server
      fetch(`http://localhost:3000/api/activity-tracker/end-session/${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sessionId })
      })
      .then(response => response.json())
      .then(data => {
        console.log('Session ended:', data);
        // Clear session storage
        sessionStorage.removeItem('activity_session_id');
      })
      .catch(error => console.error('Error ending session:', error));
    } else {
      // Just clear session storage if no user data
      sessionStorage.removeItem('activity_session_id');
    }
    
    console.log('Activity session cleared');
  }
  
  setupEventListeners() {
    // Track all button clicks
    document.addEventListener('click', (e) => {
      if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
        const button = e.target.tagName === 'BUTTON' ? e.target : e.target.closest('button');
        this.trackButtonClick(button);
      }
      
      // Track product clicks and phone views
      if (e.target.closest('.col') || e.target.closest('.product-item')) {
        const productElement = e.target.closest('.col') || e.target.closest('.product-item');
        this.trackProductClick(productElement);
      }
      
      // Track phone name views
      if (e.target.closest('.phone-name') || e.target.closest('.product-title')) {
        const phoneElement = e.target.closest('.phone-name') || e.target.closest('.product-title');
        this.trackPhoneView(phoneElement);
      }
      
      // Track navigation links
      if (e.target.tagName === 'A' && e.target.href && !e.target.href.includes('javascript:')) {
        this.trackNavigation(e.target);
      }
    });
    
    // Track social icon clicks
    document.querySelectorAll('.social, .col-icon a').forEach(icon => {
      icon.addEventListener('click', (e) => {
        this.sendActivity('social_click', window.location.pathname, {
          platform: e.currentTarget.querySelector('i')?.className || 'unknown',
          elementId: e.currentTarget.id || 'unknown',
          elementClass: e.currentTarget.className
        });
      });
    });
    
    // Track form inputs
    document.querySelectorAll('input, select, textarea').forEach(input => {
      input.addEventListener('focus', () => {
        this.fieldFocusTime = new Date();
        this.currentField = input.id || input.name || 'unknown';
      });
      
      input.addEventListener('blur', () => {
        if (this.fieldFocusTime && this.currentField) {
          const duration = new Date() - this.fieldFocusTime;
          this.sendActivity('field_interaction', window.location.pathname, {
            fieldId: this.currentField,
            fieldType: input.type || 'text',
            durationMs: duration
          });
          this.fieldFocusTime = null;
          this.currentField = null;
        }
      });
    });
    
    // Track page visibility changes
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') {
        this.trackPageDuration();
      } else if (document.visibilityState === 'visible') {
        this.pageLoadTime = new Date();
      }
    });
    
    // Track page exit
    window.addEventListener('beforeunload', () => {
      this.trackPageDuration();
    });
    
    // Track scroll depth
    let maxScroll = 0;
    window.addEventListener('scroll', () => {
      const scrollPercent = Math.round((window.scrollY + window.innerHeight) / document.documentElement.scrollHeight * 100);
      if (scrollPercent > maxScroll) {
        maxScroll = scrollPercent;
        if (maxScroll % 25 === 0) { // Track at 25%, 50%, 75%, 100%
          this.sendActivity('scroll_depth', window.location.pathname, {
            depth: maxScroll
          });
        }
      }
    });
  }
  
  trackButtonClick(button) {
    const action = 'button_click';
    const metadata = {
      buttonId: button.id || 'unknown',
      buttonText: button.textContent.trim(),
      buttonClass: button.className,
      buttonType: button.type || 'button'
    };
    
    this.sendActivity(action, window.location.pathname, metadata);
  }
  
  trackProductClick(productElement) {
    const action = 'product_click';
    const productName = productElement.querySelector('img')?.alt || 'Unknown Product';
    const productId = productElement.id || 'unknown';
    
    const metadata = {
      productId: productId,
      productName: productName,
      productClass: productElement.className
    };
    
    this.sendActivity(action, window.location.pathname, metadata);
  }
  
  trackNavigation(link) {
    const action = 'navigation';
    const metadata = {
      linkText: link.textContent.trim(),
      linkHref: link.href,
      linkId: link.id || 'unknown',
      linkClass: link.className
    };
    
    this.sendActivity(action, window.location.pathname, metadata);
  }
  
  trackPageView() {
    const action = 'page_view';
    const metadata = {
      pageTitle: document.title,
      referrer: document.referrer || 'direct',
      screenWidth: window.innerWidth,
      screenHeight: window.innerHeight
    };
    
    this.sendActivity(action, window.location.pathname, metadata);
  }
  
  trackPageDuration() {
    const now = new Date();
    const durationMs = now - this.pageLoadTime;
    const action = 'page_duration';
    const metadata = {
      durationMs: durationMs,
      durationSeconds: Math.floor(durationMs / 1000),
      pageTitle: document.title
    };
    
    this.sendActivity(action, window.location.pathname, metadata);
  }
  
  // Add new method to track phone views
  trackPhoneView(phoneElement) {
    const action = 'phone_view';
    const phoneName = phoneElement.textContent.trim();
    const phoneId = phoneElement.closest('[data-product-id]')?.dataset.productId || 'unknown';
    
    const metadata = {
      phoneId: phoneId,
      phoneName: phoneName,
      elementId: phoneElement.id || 'unknown',
      elementClass: phoneElement.className
    };
    
    this.sendActivity(action, window.location.pathname, metadata);
  }
  
  // Send activity data to backend
  sendActivity(action, page, metadata = {}) {
    // Use the PHP script to forward data to Node.js
    const data = {
      userId: this.id,
      username: this.username,
      action,
      page,
      sessionId: this.sessionId,
      timestamp: new Date().toISOString(),
      metadata: {
        ...metadata,
        userAgent: navigator.userAgent,
        language: navigator.language,
        platform: navigator.platform
      }
    };
    
    console.log('Sending activity data:', data);
    
    // Use the correct path to the PHP script
    fetch('../Login/track_interactions.php', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
      // This ensures the request still goes out even if page is unloading
      keepalive: true
    })
    .then(response => {
      console.log('Activity data sent successfully:', response.status);
      return response.json();
    })
    .then(data => {
      console.log('Response from server:', data);
    })
    .catch(error => console.error('Error sending activity data:', error));
  }
}

// Function to initialize tracker after user login
function initTracker(id, username) {
  // Check if already initialized
  if (!window.activityTracker) {
    window.activityTracker = new ActivityTracker(id, username);
  }
}

// Auto-initialize tracker if user data exists in sessionStorage
document.addEventListener('DOMContentLoaded', function() {
  // Try to get user info from sessionStorage
  const email = sessionStorage.getItem('user_email');
  const username = sessionStorage.getItem('user_name');
  
  console.log('Checking for user data in sessionStorage:', { email, username });
  
  if (email) {
    // Initialize tracker with email as ID and username
    initTracker(email, username || email);
  } else {
    console.log('No user data found in sessionStorage, initializing with anonymous user');
    // Initialize with anonymous user for testing
    initTracker('anonymous', 'Anonymous User');
  }
}); 