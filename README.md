# Real-Time Chat Application

A modern, real-time chat application built with React, FastAPI, and WebSocket technology. Features user authentication, real-time messaging, and online user tracking.

## 🚀 Features

- **Real-time messaging** with WebSocket connections
- **User authentication** using custom JWT
- **Online user tracking** and user list
- **Responsive design** with modern UI
- **System messages** for user join/leave notifications

## 🛠️ Tech Stack

### Frontend
- **React 19** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **JWT** - Authentication and user management
- **CSS Modules** - Scoped styling

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Primary database
- **Redis** - Caching and session management
- **WebSocket** - Real-time bidirectional communication
 - **Uvicorn** - ASGI server
 - **Alembic** - Database migrations
 - **fastapi-limiter** - Rate limiting backed by Redis
 - **Python logging** - Centralized app logging

## 🖼️ Screenshots

<img width="1920" height="915" alt="image" src="https://github.com/user-attachments/assets/78c62ef9-3347-4d6d-9cf1-7855f0fe8df0" />

## 🚀 Quick Start with Docker

### Prerequisites

- **Docker** and **Docker Compose** installed
- **JWT** for authentication

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mikhailofficial/simple-chat-fastapi.git
   cd simple-chat-fastapi
   ```

2. **Set up environment variables**

   Copy the example environment files and configure them:

   **Backend:**
   ```bash
   cp backend/src/.env.example backend/src/.env
   ```

   **Frontend:**
   ```bash
   cp frontend/.env.example frontend/.env
   ```

   Then edit both `.env` files with your actual values.

3. **Start the application**
   ```bash
   docker compose up --build
   ```

4. **Access the application**

   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Stopping the application
```bash
docker compose down
```

## 🔧 Development

### Project Structure

```
simple-chat-fastapi/
├── backend/
│   ├── src/
│   │   ├── app.py               # FastAPI application (lifespan, middleware, routers)
│   │   ├── routes/              # API routes (e.g., chat endpoints, WebSocket)
│   │   ├── database/            # DB engine, sessions, CRUD helpers, models
│   │   │   ├── models/          # SQLAlchemy models
│   │   ├── core/                # Core utilities (e.g., Redis client)
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── dependencies.py      # FastAPI dependencies (auth helpers, etc.)
│   │   ├── config.py            # Settings and config
│   │   ├── utils.py             # JWT utilities and helpers
│   │   ├── .env.example         # Environment variables template
│   │   └── .env                 # Your environment variables (not in git)
│   ├── migrations/              # Alembic migration scripts
│   ├── logging_config.ini       # Centralized Python logging configuration
│   ├── server.py                # ASGI app export; loads logging config
│   └── Dockerfile               # Backend container
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   └── hooks/              # Custom React hooks
│   ├── package.json            # Node.js dependencies
│   ├── .env.example            # Environment variables template
│   ├── .env                    # Your environment variables (not in git)
│   └── Dockerfile              # Frontend container
└── docker-compose.yaml         # Multi-container setup
```


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Happy Chatting! 🎉**
