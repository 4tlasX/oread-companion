/**
 * Dependency management - Singleton pattern for chatbot instance
 */
import { HybridChatbot } from '../core/chatbotHybrid.js';
let chatbotInstance = null;
/**
 * Get or create the singleton chatbot instance
 */
export async function getChatbot() {
    if (!chatbotInstance) {
        chatbotInstance = new HybridChatbot();
        await chatbotInstance.initialize();
    }
    return chatbotInstance;
}
/**
 * Reset chatbot instance (useful for testing or reloading)
 */
export function resetChatbot() {
    chatbotInstance = null;
}
//# sourceMappingURL=dependencies.js.map