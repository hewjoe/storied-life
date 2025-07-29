# Storied Life - Project Setup Complete! 🎉

Welcome to Storied Life, your open-source digital legacy platform. This document provides an overview of the project structure and next steps to get you started.

## 📁 Project Structure

```
storied-life/
├── 📄 README.md                    # Main project documentation
├── 📄 CONTRIBUTING.md               # Contribution guidelines
├── 📄 LICENSE                      # MIT License
├── 📄 env.example                  # Environment variables template
├── 📄 .gitignore                   # Git ignore rules
├── 🐳 docker-compose.yml           # Production Docker setup
├── 🐳 docker-compose.dev.yml       # Development Docker setup
│
├── 🐍 backend/                     # FastAPI Backend
│   ├── 📄 main.py                  # FastAPI application entry point
│   ├── 📄 requirements.txt         # Python dependencies
│   ├── 📄 requirements.dev.txt     # Development dependencies
│   ├── 🐳 Dockerfile               # Backend container
│   └── 📁 app/                     # Application code
│       ├── 📁 api/                 # API routes and endpoints
│       ├── 📁 core/                # Core configuration and utilities
│       ├── 📁 db/                  # Database models and connections
│       ├── 📁 models/              # SQLAlchemy models
│       ├── 📁 services/            # Business logic services
│       └── 📁 utils/               # Utility functions
│
├── ⚛️  frontend/                   # React TypeScript Frontend
│   ├── 📄 package.json             # Node.js dependencies
│   ├── 📄 vite.config.ts           # Vite configuration
│   ├── 📄 tsconfig.json            # TypeScript configuration
│   ├── 📄 tailwind.config.js       # Tailwind CSS configuration
│   ├── 🐳 Dockerfile               # Frontend container
│   ├── 🐳 nginx.conf               # Nginx configuration
│   ├── 📁 public/                  # Static assets
│   └── 📁 src/                     # Source code
│       ├── 📁 components/          # React components
│       ├── 📁 pages/               # Page components
│       ├── 📁 hooks/               # Custom React hooks
│       ├── 📁 services/            # API services
│       ├── 📁 store/               # State management
│       ├── 📁 types/               # TypeScript types
│       └── 📁 utils/               # Utility functions
│
├── 🗄️  database/                   # Database setup
│   └── 📁 init/                    # Database initialization scripts
│       └── 📄 01-init.sql          # PostgreSQL schema
│
├── 🤖 litellm/                     # AI Proxy Configuration
│   ├── 📄 config.yaml              # Production AI config
│   └── 📄 config.dev.yaml          # Development AI config
│
├── 🔐 authelia/                    # Authentication service config
├── 🐳 docker/                      # Additional Docker configurations
├── 📚 docs/                        # Documentation
├── 🛠️  scripts/                    # Utility scripts
│   └── 📄 setup.sh                 # Automated setup script
├── 🧪 tests/                       # Integration tests
└── 🚀 deploy/                      # Deployment configurations
```

## 🚀 Quick Start

### Option 1: Containerized Development (Recommended for Clean Environment)
Keep your development machine clean with everything running in Docker containers:

```bash
# Start the complete containerized development environment
chmod +x scripts/dev-containerized.sh
./scripts/dev-containerized.sh
```

This will:
- ✅ Start all services in Docker containers (frontend, backend, databases)
- ✅ Enable hot reloading for both frontend and backend
- ✅ Mount source code as volumes for instant updates
- ✅ Provide all development tools without installing dependencies locally

**Access URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

### Option 2: Automated Local Setup
```bash
# Make setup script executable and run it
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Option 3: Manual Local Setup

1. **Environment Configuration**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Start Development Services**
   ```bash
   # Start databases only
   docker-compose -f docker-compose.dev.yml up -d postgres neo4j redis litellm mailhog
   
   # Start backend (Terminal 1)
   cd backend && source venv/bin/activate && uvicorn main:app --reload
   
   # Start frontend (Terminal 2)
   cd frontend && npm run dev
   ```

## 🐳 Development Environments

### Containerized Development (Recommended)
- **Pros**: Clean machine, consistent environment, easy collaboration
- **Cons**: Slightly slower than native (especially on file changes)
- **Use when**: You want to avoid installing dependencies locally
- **Command**: `./scripts/dev-containerized.sh`

### Local Development 
- **Pros**: Faster file changes, native debugging, IDE integration
- **Cons**: Requires local dependency installation, potential version conflicts
- **Use when**: You need maximum development speed or debugging capabilities
- **Command**: Follow Option 2 or 3 above

### Production Environment
- **All services containerized with SSL and reverse proxy**
- **Command**: `docker-compose up -d`

## 🏗️ Architecture Overview

### Technology Stack
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18 + TypeScript + Vite
- **Databases**: PostgreSQL + Neo4J + Redis
- **AI**: LiteLLM proxy (OpenAI, Anthropic, Gemini, Ollama)
- **Styling**: Tailwind CSS
- **Infrastructure**: Docker + Traefik + Authelia

### Key Features Implemented
- ✅ Project structure and configuration
- ✅ Docker containerization
- ✅ Database schema design
- ✅ API endpoint structure
- ✅ Frontend component architecture
- ✅ AI integration setup
- ✅ Authentication framework
- ✅ Development tooling

## 🎯 Next Development Steps

### Phase 1: Core MVP (Weeks 1-4)
1. **User Authentication**
   - Complete user registration/login
   - Email verification
   - Password reset

2. **Legacy Management**
   - Create/edit legacies
   - Upload photos
   - Basic privacy controls

3. **Story Management**
   - Add/edit stories
   - Basic text editor
   - Story approval workflow

4. **Basic AI Chat**
   - Simple persona chat
   - Story-based responses
   - Basic conversation memory

### Phase 2: Enhanced Features (Weeks 5-8)
1. **Advanced UI/UX**
   - Responsive design
   - Beautiful legacy pages
   - Photo galleries

2. **Search & Organization**
   - Full-text search
   - Tag system
   - Timeline views

3. **Enhanced AI**
   - Better persona development
   - Voice synthesis
   - Conversation improvements

### Phase 3: Advanced Features (Weeks 9-12)
1. **Multi-input Collection**
   - SMS integration
   - Email import
   - QR code sharing

2. **Social Features**
   - Family groups
   - Sharing controls
   - Notifications

3. **Advanced Analytics**
   - Usage insights
   - Legacy statistics
   - AI conversation analytics

## 🔧 Development Commands

### Backend
```bash
cd backend
source venv/bin/activate

# Run development server
uvicorn main:app --reload

# Run tests
pytest

# Format code
black .
ruff check .

# Type checking
mypy .
```

### Frontend
```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Lint and format
npm run lint
npm run format
```

### Docker

#### Containerized Development (Everything in Docker)
```bash
# Start complete development environment
./scripts/dev-containerized.sh

# View logs for all services
docker-compose -f docker-compose.dev.yml logs -f

# View logs for specific service
docker-compose -f docker-compose.dev.yml logs -f frontend
docker-compose -f docker-compose.dev.yml logs -f backend

# Restart a service
docker-compose -f docker-compose.dev.yml restart backend
docker-compose -f docker-compose.dev.yml restart frontend

# Stop all services
docker-compose -f docker-compose.dev.yml down

# Rebuild and restart
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up -d

# Shell access
docker exec -it storied-life-dev-backend bash
docker exec -it storied-life-dev-frontend sh
```

#### Hybrid Development (Databases in Docker, Apps Local)
```bash
# Start only databases and external services
docker-compose -f docker-compose.dev.yml up -d postgres neo4j redis litellm mailhog

# Stop external services
docker-compose -f docker-compose.dev.yml down
```

#### Production Environment
```bash
# Start production environment
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📚 Documentation

- **User Guide**: `docs/user-guide/`
- **API Documentation**: `docs/api/`
- **Development Guide**: `docs/development/`
- **Deployment Guide**: `docs/deployment/`

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) for details on:
- Code standards
- Development workflow
- Pull request process
- Community guidelines

## 🔒 Security

- All sensitive data is encrypted
- Environment variables for secrets
- Role-based access control
- GDPR compliance ready

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/storied-life/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/storied-life/discussions)
- **Documentation**: `docs/` directory

---

## 🎉 You're Ready to Build!

Your Storied Life project is now set up with:
- ✅ Complete project structure
- ✅ Development environment
- ✅ Database schema
- ✅ API framework
- ✅ Frontend foundation
- ✅ AI integration
- ✅ Docker containerization
- ✅ Documentation structure

**Next Step**: Run `./scripts/setup.sh` to initialize your development environment and start building this meaningful platform that helps families preserve and share their most precious memories.

*"Every story matters. Every memory counts. Let's build something beautiful together."* 