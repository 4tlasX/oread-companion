/**
 * Character profile loader
 */
import { promises as fs } from 'fs';
import path from 'path';
import { envConfig } from './env_config.js';
import { ProfileController } from '../controllers/ProfileController.js';
const logger = console;
/**
 * Load user settings including name and gender
 * Supports both JSON (user-profile.json) and legacy TXT (user-settings.txt) formats
 */
export async function loadUserSettings(encryptionKey = null) {
    const defaults = {
        userName: "User",
        userGender: "non-binary",
        timezone: "UTC",
        userBackstory: "",
        userPreferences: {
            music: [],
            books: [],
            movies: [],
            hobbies: [],
            other: ""
        },
        majorLifeEvents: [],
        enableMemory: envConfig.features.enableMemory,  // From env by default
        enableWebSearch: envConfig.features.enableWebSearch  // From env by default
    };
    try {
        // Try using ProfileController first (supports encryption)
        try {
            const data = await ProfileController.getUserSettings(encryptionKey);
            return data;
        } catch (error) {
            // ProfileController failed, try direct filesystem access (legacy)
            logger.warn('Failed to load user settings via ProfileController, trying legacy method');
        }

        // Fallback to legacy direct filesystem access
        const profilesDir = envConfig.paths.profilesDir;
        const jsonPath = path.join(profilesDir, 'user-profile.json');
        const txtPath = path.join(profilesDir, 'user-settings.txt');

        // Try JSON format first
        try {
            await fs.access(jsonPath);
            const content = await fs.readFile(jsonPath, 'utf-8');
            const data = JSON.parse(content);

            if (data.version === '2.0' && data.type === 'user') {
                return {
                    userName: data.user.name || defaults.userName,
                    userGender: data.user.gender || defaults.userGender,
                    timezone: data.user.timezone || defaults.timezone,
                    userBackstory: data.user.backstory || defaults.userBackstory,
                    userPreferences: data.user.preferences || defaults.userPreferences,
                    majorLifeEvents: data.user.majorLifeEvents || defaults.majorLifeEvents,
                    sharedRoleplayEvents: data.sharedMemory?.roleplayEvents || defaults.sharedRoleplayEvents,
                    // User preferences override env config
                    enableMemory: data.settings?.enableMemory ?? defaults.enableMemory,
                    enableWebSearch: data.settings?.enableWebSearch ?? defaults.enableWebSearch
                };
            }
        } catch (error) {
            // JSON file doesn't exist or is invalid, try TXT format
        }

        // Fallback to TXT format (legacy)
        try {
            await fs.access(txtPath);
            const content = await fs.readFile(txtPath, 'utf-8');
            const settings = { ...defaults };
            for (const line of content.trim().split('\n')) {
                if (line.includes('=')) {
                    const [key, value] = line.split('=', 2);
                    const trimmedKey = key.trim();
                    const trimmedValue = value.trim();
                    if (trimmedKey in settings) {
                        settings[trimmedKey] = trimmedValue;
                    }
                }
            }
            return settings;
        } catch (error) {
            // No user settings file exists, return defaults
            return defaults;
        }
    }
    catch (error) {
        logger.error(`Error loading user settings: ${error}`);
        return defaults;
    }
}
/**
 * Load the configured user name
 */
export async function loadUserName(encryptionKey = null) {
    const settings = await loadUserSettings(encryptionKey);
    return settings.userName;
}
/**
 * Load a specific character profile by name, or load the active character if no name specified
 */
export async function loadActiveCharacter(specificCharacterName = null, encryptionKey = null) {
    const profilesDir = envConfig.paths.profilesDir;
    // Load user name
    const userName = await loadUserName(encryptionKey);
    // Check if profiles directory exists
    try {
        await fs.access(profilesDir);
    }
    catch {
        logger.error(`Profiles directory does not exist`);
        return loadDefaultCharacter(userName);
    }

    let characterName = specificCharacterName;

    // If no specific character name provided, get active character name
    if (!characterName) {
        // Try ProfileController first (supports encryption)
        try {
            characterName = await ProfileController.getActiveProfile(encryptionKey);
        } catch (err) {
            // ProfileController failed, try legacy filesystem access
            logger.warn('Failed to get active character via ProfileController, trying legacy method');
        }

        // Fallback to legacy filesystem access if ProfileController failed
        if (!characterName) {
            const userProfileJson = path.join(profilesDir, 'user-profile.json');
            const activeCharacterTxt = path.join(profilesDir, 'active-character.txt');

            try {
                // Try JSON format first
                await fs.access(userProfileJson);
                const content = await fs.readFile(userProfileJson, 'utf-8');
                const data = JSON.parse(content);

                if (data.version === '2.0' && data.settings?.defaultActiveCharacter) {
                    characterName = data.settings.defaultActiveCharacter;
                }
            } catch (err) {
                // JSON doesn't exist or doesn't have active character, try TXT
            }

            // Fallback to TXT format if JSON didn't work
            if (!characterName) {
                try {
                    await fs.access(activeCharacterTxt);
                    characterName = (await fs.readFile(activeCharacterTxt, 'utf-8')).trim();
                } catch (err) {
                    logger.info(`No active character configured - will use default until user logs in and selects a character`);
                    return loadDefaultCharacter(userName);
                }
            }
        }
    }
    // Load character profile using ProfileController (supports encryption)
    let profile = null;
    let isJsonFormat = false;

    try {
        const data = await ProfileController.getProfile(characterName, encryptionKey);

        if (data.version === '2.0' && data.type === 'character') {
            profile = data.character;
            isJsonFormat = true;
        }
    } catch (error) {
        logger.error(`[CharacterLoader] Failed to load profile via ProfileController`);

        // Fallback to legacy filesystem access
        const jsonPath = path.join(profilesDir, `${characterName}.json`);
        const txtPath = path.join(profilesDir, `${characterName}.txt`);

        // Try JSON format first
        try {
            await fs.access(jsonPath);
            const content = await fs.readFile(jsonPath, 'utf-8');
            const data = JSON.parse(content);

            if (data.version === '2.0' && data.type === 'character') {
                profile = data.character;
                isJsonFormat = true;
            }
        } catch (error) {
            // JSON doesn't exist or is invalid, try TXT
        }

        // Fallback to TXT format
        if (!profile) {
            try {
                await fs.access(txtPath);
                const content = await fs.readFile(txtPath, 'utf-8');
                profile = parseProfile(content);
            } catch (error) {
                logger.warn(`Character profile not found`);
                return loadDefaultCharacter(userName);
            }
        }
    }

    try {
        // Get character name from profile
        const charName = profile.name || characterName;
        // Get avoid words list
        const avoidWordsStr = profile.avoidWords || '';
        const avoidWords = avoidWordsStr
            .split(',')
            .map((word) => word.trim().toLowerCase())
            .filter((word) => word.length > 0);
        // Get companion type
        const companionType = (profile.companionType || 'friend');

        // Extract additional fields for inference
        const gender = profile.gender || 'unknown';
        const role = profile.role || '';
        const backstory = profile.backstory || '';
        const lorebook = profile.lorebook || {};
        const tagSelections = profile.tagSelections || {};

        // Format as character string
        const characterString = formatCharacterProfile(profile);

        return {
            characterString,
            characterName: charName,
            avoidWords,
            userName,
            companionType,
            gender,
            role,
            backstory,
            lorebook,
            tagSelections
        };
    }
    catch (error) {
        logger.error(`Error loading character profile`);
        return loadDefaultCharacter(userName);
    }
}
/**
 * Parse profile content into a dictionary
 */
function parseProfile(content) {
    const profile = {};
    const lines = content.split('\n');
    for (const line of lines) {
        if (line.includes('=')) {
            const firstEquals = line.indexOf('=');
            const key = line.slice(0, firstEquals).trim();
            const value = line.slice(firstEquals + 1).replace(/\\n/g, '\n');
            if (key === 'notifications') {
                profile[key] = value === 'true';
            }
            else {
                profile[key] = value;
            }
        }
    }
    return profile;
}
/**
 * Format profile dictionary into character string
 */
function formatCharacterProfile(profile) {
    const companionType = profile.companionType === 'friend' ? 'Platonic' : 'Romantic';

    // Build the profile string, including personality kernel if present
    let profileString = `Character Profile: ${profile.name || 'Unknown'}

Gender: ${profile.gender || 'Unknown'}
Age: ${profile.age || 'Unknown'}
Role: ${profile.role || ''}
Companion Type: ${companionType}
`;

    // Add personality kernel at the top if it exists (high priority)
    if (profile.personalityKernel && profile.personalityKernel.trim()) {
        profileString += `
**CORE PERSONALITY (CRITICAL - OVERRIDE ALL DEFAULTS):**
${profile.personalityKernel}
`;
    }

    profileString += `
Appearance:
${profile.appearance || ''}

Personality Traits:
${profile.traits || ''}

Personal Interests/Domains of Expertise:
${profile.interests || ''}

Backstory:
${profile.backstory || ''}

Communication Style:
${profile.communicationStyle || ''}

Affection Style:
${profile.affectionStyle || ''}

Communication Boundaries:
${profile.boundaries || ''}

Words/Phrases to Avoid:
${profile.avoidWords || ''}
`;

    return profileString;
}
/**
 * Load default character profile
 */
function loadDefaultCharacter(userName = "User") {
    const defaultProfile = `Character Profile: Default Character

This is a default character profile. Please select a character in the profile builder.
`;
    return {
        characterString: defaultProfile,
        characterName: "Default Character",
        avoidWords: [],
        userName,
        companionType: 'friend'
    };
}
/**
 * Character loader class for hybrid chatbot
 */
export class CharacterLoader {
    activeCharacter = null;
    encryptionKey = null;

    /**
     * Set encryption key for loading encrypted profiles
     */
    setEncryptionKey(key) {
        this.encryptionKey = key;
    }

    /**
     * Load the active character profile (optionally a specific character)
     */
    loadActiveCharacter(characterName = null) {
        // This is synchronous for compatibility, but loads async in background
        loadActiveCharacter(characterName, this.encryptionKey).then(profile => {
            this.activeCharacter = profile;
        }).catch(error => {
            logger.error(`Failed to load character: ${error}`);
        });
    }
    /**
     * Get the active character (synchronous)
     */
    getActiveCharacter() {
        return this.activeCharacter;
    }
    /**
     * Get the active character name
     */
    getActiveCharacterName() {
        return this.activeCharacter?.characterName || 'Unknown';
    }
    /**
     * Load character asynchronously and return it (optionally a specific character)
     */
    async loadCharacterAsync(characterName = null) {
        this.activeCharacter = await loadActiveCharacter(characterName, this.encryptionKey);
        return this.activeCharacter;
    }
}
//# sourceMappingURL=characterLoader.js.map