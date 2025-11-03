/**
 * Profile caching service
 * Provides simple TTL-based caching for user settings and profile lists
 */
export class ProfileCache {
    constructor() {
        this.userSettingsCache = null;
        this.profileListCache = null;
        this.profileListCacheTime = 0;
        this.CACHE_TTL = 30000; // 30 seconds
    }

    /**
     * Get cached profile list if valid
     */
    getProfileList() {
        const now = Date.now();
        if (this.profileListCache && (now - this.profileListCacheTime) < this.CACHE_TTL) {
            return this.profileListCache;
        }
        return null;
    }

    /**
     * Set profile list cache
     */
    setProfileList(profiles) {
        this.profileListCache = profiles;
        this.profileListCacheTime = Date.now();
    }

    /**
     * Invalidate profile list cache
     */
    invalidateProfileList() {
        this.profileListCache = null;
        this.profileListCacheTime = 0;
    }

    /**
     * Get cached user settings
     */
    getUserSettings() {
        return this.userSettingsCache;
    }

    /**
     * Set user settings cache
     */
    setUserSettings(settings) {
        this.userSettingsCache = settings;
    }

    /**
     * Invalidate user settings cache
     */
    invalidateUserSettings() {
        this.userSettingsCache = null;
    }

    /**
     * Clear all caches
     */
    clearAll() {
        this.invalidateProfileList();
        this.invalidateUserSettings();
    }
}

// Singleton instance
let cacheInstance = null;

export function getProfileCache() {
    if (!cacheInstance) {
        cacheInstance = new ProfileCache();
    }
    return cacheInstance;
}