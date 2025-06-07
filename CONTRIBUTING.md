# Contributing to Storied Life

Thank you for your interest in contributing to Storied Life! This project serves families navigating loss, so all contributions are made with deep respect and care.

## 🌟 Ways to Contribute

- **Code**: Backend, frontend, AI features, documentation
- **Testing**: Manual testing, automated test creation
- **Design**: UI/UX improvements, accessibility enhancements  
- **Documentation**: Guides, tutorials, API documentation
- **Community**: Support in discussions, issue triage
- **Feedback**: User experience insights, feature suggestions

## 🚀 Getting Started

### Development Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/storied-life.git
   cd storied-life
   ```

2. **Install dependencies**
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements.dev.txt

   # Frontend
   cd ../frontend
   npm install
   ```

3. **Set up databases**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d postgres neo4j redis
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

5. **Run development servers**
   ```bash
   # Backend (Terminal 1)
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000

   # Frontend (Terminal 2)  
   cd frontend
   npm run dev
   ```

### Code Standards

#### Python (Backend)
- **Formatter**: Black with line length 88
- **Linter**: Ruff for fast Python linting
- **Type Hints**: Required for all functions
- **Testing**: Pytest with minimum 80% coverage
- **Style**: Follow PEP 8 and FastAPI best practices

```bash
# Run formatting and linting
cd backend
black .
ruff check .
pytest --cov=app tests/
```

#### TypeScript (Frontend)
- **Formatter**: Prettier
- **Linter**: ESLint with TypeScript rules
- **Testing**: Vitest for unit tests, Playwright for E2E
- **Style**: Functional components with hooks

```bash
# Run formatting and linting
cd frontend  
npm run format
npm run lint
npm run test
npm run test:e2e
```

## 📝 Development Workflow

### Branch Strategy
- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/**: Individual feature development
- **hotfix/**: Critical production fixes

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, descriptive commit messages
   - Include tests for new functionality
   - Update documentation as needed

3. **Test thoroughly**
   ```bash
   # Run all tests
   npm run test:all          # Frontend tests
   pytest                    # Backend tests
   docker-compose run tests  # Integration tests
   ```

4. **Submit pull request**
   - Use the PR template
   - Link related issues
   - Request appropriate reviewers
   - Ensure CI passes

### Commit Message Format
```
type(scope): brief description

Longer description if needed explaining what and why.

Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`


## 🧪 Testing Guidelines

### Backend Testing
```python
# Example test structure
def test_create_story():
    # Arrange
    story_data = {"title": "Test Story", "content": "Content"}
    
    # Act
    response = client.post("/api/v1/stories", json=story_data)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["title"] == "Test Story"
```

### Frontend Testing
```typescript
// Component test example
test('renders story list', async () => {
  const stories = [
    { id: '1', title: 'Test Story', content: 'Content' }
  ];
  
  render(<StoryList stories={stories} />);
  
  expect(screen.getByText('Test Story')).toBeInTheDocument();
});
```

## 📚 Documentation

- **Code Comments**: Explain complex logic and AI interactions
- **Docstrings**: Required for all Python functions
- **README Updates**: Keep setup instructions current
- **API Documentation**: Auto-generated from OpenAPI specs
- **User Guides**: Clear tutorials for major features

## 🔒 Security Considerations

- **Sensitive Data**: Never commit secrets, API keys, or personal data
- **Privacy**: Respect the sensitive nature of memorial content
- **Dependencies**: Keep dependencies updated and secure
- **Access Control**: Test permission boundaries thoroughly
- **AI Safety**: Ensure AI responses are appropriate and respectful

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Clear description** of the issue
2. **Steps to reproduce** the problem  
3. **Expected vs actual behavior**
4. **Environment details** (OS, browser, versions)
5. **Screenshots/logs** if applicable
6. **Minimal reproduction** case when possible

Use the bug report template in GitHub Issues.

## 💡 Feature Requests

For new features:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** and user benefit
3. **Consider implementation** complexity
4. **Respect project scope** and memorial context
5. **Propose solutions** when possible

Use the feature request template in GitHub Issues.

## 🤝 Community Guidelines

### Code of Conduct

- **Respectful**: Honor the sensitive nature of this project
- **Inclusive**: Welcome contributors from all backgrounds  
- **Constructive**: Provide helpful feedback and support
- **Patient**: Understand that contributors may be grieving
- **Professional**: Maintain appropriate communication

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General project discussion
- **Discord**: Real-time chat and support
- **Email**: Security issues and private matters

## 🎯 Priority Areas

Current development priorities:

1. **Core MVP Features**: Story management, basic AI chat
2. **Privacy Controls**: Granular permissions system
3. **AI Improvements**: Better persona development
4. **Mobile Experience**: Responsive design enhancements
5. **Documentation**: User guides and deployment docs

## 🙏 Recognition

Contributors are recognized in:
- **README.md**: Contributor section
- **Release Notes**: Feature acknowledgments  
- **GitHub**: Contributor graph and stats
- **Community**: Discord contributor roles

Thank you for helping create a meaningful platform that honors memories and supports families. Every contribution makes a difference.

---

*"Technology at the service of human connection."* 