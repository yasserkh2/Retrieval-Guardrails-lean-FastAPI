"""
FastAPI application factory.
Wires up middleware, routes, and initializes the retrieval index at startup.
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routes import answer
from app.core.metrics import LatencyMiddleware
from app.guardrails import denylist


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup/shutdown lifecycle manager.
    Initializes all services at startup.
    """
    # Startup: initialize services
    print("🚀 Initializing services...")
    
    # Initialize retrieval service (which builds index and corpus)
    from app.services.retrieval_service import get_retrieval_service
    retrieval_service = get_retrieval_service()
    retrieval_service.initialize()
    
    # Initialize guardrails with TF-IDF vectors
    try:
        from app.retrieval.index import get_index
        index = get_index()
        denylist.initialize_denylist_vectors(index.vectorizer)
    except Exception as e:
        print(f"⚠️ Failed to initialize guardrail vectors: {e}")
    
    print("✅ Services initialized successfully")
    
    yield
    
    # Shutdown: cleanup if needed
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Mini RAG Service",
    description="Lean retrieval-augmented answering with guardrails",
    version="1.0.0",
    lifespan=lifespan
)

# Add latency tracking middleware
app.add_middleware(LatencyMiddleware)

# Include routers
app.include_router(answer.router, tags=["Answer"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "mini-rag",
        "status": "healthy",
        "endpoints": ["/answer", "/metrics", "/docs"]
    }
