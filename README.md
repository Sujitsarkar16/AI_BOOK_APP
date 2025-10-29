# BookForge AI - Complete Implementation

AI-powered e-book generation system with 7 specialized agents working collaboratively to write complete books.

## Project Structure

### Backend (`backend/`)
Python FastAPI backend with AutoGen multi-agent system:
- **Models**: Book, Chapter, Source, AgentLog (SQLAlchemy)
- **Services**: RAG service (Chroma), Research service (DuckDuckGo)
- **Agents**: 7 specialized AutoGen agents
- **API**: REST + WebSocket for real-time updates
- **LLM**: Google Gemini API integration

### Frontend (`src/`)
React TypeScript frontend with shadcn/ui:
- **Pages**: Index, Configure, Generate, Preview
- **Components**: AIAgentPanel, UI components
- **Services**: API client, WebSocket hook
- **Real-time updates** via WebSocket

## Setup Instructions

### Backend Setup

1. **Install Python dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

3. **Run the backend:**
```bash
python main.py
```

Backend runs on `http://localhost:8000`

### Frontend Setup

1. **Install dependencies (already installed):**
```bash
npm install
```

2. **Run the frontend:**
```bash
npm run dev
```

Frontend runs on `http://localhost:8080`

## Features

### 7 AI Agents

1. **Ideation Agent**: Refines and conceptualizes book ideas
2. **Research Agent**: Gathers information from web sources
3. **Outline Agent**: Creates detailed book structure
4. **Writing Agent**: Writes engaging chapter content
5. **Content Agent**: Enhances with examples and depth
6. **Editor Agent**: Polishes and ensures quality
7. **Format Agent**: Applies final formatting

### User Flow

1. **Configure**: Set up book concept, genre, chapters, tone
2. **Generate**: Agents create outline, research, and write chapters
3. **Preview**: Real-time preview of generated content
4. **Chat**: Interact with agents for modifications
5. **Export**: Download as markdown or HTML

## API Endpoints

### Books
- `POST /api/books` - Create book
- `GET /api/books/{id}` - Get book
- `GET /api/books/{id}/status` - Generation status
- `DELETE /api/books/{id}` - Delete book

### Chapters
- `GET /api/books/{id}/chapters` - List chapters
- `GET /api/books/{id}/chapters/{cid}` - Get chapter
- `POST /api/books/{id}/chapters/{cid}/generate` - Generate chapter
- `POST /api/books/{id}/chapters/generate-all` - Generate all
- `PUT /api/books/{id}/chapters/{cid}` - Update chapter

### Chat
- `POST /api/books/{id}/chat` - Send message to agents

### Export
- `GET /api/books/{id}/export/markdown` - Export as .md
- `GET /api/books/{id}/export/html` - Export as HTML

### WebSocket
- `WS /ws/books/{id}` - Real-time updates

## Database

SQLite database (`bookforge.db`) with tables:
- `books`: Book configurations
- `chapters`: Chapter content and metadata
- `sources`: Research citations
- `agent_logs`: Agent activity tracking

## RAG System

Vector database using Chroma for semantic search:
- Free embeddings: `sentence-transformers/all-MiniLM-L6-v2`
- Web research: DuckDuckGo (free)
- Context retrieval for writing agents

## Technologies

### Backend
- FastAPI (REST + WebSocket)
- SQLAlchemy (Database ORM)
- AutoGen (Multi-agent orchestration)
- Chroma (Vector database)
- Google Gemini (LLM)

### Frontend
- React + TypeScript
- Vite
- shadcn/ui
- TanStack Query
- Axios
- Sonner (Toast notifications)

## Notes

- Backend must run before frontend
- Requires valid Gemini API key
- First run creates database and Chroma collections
- WebSocket provides real-time agent status updates
- All agents use Gemini except Format agent (pure text processing)

## Development

Backend logs show agent activities and API requests.
Frontend uses React DevTools for debugging.

## License

See project license file.
