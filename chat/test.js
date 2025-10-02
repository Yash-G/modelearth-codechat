/**
 * Simple test script to verify ChatAssistant functionality
 * Run this in the browser console after loading the page
 */

console.log('Running ChatAssistant tests...');

// Test 1: Check if ChatAssistant is initialized
if (window.chatAssistant) {
    console.log('✅ ChatAssistant instance found');
} else {
    console.error('❌ ChatAssistant instance not found');
}

// Test 2: Check if API endpoint is configured
if (window.chatAssistant && window.chatAssistant.apiEndpoint) {
    console.log('✅ API endpoint configured:', window.chatAssistant.apiEndpoint);
} else {
    console.error('❌ API endpoint not configured');
}

// Test 3: Check if repositories are loaded
if (window.chatAssistant && window.chatAssistant.availableRepositories.length > 0) {
    console.log('✅ Repositories loaded:', window.chatAssistant.availableRepositories.length);
} else {
    console.warn('⚠️ No repositories loaded');
}

// Test 4: Check if required methods exist
const requiredMethods = [
    'getCurrentConversation',
    'saveConversations', 
    'showTypingIndicator',
    'removeTypingIndicator',
    'sanitizeHtml'
];

requiredMethods.forEach(methodName => {
    if (window.chatAssistant && typeof window.chatAssistant[methodName] === 'function') {
        console.log(`✅ Method ${methodName} exists`);
    } else {
        console.error(`❌ Method ${methodName} missing or not a function`);
    }
});

console.log('Tests completed!');

// Helper function to test sending a message (use carefully in testing)
window.testSendMessage = function(message, repository = 'sagar8080/codechat') {
    if (!window.chatAssistant) {
        console.error('ChatAssistant not available');
        return;
    }
    
    if (window.chatAssistant.repoSelect) {
        window.chatAssistant.repoSelect.value = repository;
    }
    
    if (window.chatAssistant.messageInput) {
        window.chatAssistant.messageInput.value = message;
        window.chatAssistant.handleInputChange();
    }
    
    console.log('Test message prepared. Call chatAssistant.sendMessage() to send.');
};