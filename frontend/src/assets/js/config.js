/**
 * Frontend Configuration
 *
 * IMPORTANT: This file contains your API key.
 * Keep it secure and do not commit to git if deploying publicly.
 */

const CONFIG = {
    // API Configuration - API key is now loaded from localStorage after authentication
    get API_KEY() {
        return localStorage.getItem('apiKey') || '';
    },

    // Base URL - always use HTTPS for secure connections
    get API_BASE() {
        return `https://${window.location.hostname}:${window.location.port || '9000'}`;
    },

    // API Endpoints
    ENDPOINTS: {
        CHAT: '/chat',
        ANALYZE: '/api/analyze',
        PROFILES: '/api/profiles',
        ACTIVE_PROFILE: '/api/active',
        USER_SETTINGS: '/api/user-settings',
        HEALTH: '/health'
    },

    // Request headers with API key
    getHeaders() {
        return {
            'Content-Type': 'application/json',
            'X-API-Key': this.API_KEY
        };
    },

    // Fetch wrapper with API key
    async fetch(endpoint, options = {}) {
        const defaultOptions = {
            headers: this.getHeaders(),
            credentials: 'include', // Send session cookies
            ...options
        };

        // Merge headers if provided
        if (options.headers) {
            defaultOptions.headers = {
                ...this.getHeaders(),
                ...options.headers
            };
        }

        const url = `${this.API_BASE}${endpoint}`;
        return fetch(url, defaultOptions);
    }
};

// Make config available globally
window.CONFIG = CONFIG;