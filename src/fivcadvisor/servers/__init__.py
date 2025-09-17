"""
FivcAdvisor FastAPI Server.

This module provides a REST API server for FivcAdvisor flows.
"""

__all__ = ["create_server_app", "run_server_app", "app"]

import datetime
import time

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from fivcadvisor import __version__
from fivcadvisor.logs import default_logger
from fivcadvisor.tools import default_retriever

from .routes import router as api_router
from .sessions import default_manager


@asynccontextmanager
async def _lifespan(server_app: FastAPI):
    """Application lifespan manager."""

    default_logger.info("Starting FivcAdvisor API server...")

    # Startup logic
    try:
        # Initialize any required services here
        default_logger.info("Server startup completed successfully")
        yield
    except Exception as e:
        default_logger.error(f"Server startup failed: {e}")
        raise
    finally:
        # Cleanup logic
        default_logger.info("Shutting down FivcAdvisor API server...")


def create_server_app(**kwargs) -> FastAPI:
    """Create and configure the FastAPI application."""
    default_manager()  # Initialize the session manager
    default_retriever()  # Initialize the tools retriever

    sever_app = FastAPI(
        title="FivcAdvisor API",
        description="REST API for FivcAdvisor - "
        "Intelligent agent ecosystem for autonomous tool generation and "
        "dynamic crew orchestration",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=_lifespan,
    )

    # Configure CORS
    sever_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure this properly for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    sever_app.include_router(api_router, prefix="/api/v1")

    # Global exception handler
    @sever_app.exception_handler(Exception)
    async def _exception(request: Request, exc: Exception):
        default_logger.error(f"Global exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc),
                "timestamp": datetime.datetime.now().isoformat(),
            },
        )

    # Request logging middleware
    @sever_app.middleware("http")
    async def _log(request: Request, call_next):
        start_time = time.time()

        # Add timestamp to request state
        request.state.timestamp = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        default_logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )

        return response

    # Root endpoint
    @sever_app.get("/")
    async def _root():
        """Root endpoint with basic information."""
        return {
            "name": "FivcAdvisor API",
            "version": __version__,
            "description": "REST API for FivcAdvisor flows",
            "docs": "/docs",
            "health": "/health",
        }

    @sever_app.get("/health")
    async def health():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": __version__,
            "timestamp": datetime.datetime.now().isoformat(),
        }

    return sever_app


def run_server_app(
    server_app: FastAPI,
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    log_level: str = "info",
):
    """Run the FastAPI server using uvicorn."""
    import uvicorn

    default_logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        server_app,
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True,
    )


# Create the application instance
app = create_server_app()

if __name__ == "__main__":
    run_server_app(app)
