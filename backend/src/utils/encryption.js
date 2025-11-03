/**
 * Encryption utility for sensitive user data
 * Uses AES-256-GCM encryption with password-derived keys
 */
import crypto from 'crypto';

const ALGORITHM = 'aes-256-gcm';
const KEY_LENGTH = 32; // 256 bits
const IV_LENGTH = 16; // 128 bits
const SALT_LENGTH = 32;
const TAG_LENGTH = 16;
const ITERATIONS = 100000; // PBKDF2 iterations

export class EncryptionService {
    /**
     * Derive encryption key from password using PBKDF2
     */
    static deriveKey(password, salt) {
        return crypto.pbkdf2Sync(
            password,
            salt,
            ITERATIONS,
            KEY_LENGTH,
            'sha256'
        );
    }

    /**
     * Encrypt data with password
     * @param {string} plaintext - Data to encrypt
     * @param {string} password - User's password
     * @returns {string} Encrypted data in format: salt:iv:authTag:ciphertext (base64)
     */
    static encrypt(plaintext, password) {
        try {
            // Generate random salt and IV
            const salt = crypto.randomBytes(SALT_LENGTH);
            const iv = crypto.randomBytes(IV_LENGTH);

            // Derive key from password
            const key = this.deriveKey(password, salt);

            // Create cipher
            const cipher = crypto.createCipheriv(ALGORITHM, key, iv);

            // Encrypt data
            let ciphertext = cipher.update(plaintext, 'utf8', 'base64');
            ciphertext += cipher.final('base64');

            // Get auth tag
            const authTag = cipher.getAuthTag();

            // Combine: salt:iv:authTag:ciphertext
            const encrypted = [
                salt.toString('base64'),
                iv.toString('base64'),
                authTag.toString('base64'),
                ciphertext
            ].join(':');

            return encrypted;
        } catch (error) {
            console.error('Encryption error:', error);
            throw new Error('Failed to encrypt data');
        }
    }

    /**
     * Decrypt data with password
     * @param {string} encrypted - Encrypted data in format: salt:iv:authTag:ciphertext
     * @param {string} password - User's password
     * @returns {string} Decrypted plaintext
     */
    static decrypt(encrypted, password) {
        try {
            // Split encrypted data
            const parts = encrypted.split(':');
            if (parts.length !== 4) {
                throw new Error('Invalid encrypted data format');
            }

            const [saltB64, ivB64, authTagB64, ciphertext] = parts;

            // Convert from base64
            const salt = Buffer.from(saltB64, 'base64');
            const iv = Buffer.from(ivB64, 'base64');
            const authTag = Buffer.from(authTagB64, 'base64');

            // Derive key from password
            const key = this.deriveKey(password, salt);

            // Create decipher
            const decipher = crypto.createDecipheriv(ALGORITHM, key, iv);
            decipher.setAuthTag(authTag);

            // Decrypt data
            let plaintext = decipher.update(ciphertext, 'base64', 'utf8');
            plaintext += decipher.final('utf8');

            return plaintext;
        } catch (error) {
            console.error('Decryption error:', error);
            throw new Error('Failed to decrypt data - incorrect password or corrupted data');
        }
    }

    /**
     * Encrypt a JSON object
     * @param {Object} obj - Object to encrypt
     * @param {string} password - User's password
     * @returns {string} Encrypted JSON string
     */
    static encryptObject(obj, password) {
        const json = JSON.stringify(obj);
        return this.encrypt(json, password);
    }

    /**
     * Decrypt to JSON object
     * @param {string} encrypted - Encrypted data
     * @param {string} password - User's password
     * @returns {Object} Decrypted object
     */
    static decryptObject(encrypted, password) {
        const json = this.decrypt(encrypted, password);
        return JSON.parse(json);
    }

    /**
     * Encrypt specific fields in an object
     * @param {Object} obj - Object with fields to encrypt
     * @param {Array<string>} fields - Field names to encrypt
     * @param {string} password - User's password
     * @returns {Object} Object with encrypted fields
     */
    static encryptFields(obj, fields, password) {
        const result = { ...obj };

        for (const field of fields) {
            if (obj[field] !== undefined && obj[field] !== null) {
                const value = typeof obj[field] === 'string'
                    ? obj[field]
                    : JSON.stringify(obj[field]);
                result[field] = this.encrypt(value, password);
            }
        }

        return result;
    }

    /**
     * Decrypt specific fields in an object
     * @param {Object} obj - Object with encrypted fields
     * @param {Array<string>} fields - Field names to decrypt
     * @param {string} password - User's password
     * @returns {Object} Object with decrypted fields
     */
    static decryptFields(obj, fields, password) {
        const result = { ...obj };

        for (const field of fields) {
            if (obj[field] !== undefined && obj[field] !== null && typeof obj[field] === 'string') {
                try {
                    const decrypted = this.decrypt(obj[field], password);
                    // Try to parse as JSON, otherwise keep as string
                    try {
                        result[field] = JSON.parse(decrypted);
                    } catch {
                        result[field] = decrypted;
                    }
                } catch (error) {
                    console.error(`Failed to decrypt field ${field}:`, error.message);
                    // Keep encrypted value if decryption fails
                }
            }
        }

        return result;
    }

    /**
     * Check if data is encrypted (heuristic check)
     * @param {string} data - Data to check
     * @returns {boolean} True if data appears to be encrypted
     */
    static isEncrypted(data) {
        if (typeof data !== 'string') return false;

        // Check for our format: base64:base64:base64:base64
        const parts = data.split(':');
        if (parts.length !== 4) return false;

        // Check if all parts are valid base64
        const base64Regex = /^[A-Za-z0-9+/]+=*$/;
        return parts.every(part => base64Regex.test(part));
    }
}
