/**
 * Profile management routes
 * Refactored for clarity and maintainability
 */
import { Router } from 'express';
import path from 'path';
import { ProfileController } from '../controllers/ProfileController.js';
import { avatarUpload } from '../config/multerConfig.js';

const router = Router();

// ============================================================================
// PROFILE CRUD
// ============================================================================

// List all profiles
router.get('/profiles', async (req, res) => {
    try {
        const profiles = await ProfileController.listProfiles();
        res.json(profiles);
    } catch (error) {
        console.error('Error listing profiles:', error);
        res.status(500).json({
            error: 'Internal Server Error',
            message: 'Could not list profiles'
        });
    }
});

// Get specific profile
router.get('/profiles/:profileName', async (req, res) => {
    try {
        const encryptionKey = req.session?.encryptionKey || null;
        const profile = await ProfileController.getProfile(req.params.profileName, encryptionKey);
        res.json(profile);
    } catch (error) {
        console.error('Error loading profile:', error);
        res.status(500).json({
            error: 'Internal Server Error',
            message: 'Could not load profile'
        });
    }
});

// Save profile
router.post('/profiles/:profileName', async (req, res) => {
    try {
        const encryptionKey = req.session?.encryptionKey || null;
        await ProfileController.saveProfile(req.params.profileName, req.body, encryptionKey);
        res.json({ success: true });
    } catch (error) {
        console.error('Error saving profile:', error);
        res.status(500).json({
            error: 'Internal Server Error',
            message: 'Could not save profile'
        });
    }
});

// Delete profile
router.delete('/profiles/:profileName', async (req, res) => {
    try {
        await ProfileController.deleteProfile(req.params.profileName);
        res.json({ success: true });
    } catch (error) {
        console.error('Error deleting profile:', error);
        res.status(500).json({
            error: 'Internal Server Error',
            message: 'Could not delete profile'
        });
    }
});

// ============================================================================
// ACTIVE PROFILE
// ============================================================================

// Get active profile
router.get('/profiles/active', async (req, res) => {
    try {
        const encryptionKey = req.session?.encryptionKey || null;
        const active = await ProfileController.getActiveProfile(encryptionKey);
        res.json({ active });
    } catch (error) {
        console.error('Error getting active profile:', error);
        res.status(500).json({
            error: 'Internal Server Error',
            message: 'Could not get active profile'
        });
    }
});

// Set active profile
router.post('/profiles/active', async (req, res) => {
    try {
        const { active, name } = req.body;
        const profileName = active || name;

        if (!profileName) {
            return res.status(400).json({
                error: 'Validation Error',
                message: 'Profile name is required'
            });
        }

        const encryptionKey = req.session?.encryptionKey || null;
        const sanitizedName = await ProfileController.setActiveProfile(profileName, encryptionKey);
        res.json({ success: true, active: sanitizedName });
    } catch (error) {
        console.error('Error setting active profile:', error);
        res.status(500).json({
            error: 'Internal Server Error',
            message: error.message || 'Could not set active profile'
        });
    }
});

// ============================================================================
// AVATARS
// ============================================================================

// Get avatar
router.get('/profiles/:profileName/avatar', async (req, res) => {
    try {
        const avatar = await ProfileController.getAvatar(req.params.profileName);
        res.json({ avatar });
    } catch (error) {
        console.error('[Avatar API] Error loading avatar:', error);
        res.status(500).json({ avatar: null, error: error.message });
    }
});

// Upload avatar
router.post('/profiles/:profileName/avatar', avatarUpload.single('avatar'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({
                error: 'Validation Error',
                message: 'Avatar file is required'
            });
        }

        const avatarPath = `/uploads/avatars/${req.file.filename}`;
        res.json({
            success: true,
            message: 'Avatar saved successfully',
            avatar: avatarPath
        });
    } catch (error) {
        console.error('Error saving avatar:', error);
        res.status(500).json({
            error: 'Internal Server Error',
            message: error.message || 'Could not save avatar'
        });
    }
});

// ============================================================================
// USER SETTINGS
// ============================================================================

// Get user settings
router.get('/user-settings', async (req, res) => {
    try {
        const encryptionKey = req.session?.encryptionKey || null;
        const settings = await ProfileController.getUserSettings(encryptionKey);
        res.json(settings);
    } catch (error) {
        console.error('Error loading user settings:', error);
        res.status(500).json({
            error: 'Internal Server Error',
            message: 'Could not load user settings'
        });
    }
});

// Save user settings
router.post('/user-settings', async (req, res) => {
    try {
        const encryptionKey = req.session?.encryptionKey || null;
        await ProfileController.saveUserSettings(req.body, encryptionKey);
        res.json({ success: true });
    } catch (error) {
        console.error('Error saving user settings:', error);
        res.status(500).json({
            error: 'Internal Server Error',
            message: 'Could not save user settings'
        });
    }
});

// ============================================================================
// DATA IMPORT/EXPORT
// ============================================================================

// Export all data (user settings + all character profiles)
router.get('/export-data', async (req, res) => {
    try {
        const encryptionKey = req.session?.encryptionKey || null;

        if (!encryptionKey) {
            return res.status(401).json({
                error: 'Authentication Required',
                message: 'You must be logged in to export data'
            });
        }

        // Get raw user settings (full data structure, not transformed)
        const storage = (await import('../services/ProfileStorage.js')).getProfileStorage();

        let userSettings;
        try {
            userSettings = await storage.getUserSettings(encryptionKey);
        } catch (err) {
            console.error('Failed to load user settings for export:', err.message);
            return res.status(500).json({
                error: 'Export Failed',
                message: 'Failed to decrypt user settings - please check your login session'
            });
        }

        // Get list of all profiles
        const profileNames = await ProfileController.listProfiles();

        // Load all character profiles (full data structures)
        const profiles = {};
        const failedProfiles = [];

        for (const profileName of profileNames) {
            try {
                const profileData = await storage.getProfile(profileName, encryptionKey);
                profiles[profileName] = profileData;
            } catch (err) {
                console.error('Failed to load profile for export:', err.message);
                failedProfiles.push(profileName);
            }
        }

        // Validate we have data to export
        if (!userSettings) {
            return res.status(500).json({
                error: 'Export Failed',
                message: 'No user settings found to export'
            });
        }

        // Create export package
        const exportData = {
            version: '1.0',
            exportDate: new Date().toISOString(),
            userSettings,
            profiles
        };

        // Set headers for download
        res.setHeader('Content-Type', 'application/json');
        res.setHeader('Content-Disposition', `attachment; filename="echo-backup-${new Date().toISOString().split('T')[0]}.json"`);

        res.json(exportData);
    } catch (error) {
        console.error('Error exporting data:', error.message);
        res.status(500).json({
            error: 'Internal Server Error',
            message: 'Failed to export data: ' + error.message
        });
    }
});

// Import functionality removed for security
// Users should manually restore encrypted backup files to the data/profiles directory

// ============================================================================
// CONSENT
// ============================================================================

// Get consent
router.get('/consent', async (req, res) => {
    try {
        const encryptionKey = req.session?.encryptionKey || null;
        const consent = await ProfileController.getConsent(encryptionKey);
        res.json(consent);
    } catch (error) {
        console.error('Error loading consent:', error);
        res.status(500).json({
            error: 'Internal Server Error',
            message: 'Could not load consent data'
        });
    }
});

// Save consent
router.post('/consent', async (req, res) => {
    try {
        const encryptionKey = req.session?.encryptionKey || null;
        await ProfileController.saveConsent(req.body, encryptionKey);
        res.json({ success: true });
    } catch (error) {
        console.error('Error saving consent:', error);
        res.status(500).json({
            error: 'Internal Server Error',
            message: 'Could not save consent data'
        });
    }
});

// ============================================================================
// LEGACY ROUTES (backward compatibility)
// ============================================================================

router.get('/active', async (req, res) => {
    try {
        const encryptionKey = req.session?.encryptionKey || null;
        const active = await ProfileController.getActiveProfile(encryptionKey);
        res.json({ active });
    } catch (error) {
        console.error('Error getting active profile:', error);
        res.status(500).json({
            error: 'Internal Server Error',
            message: 'Could not get active profile'
        });
    }
});

router.post('/active', async (req, res) => {
    try {
        const { active, name } = req.body;
        const profileName = active || name;

        if (!profileName) {
            return res.status(400).json({
                error: 'Validation Error',
                message: 'Profile name is required'
            });
        }

        const encryptionKey = req.session?.encryptionKey || null;
        const sanitizedName = await ProfileController.setActiveProfile(profileName, encryptionKey);
        res.json({ success: true, active: sanitizedName });
    } catch (error) {
        console.error('Error setting active profile:', error);
        res.status(500).json({
            error: 'Internal Server Error',
            message: error.message || 'Could not set active profile'
        });
    }
});

export default router;
