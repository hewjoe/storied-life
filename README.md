# Storied Life

> *Preserving memories. Honoring legacies. Connecting families.*

An open-source digital legacy platform that captures, organizes, and preserves the stories and memories of loved ones through AI-powered interactive experiences.

## 🌟 Vision

Storied Life creates a lasting digital legacy by:
- Capturing authentic stories from family and friends
- Preserving personalities through AI-powered personas  
- Providing interactive legacy experiences
- Maintaining complete data ownership and privacy
- Supporting both self-hosted and managed deployments

## ✨ Key Features

### Core Functionality
- **Multi-Input Story Collection**: Web forms, mobile apps, SMS, email, and QR codes
- **AI-Powered Personas**: Interactive conversations with personalities based on collected stories
- **Intelligent Organization**: Advanced search, tagging, and relationship mapping
- **Privacy Controls**: Granular permissions and group-based access
- **Responsive Design**: Beautiful, respectful interface across all devices

### Advanced Capabilities
- **Voice Synthesis**: AI-generated voices from audio samples
- **Timeline Views**: Chronological story organization
- **Social Integration**: Import from Facebook, Instagram, and other platforms
- **Multi-Tenant Support**: Secure family isolation with enterprise features

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 20+ with nvm (for local development)
- Python 3.11+ with uv (for local development)

### Self-Hosted Deployment

```bash
git clone https://github.com/your-org/storied-life.git
cd storied-life
cp .env.example .env
# Edit .env with your configuration
docker-compose up -d
```

Visit `http://localhost` to access your Storied Life instance.

### Development Setup

```bash
# Clone and setup
git clone https://github.com/your-org/storied-life.git
cd storied-life

# Quick setup with Makefile
make setup           # Initial project setup
make nvm-setup       # Setup Node.js environment with nvm
make nvm-check       # Verify nvm and Node.js setup

# Manual backend setup (with uv)
cd backend
uv sync              # Install dependencies with uv
uv run python main.py

# Manual frontend setup (with nvm)
cd frontend
nvm use              # Use Node.js version from .nvmrc
npm install

# Start development environment
make start-dev       # Docker services + development containers
# OR start individual services
make start           # Production-like environment
```

## 📁 Project Structure

```
storied-life/
├── backend/           # FastAPI backend
├── frontend/          # React TypeScript frontend
├── docker/           # Docker configurations
├── docs/             # Documentation
├── scripts/          # Utility scripts
├── tests/            # Integration tests
└── deploy/           # Deployment configurations
```

## 🏗️ Architecture

### Technology Stack
- **Backend**: FastAPI (Python 3.11+), PostgreSQL, Neo4J, managed with `uv`
- **Frontend**: React + TypeScript, Tailwind CSS, Vite, managed with `nvm`
- **AI**: LiteLLM proxy supporting OpenAI, Anthropic, Gemini, Ollama
- **Infrastructure**: Docker, Traefik, Authelia
- **Storage**: S3-compatible or local filesystem

### Database Design
- **PostgreSQL**: Primary relational data (users, stories, legacies)
- **Neo4J**: Relationship graphs and social connections
- **Redis**: Caching and session management

## 🔒 Privacy & Security

- **Encryption**: All data encrypted at rest and in transit
- **Access Control**: Role-based permissions with granular story access
- **Data Ownership**: Complete control over your family's data
- **GDPR Compliant**: Data export, deletion, and portability
- **Self-Hosted**: Keep sensitive memories on your own infrastructure

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with respect for families navigating loss
- Inspired by the belief that stories connect us across time
- Dedicated to preserving the essence of those we've lost

## 📞 Support

- **Documentation**: [docs.storied-life.org](https://docs.storied-life.org)
- **Issues**: [GitHub Issues](https://github.com/your-org/storied-life/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/storied-life/discussions)
- **Community**: [Discord Server](https://discord.gg/storied-life)

---

*"In every story lives a piece of eternity."* 