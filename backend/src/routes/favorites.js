/**
 * Favorites management routes
 */
import { Router } from 'express';
import { ProfileController } from '../controllers/ProfileController.js';

const router = Router();

// ============================================================================
// FAVORITES CRUD
// ============================================================================

// Get all favorites for a character
router.get('/favorites/:characterName', async (req, res) => {
    try {
        const encryptionKey = req.session?.encryptionKey || null;
        const favorites = await ProfileController.getFavorites(req.params.characterName, encryptionKey);
        res.json({ favorites });
    } catch (error) {
        console.error('Error getting favorites:', error);
        res.status(500).json({
            error: 'Internal Server Error',
            message: 'Could not get favorites'
        });
    }
});

// Add a favorite to a character
router.post('/favorites/:characterName', async (req, res) => {
    try {
        const { text, senderName, emotion, sentiment } = req.body;

        if (!text) {
            return res.status(400).json({
                error: 'Validation Error',
                message: 'Favorite text is required'
            });
        }

        const encryptionKey = req.session?.encryptionKey || null;
        const favorite = await ProfileController.addFavorite(req.params.characterName, {
            text,
            senderName,
            emotion,
            sentiment
        }, encryptionKey);

        res.json({
            success: true,
            favorite
        });
    } catch (error) {
        console.error('Error adding favorite:', error);
        res.status(500).json({
            error: 'Internal Server Error',
            message: error.message || 'Could not add favorite'
        });
    }
});

// Remove a favorite from a character
router.delete('/favorites/:characterName/:favoriteId', async (req, res) => {
    try {
        const encryptionKey = req.session?.encryptionKey || null;
        await ProfileController.removeFavorite(
            req.params.characterName,
            req.params.favoriteId,
            encryptionKey
        );

        res.json({ success: true });
    } catch (error) {
        console.error('Error removing favorite:', error);
        res.status(500).json({
            error: 'Internal Server Error',
            message: 'Could not remove favorite'
        });
    }
});

export default router;
