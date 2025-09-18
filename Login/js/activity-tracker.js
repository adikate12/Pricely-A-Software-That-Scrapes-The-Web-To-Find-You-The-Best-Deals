class ActivityTracker {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.userId = null;
        this.username = null;
        this.baseUrl = '/Login/track_interactions.php';
    }

    // Generate a unique session ID
    generateSessionId() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    // Set user information
    setUserInfo(userId, username) {
        this.userId = userId;
        this.username = username;
    }

    // Track user activity
    async trackActivity(action, page, metadata = {}) {
        if (!this.userId || !this.username) {
            console.warn('User information not set. Activity tracking skipped.');
            return;
        }

        const activityData = {
            user_id: this.userId,
            username: this.username,
            action: action,
            page: page,
            session_id: this.sessionId,
            timestamp: new Date().toISOString(),
            metadata: metadata
        };

        try {
            const response = await fetch(this.baseUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(activityData)
            });

            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Failed to track activity');
            }

            return result;
        } catch (error) {
            console.error('Error tracking activity:', error);
            throw error;
        }
    }

    // Track page view
    trackPageView(page) {
        return this.trackActivity('page_view', page);
    }

    // Track button click
    trackButtonClick(buttonId, page) {
        return this.trackActivity('button_click', page, { button_id: buttonId });
    }

    // Track form submission
    trackFormSubmission(formId, page) {
        return this.trackActivity('form_submission', page, { form_id: formId });
    }

    // Track search
    trackSearch(searchTerm, page) {
        return this.trackActivity('search', page, { search_term: searchTerm });
    }
}

// Create global instance
window.activityTracker = new ActivityTracker();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ActivityTracker;
} 