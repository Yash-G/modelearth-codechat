class ChatAssistant {
    constructor() {
        this.conversations = JSON.parse(localStorage.getItem('chatConversations') || '[]');
        this.currentConversationId = null;
        this.apiEndpoint = 'YOUR_AWS_LAMBDA_ENDPOINT_HERE'; // Replace with your actual endpoint
        this.availableRepositories = []; // Will be populated from API
        
        this.initializeElements();
        this.bindEvents();
        this.loadAvailableRepositories();
        this.loadConversations();
        this.autoResizeTextarea();
    }

    initializeElements() {
        this.chatContainer = document.getElementById('chatContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.newChatBtn = document.getElementById('newChatBtn');
        this.clearHistoryBtn = document.getElementById('clearHistoryBtn');
        this.chatHistory = document.getElementById('chatHistory');
        this.repoSelect = document.getElementById('repoSelect');
        this.sidebar = document.getElementById('sidebar');
        this.sidebarToggle = document.getElementById('sidebarToggle');
    }

    bindEvents() {
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        this.messageInput.addEventListener('input', () => this.handleInputChange());
        this.newChatBtn.addEventListener('click', () => this.startNewChat());
        this.clearHistoryBtn.addEventListener('click', () => this.clearAllConversations());
        this.sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768 && 
                !this.sidebar.contains(e.target) && 
                !this.sidebarToggle.contains(e.target) &&
                this.sidebar.classList.contains('open')) {
                this.sidebar.classList.remove('open');
            }
        });

        // Load repositories when page loads
        window.addEventListener('load', () => this.loadAvailableRepositories());
    }

    toggleSidebar() {
        this.sidebar.classList.toggle('open');
    }

    handleInputChange() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendBtn.disabled = !hasText;
        this.autoResizeTextarea();
    }

    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 200) + 'px';
    }

    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    startNewChat() {
        this.currentConversationId = this.generateId();
        this.clearChatDisplay();
        this.showWelcomeMessage();
        this.updateChatHistory();
        
        // Close sidebar on mobile after starting new chat
        if (window.innerWidth <= 768) {
            this.sidebar.classList.remove('open');
        }
    }

    clearChatDisplay() {
        this.chatContainer.innerHTML = '';
    }

    showWelcomeMessage() {
        this.chatContainer.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                        <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                        <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                    </svg>
                </div>
                <h2>Welcome to Model Earth Chat Assistant</h2>
                <p>Hit me up with your questions about the codebase! I can help you understand code, find specific implementations, or explain how different parts work together.</p>
            </div>
        `;
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        const repository = this.repoSelect.value;
        
        // Clear input
        this.messageInput.value = '';
        this.sendBtn.disabled = true;
        this.autoResizeTextarea();

        // Remove welcome message if present
        const welcomeMessage = this.chatContainer.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        // Add user message
        this.addMessage(message, 'user');

        // Add loading message
        const loadingId = this.addLoadingMessage();

        try {
            const answer = await this.callAPI(message, repository);

            // Remove loading message
            this.removeLoadingMessage(loadingId);

            // Add assistant message
            this.addMessage(answer, 'assistant');
        
        } catch (error) {
            console.error('Error calling API:', error);
            
            // Remove loading message
            this.removeLoadingMessage(loadingId);
            
            // Add error message
            this.addMessage('Sorry, I encountered an error while processing your request. Please try again.', 'assistant');
        }

        // Save conversation
        this.saveCurrentConversation();
        this.updateChatHistory();
    }

    addMessage(content, role) {
        const messageId = this.generateId();
        const messageElement = document.createElement('div');
        messageElement.className = `message ${role}`;
        messageElement.dataset.messageId = messageId;

        const avatar = role === 'user' ? 'U' : 'AI';
        const processedContent = role === 'assistant' ? this.processCodeBlocks(content) : this.escapeHtml(content);

        messageElement.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                ${processedContent}
                ${role === 'assistant' ? `
                    <div class="message-actions">
                        <button class="copy-btn" onclick="chatAssistant.copyMessage('${messageId}')">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M16 4H18C18.5304 4 19.0391 4.21071 19.4142 4.58579C19.7893 4.96086 20 5.46957 20 6V18C20 18.5304 19.7893 19.0391 19.4142 19.4142C19.0391 19.7893 18.5304 20 18 20H6C5.46957 20 4.96086 19.7893 4.58579 19.4142C4.21071 19.0391 4 18.5304 4 18V6C4 5.46957 4.21071 4.96086 4.58579 4.58579C4.96086 4.21071 5.46957 4 6 4H8" stroke="currentColor" stroke-width="2"/>
                                <path d="M15 2H9C8.44772 2 8 2.44772 8 3V5C8 5.55228 8.44772 6 9 6H15C15.5523 6 16 5.55228 16 5V3C16 2.44772 15.5523 2 15 2Z" stroke="currentColor" stroke-width="2"/>
                            </svg>
                            Copy
                        </button>
                    </div>
                ` : ''}
            </div>
        `;

        this.chatContainer.appendChild(messageElement);
        this.scrollToBottom();

        return messageId;
    }

    addLoadingMessage() {
        const loadingId = this.generateId();
        const loadingElement = document.createElement('div');
        loadingElement.className = 'message assistant';
        loadingElement.dataset.messageId = loadingId;

        loadingElement.innerHTML = `
            <div class="message-avatar">AI</div>
            <div class="message-content">
                <div class="loading">
                    <span>Thinking</span>
                    <div class="loading-dots">
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                    </div>
                </div>
            </div>
        `;

        this.chatContainer.appendChild(loadingElement);
        this.scrollToBottom();

        return loadingId;
    }

    removeLoadingMessage(loadingId) {
        const loadingElement = document.querySelector(`[data-message-id="${loadingId}"]`);
        if (loadingElement) {
            loadingElement.remove();
        }
    }

    processCodeBlocks(content) {
        // Simple code block detection and formatting
        const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
        const inlineCodeRegex = /`([^`]+)`/g;

        let processedContent = this.escapeHtml(content);

        // Process code blocks
        processedContent = processedContent.replace(codeBlockRegex, (match, language, code) => {
            const lang = language || 'text';
            const codeId = this.generateId();
            return `
                <div class="code-block">
                    <div class="code-header">
                        <span>${lang}</span>
                        <button class="copy-btn" onclick="chatAssistant.copyCode('${codeId}')">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M16 4H18C18.5304 4 19.0391 4.21071 19.4142 4.58579C19.7893 4.96086 20 5.46957 20 6V18C20 18.5304 19.7893 19.0391 19.4142 19.4142C19.0391 19.7893 18.5304 20 18 20H6C5.46957 20 4.96086 19.7893 4.58579 19.4142C4.21071 19.0391 4 18.5304 4 18V6C4 5.46957 4.21071 4.96086 4.58579 4.58579C4.96086 4.21071 5.46957 4 6 4H8" stroke="currentColor" stroke-width="2"/>
                                <path d="M15 2H9C8.44772 2 8 2.44772 8 3V5C8 5.55228 8.44772 6 9 6H15C15.5523 6 16 5.55228 16 5V3C16 2.44772 15.5523 2 15 2Z" stroke="currentColor" stroke-width="2"/>
                            </svg>
                            Copy
                        </button>
                    </div>
                    <pre id="${codeId}"><code>${code.trim()}</code></pre>
                </div>
            `;
        });

        // Process inline code
        processedContent = processedContent.replace(inlineCodeRegex, '<code>$1</code>');

        // Convert line breaks to <br> tags
        processedContent = processedContent.replace(/\n/g, '<br>');

        return processedContent;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    copyMessage(messageId) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"] .message-content`);
        if (messageElement) {
            const text = messageElement.textContent.replace(/Copy/g, '').trim();
            navigator.clipboard.writeText(text).then(() => {
                this.showCopyFeedback(messageElement.querySelector('.copy-btn'));
            });
        }
    }

    copyCode(codeId) {
        const codeElement = document.getElementById(codeId);
        if (codeElement) {
            const text = codeElement.textContent;
            navigator.clipboard.writeText(text).then(() => {
                const copyBtn = codeElement.parentElement.querySelector('.copy-btn');
                this.showCopyFeedback(copyBtn);
            });
        }
    }

    showCopyFeedback(button) {
        const originalText = button.innerHTML;
        button.innerHTML = `
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            Copied!
        `;
        setTimeout(() => {
            button.innerHTML = originalText;
        }, 2000);
    }

    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    async callAPI(message, repository) {
        // Simulate API call for now - replace with actual endpoint
        if (this.apiEndpoint === 'YOUR_AWS_LAMBDA_ENDPOINT_HERE') {
            // Simulate delay
            await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
            
            // Return mock response
            return `I understand you're asking about: "${message}"${repository ? ` in the ${repository} repository` : ' across all repositories'}.\n\nThis is a placeholder response. Please replace the API endpoint in script.js with your actual AWS Lambda endpoint.\n\nHere's an example of how I might respond with code:\n\n\`\`\`javascript\nfunction exampleFunction() {\n    console.log("This is example code from the repository");\n    return "Hello from Model Earth!";\n}\n\`\`\`\n\nI can help you understand code structure, find specific implementations, and explain how different parts work together.`;
        }

        // Actual API call
        const response = await fetch(this.apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: message,
                repository: repository || null
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.answer || data.response || 'No response received';
    }

    async loadAvailableRepositories() {
        try {
            // Call API to get available repositories from Pinecone namespaces
            if (this.apiEndpoint === 'YOUR_AWS_LAMBDA_ENDPOINT_HERE') {
                // Mock repositories for development
                this.availableRepositories = [
                    'modelearth/localsite',
                    'modelearth/community',
                    'modelearth/io'
                ];
            } else {
                const response = await fetch(`${this.apiEndpoint}/repositories`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    this.availableRepositories = data.repositories || [];
                }
            }
            
            this.populateRepositoryDropdown();
        } catch (error) {
            console.error('Error loading repositories:', error);
            // Fallback to default repositories
            this.availableRepositories = [
                'modelearth/localsite',
                'modelearth/community',
                'modelearth/io'
            ];
            this.populateRepositoryDropdown();
        }
    }

    populateRepositoryDropdown() {
        // Clear existing options except "All repositories"
        const allOption = this.repoSelect.querySelector('option[value=""]');
        this.repoSelect.innerHTML = '';
        this.repoSelect.appendChild(allOption);

        // Add repositories from Pinecone namespaces
        this.availableRepositories.forEach(repo => {
            const option = document.createElement('option');
            option.value = repo;
            option.textContent = repo;
            this.repoSelect.appendChild(option);
        });
    }

    saveCurrentConversation() {
        if (!this.currentConversationId) return;

        const messages = Array.from(this.chatContainer.querySelectorAll('.message')).map(msg => {
            const role = msg.classList.contains('user') ? 'user' : 'assistant';
            const content = msg.querySelector('.message-content').textContent.replace(/Copy/g, '').trim();
            return { role, content };
        });

        if (messages.length === 0) return;

        const conversation = {
            id: this.currentConversationId,
            title: messages[0]?.content.substring(0, 50) + (messages[0]?.content.length > 50 ? '...' : ''),
            messages,
            timestamp: Date.now()
        };

        const existingIndex = this.conversations.findIndex(c => c.id === this.currentConversationId);
        if (existingIndex >= 0) {
            this.conversations[existingIndex] = conversation;
        } else {
            this.conversations.unshift(conversation);
        }

        // Keep only last 50 conversations
        this.conversations = this.conversations.slice(0, 50);

        localStorage.setItem('chatConversations', JSON.stringify(this.conversations));
    }

    loadConversations() {
        this.updateChatHistory();
        if (this.conversations.length === 0) {
            this.startNewChat();
        }
    }

    updateChatHistory() {
        this.chatHistory.innerHTML = '';
        
        this.conversations.forEach(conversation => {
            const chatItem = document.createElement('div');
            chatItem.className = 'chat-item';
            if (conversation.id === this.currentConversationId) {
                chatItem.classList.add('active');
            }
            chatItem.textContent = conversation.title;
            chatItem.addEventListener('click', () => this.loadConversation(conversation.id));
            this.chatHistory.appendChild(chatItem);
        });
    }

    loadConversation(conversationId) {
        const conversation = this.conversations.find(c => c.id === conversationId);
        if (!conversation) return;

        this.currentConversationId = conversationId;
        this.clearChatDisplay();

        conversation.messages.forEach(message => {
            this.addMessage(message.content, message.role);
        });

        this.updateChatHistory();
        
        // Close sidebar on mobile after loading conversation
        if (window.innerWidth <= 768) {
            this.sidebar.classList.remove('open');
        }
    }

    clearAllConversations() {
        if (confirm('Are you sure you want to clear all conversations? This action cannot be undone.')) {
            this.conversations = [];
            localStorage.removeItem('chatConversations');
            this.updateChatHistory();
            this.startNewChat();
        }
    }
}

// Initialize the chat assistant when the page loads
let chatAssistant;
document.addEventListener('DOMContentLoaded', () => {
    chatAssistant = new ChatAssistant();
});

