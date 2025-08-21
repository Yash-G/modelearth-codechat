# Code Chat Assistant - Development Prompt

## Project Overview
You are building a ChatGPT-style frontend interface for a RAG (Retrieval-Augmented Generation) powered codebase assistant. This interface connects to an AWS Lambda backend that queries a Pinecone vector database containing chunked code from various repositories.

## Technical Architecture

### Backend (AWS Lambda + Pinecone)
- **Vector Database**: Pinecone stores code chunks with metadata
- **Namespaces**: Each repository is stored in its own Pinecone namespace
- **Embeddings**: OpenAI's text-embedding-3-small for both indexing and queries
- **LLM**: Gemini (gemini-1.5-flash) for generating responses
- **Chunking**: Tree-sitter for intelligent code parsing

### Frontend (Static GitHub Pages)
- **Hosting**: GitHub Pages (static files only)
- **Framework**: Vanilla JavaScript (no build process required)
- **Storage**: localStorage for conversation history
- **Styling**: ChatGPT-identical dark theme interface

## Current Implementation

### File Structure
```
├── index.html          # Main HTML structure
├── styles.css          # Complete ChatGPT-style styling
├── script.js           # All functionality and API integration
├── README.md           # Documentation and setup instructions
└── DEVELOPMENT_PROMPT.md # This file
```

### Key Features Implemented
1. **ChatGPT-identical UI** - Dark theme, same layout and interactions
2. **Repository filtering** - Dropdown populated from Pinecone namespaces
3. **Conversation history** - Locally stored, up to 50 conversations
4. **Code snippet handling** - Automatic formatting and copy buttons
5. **Responsive design** - Mobile-optimized with collapsible sidebar
6. **Loading states** - Animated loading indicators during API calls

### API Integration Points

#### 1. Main Chat Endpoint
```javascript
// POST to main endpoint
{
    "question": "user's question",
    "repository": "namespace-name" // null for all repositories
}

// Expected response
{
    "answer": "AI response with markdown/code support"
}
```

#### 2. Repository List Endpoint
```javascript
// GET to /repositories endpoint
// Expected response
{
    "repositories": ["repo1", "repo2", "repo3"] // Array of Pinecone namespace names
}
```

## Development Guidelines

### Code Organization
- **Single Page Application**: All functionality in one HTML file with external CSS/JS
- **Modular JavaScript**: ChatAssistant class with clear method separation
- **No Build Process**: Must work directly in browser without compilation
- **GitHub Pages Compatible**: Only static files, no server-side processing

### Styling Standards
- **ChatGPT Consistency**: Match ChatGPT's exact color scheme and layout
- **CSS Custom Properties**: Use for easy theme customization
- **Mobile First**: Responsive design with mobile breakpoints
- **Accessibility**: Proper ARIA labels and keyboard navigation

### JavaScript Patterns
- **ES6+ Syntax**: Modern JavaScript features
- **Error Handling**: Comprehensive try-catch blocks
- **Local Storage**: Conversation persistence across sessions
- **Event Delegation**: Efficient event handling for dynamic content

## Configuration Requirements

### API Endpoint Setup
```javascript
// In script.js, line ~8
this.apiEndpoint = 'YOUR_AWS_LAMBDA_ENDPOINT_HERE';
```

### Repository Configuration
Repositories are automatically loaded from the `/repositories` endpoint, which should return all available Pinecone namespaces.

## Enhancement Opportunities

### Immediate Improvements
1. **Syntax Highlighting**: Add Prism.js or highlight.js for code blocks
2. **Export Functionality**: Allow users to export conversation history
3. **Search History**: Search through past conversations
4. **Keyboard Shortcuts**: Add hotkeys for common actions
5. **Theme Toggle**: Light/dark mode switcher

### Advanced Features
1. **File Context**: Show which files/functions the AI is referencing
2. **Code Navigation**: Click to jump to specific files in GitHub
3. **Collaborative Features**: Share conversations via URL
4. **Analytics**: Track usage patterns and popular queries
5. **Offline Support**: Service worker for basic offline functionality

### Performance Optimizations
1. **Lazy Loading**: Load conversation history on demand
2. **Message Virtualization**: Handle very long conversations efficiently
3. **Debounced Input**: Reduce API calls during typing
4. **Caching**: Cache repository list and recent responses

## Testing Strategy

### Manual Testing Checklist
- [ ] Chat functionality works with mock responses
- [ ] Repository dropdown populates correctly
- [ ] Conversation history saves and loads
- [ ] Copy buttons work for code and messages
- [ ] Mobile responsive design functions properly
- [ ] Error handling displays appropriate messages

### Browser Compatibility
- Chrome/Edge 88+
- Firefox 85+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Deployment Process

### GitHub Pages Setup
1. Push all files to main branch
2. Enable GitHub Pages in repository settings
3. Select "Deploy from a branch" → main → / (root)
4. Site available at `https://username.github.io/repository-name`

### Environment Configuration
- Update API endpoint in `script.js`
- Verify CORS settings on Lambda function
- Test with actual Pinecone data

## Common Issues & Solutions

### CORS Problems
```javascript
// Ensure Lambda returns proper CORS headers
{
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type"
}
```

### Repository Loading Issues
- Check `/repositories` endpoint returns proper JSON array
- Verify Pinecone namespace names match expected format
- Handle empty repository list gracefully

### Mobile Display Problems
- Test sidebar toggle functionality
- Verify touch interactions work properly
- Check text input behavior on mobile keyboards

## Code Quality Standards

### JavaScript
- Use meaningful variable names
- Add JSDoc comments for complex functions
- Handle all promise rejections
- Validate user input before API calls

### CSS
- Follow BEM naming convention where applicable
- Use consistent spacing (8px grid system)
- Optimize for performance (avoid expensive selectors)
- Maintain color contrast ratios for accessibility

### HTML
- Semantic markup structure
- Proper ARIA attributes
- Meta tags for SEO and mobile
- Valid HTML5 structure

## Future Roadmap

### Phase 1: Core Stability
- Comprehensive error handling
- Performance optimizations
- Cross-browser testing
- Documentation improvements

### Phase 2: Enhanced UX
- Advanced code highlighting
- Better mobile experience
- Keyboard shortcuts
- Export/import functionality

### Phase 3: Advanced Features
- Real-time collaboration
- Advanced search capabilities
- Integration with development tools
- Analytics and insights

## Getting Started for New Developers

1. **Clone the repository** and open `index.html` in a browser
2. **Review the code structure** starting with `script.js` ChatAssistant class
3. **Test with mock data** before connecting to real API
4. **Make incremental changes** and test thoroughly
5. **Follow the existing code patterns** for consistency

## Support and Resources

- **MDN Web Docs**: For vanilla JavaScript and Web APIs
- **ChatGPT Interface**: Reference for UI/UX patterns
- **GitHub Pages Docs**: For deployment and hosting
- **Pinecone Docs**: For understanding the backend data structure

Remember: This is a static site that must work without any build process or server-side code. All functionality must be client-side JavaScript compatible with GitHub Pages hosting.
