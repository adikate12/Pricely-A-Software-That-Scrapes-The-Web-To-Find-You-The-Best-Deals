// activity-tracker.js - Client-side activity tracking
class ActivityTracker {
  constructor(id, username) {
    this.id = id;
    this.username = username;
    this.sessionId = this.generateSessionId();
    this.pageLoadTime = new Date();
    this.lastActivityTime = this.pageLoadTime;
    this.setupEventListeners();
    console.log(`Activity tracker initialized for user: ${username} (ID: ${id})`);
  }
  
  generateSessionId() {
    return Date.now() + '-' + Math.random().toString(36).substring(2, 15);
  }
  
  setupEventListeners() {
    // Track all button clicks
    document.addEventListener('click', (e) => {
      if (e.target.tagName === 'BUTTON') {
        this.trackButtonClick(e.target);
      }
    });
    
    // Track social icon clicks
    document.querySelectorAll('.social').forEach(icon => {
      icon.addEventListener('click', (e) => {
        this.sendActivity('social_click', window.location.pathname, {
          platform: e.currentTarget.querySelector('i').className
        });
      });
    });
    
    // Track overlay button interactions
    const overlayBtn = document.getElementById('overlayBtn');
    if (overlayBtn) {
      overlayBtn.addEventListener('click', () => {
        const container = document.getElementById('container');
        this.sendActivity('toggle_panel', window.location.pathname, {
          element: 'overlayBtn',
          newState: container.classList.contains('right-panel-active') ? 'signup' : 'signin'
        });
      });
    }
    
    // Track switch panel buttons
    const signInBtn = document.getElementById('signIn');
    if (signInBtn) {
      signInBtn.addEventListener('click', () => {
        this.sendActivity('switch_panel', window.location.pathname, {
          action: 'to_signin'
        });
      });
    }
    
    const signUpBtn = document.getElementById('signUp');
    if (signUpBtn) {
      signUpBtn.addEventListener('click', () => {
        this.sendActivity('switch_panel', window.location.pathname, {
          action: 'to_signup'
        });
      });
    }
    
    // Track form inputs
    document.querySelectorAll('input').forEach(input => {
      input.addEventListener('focus', () => {
        this.fieldFocusTime = new Date();
        this.currentField = input.id || input.name;
      });
      
      input.addEventListener('blur', () => {
        if (this.fieldFocusTime && this.currentField) {
          const duration = new Date() - this.fieldFocusTime;
          this.sendActivity('field_interaction', window.location.pathname, {
            fieldId: this.currentField,
            fieldType: input.type,
            durationMs: duration
          });
          this.fieldFocusTime = null;
          this.currentField = null;
        }
      });
    });
    
    // Track page exit
    window.addEventListener('beforeunload', () => {
      this.trackPageDuration();
    });
  }
  
  trackButtonClick(button) {
    const action = 'button_click';
    const metadata = {
      buttonId: button.id || 'unknown',
      buttonText: button.textContent.trim(),
      buttonClass: button.className
    };
    
    this.sendActivity(action, window.location.pathname, metadata);
  }
  
  trackPageDuration() {
    const now = new Date();
    const durationMs = now - this.pageLoadTime;
    const action = 'page_view';
    const metadata = {
      durationMs: durationMs,
      durationSeconds: Math.floor(durationMs / 1000)
    };
    
    this.sendActivity(action, window.location.pathname, metadata);
  }
  
  // Send activity data to backend
  sendActivity(action, page, metadata = {}) {
    const token = localStorage.getItem('token');
    
    fetch('/api/activity-tracker/track', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        action,
        page,
        sessionId: this.sessionId,
        metadata
      }),
      // This ensures the request still goes out even if page is unloading
      keepalive: true
    }).catch(error => console.error('Error sending activity data:', error));
  }
}

// Function to initialize tracker after user login
function initTracker(id, username) {
  // Check if already initialized
  if (!window.activityTracker) {
    window.activityTracker = new ActivityTracker(id, username);
  }
}

// Auto-initialize tracker if user data exists in localStorage
document.addEventListener('DOMContentLoaded', function() {
  const id = localStorage.getItem('id');
  const username = localStorage.getItem('username');
  
  if (id && username) {
    initTracker(id, username);
  }
}); 