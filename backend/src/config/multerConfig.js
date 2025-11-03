/**
 * Multer configuration for file uploads
 */
import multer from 'multer';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { InputSanitizer } from '../utils/sanitizer.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Avatar upload storage configuration
const avatarStorage = multer.diskStorage({
    destination: function (req, file, cb) {
        const uploadsDir = path.join(__dirname, '../../../data/uploads/avatars');
        cb(null, uploadsDir);
    },
    filename: function (req, file, cb) {
        const profileName = InputSanitizer.sanitizeProfileName(req.params.profileName);
        const ext = path.extname(file.originalname);
        cb(null, `${profileName}${ext}`);
    }
});

export const avatarUpload = multer({
    storage: avatarStorage,
    limits: {
        fileSize: 5 * 1024 * 1024 // 5MB limit
    },
    fileFilter: function (req, file, cb) {
        const allowedTypes = /jpeg|jpg|png|gif|webp/;
        const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
        const mimetype = allowedTypes.test(file.mimetype);

        if (mimetype && extname) {
            return cb(null, true);
        } else {
            cb(new Error('Only image files are allowed'));
        }
    }
});
