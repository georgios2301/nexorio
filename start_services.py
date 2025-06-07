#!/usr/bin/env python3
"""
Unified service starter for DZMetall Lieferschein System
Runs both the FastAPI backend and Flask PDF server
"""

import os
import sys
import signal
import asyncio
import threading
import time
from multiprocessing import Process

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Add Lieferschein directories to path for imports
lieferschein_backend = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Lieferschein', 'backend')
lieferschein_programm = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Lieferschein', 'Programm')
if os.path.exists(lieferschein_backend):
    sys.path.insert(0, lieferschein_backend)
if os.path.exists(lieferschein_programm):
    sys.path.insert(0, lieferschein_programm)

def run_backend():
    """Run the FastAPI backend server"""
    print("WARNING: run_backend() called - this should not happen on Render!")
    import uvicorn
    from simple_supabase_server import app
    
    port = int(os.getenv("PORT", 10000))
    
    # On Render, we need to run on a single port
    if os.getenv("RENDER"):
        print(f"Running on Render - Backend will use port {port}")
        # The backend will handle /api/* routes
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    else:
        # Local development - use separate ports
        backend_port = 8001
        print(f"Running locally - Backend on port {backend_port}")
        uvicorn.run(app, host="0.0.0.0", port=backend_port, log_level="info")

def run_pdf_server():
    """Run the Flask PDF server"""
    from pdf_server import app
    
    # On Render, we'll proxy PDF requests through the main app
    if os.getenv("RENDER"):
        print("PDF server functionality integrated into main app")
        # PDF routes will be handled by the main FastAPI app
        return
    else:
        # Local development - use separate port
        pdf_port = 4000
        print(f"Running locally - PDF server on port {pdf_port}")
        app.run(host="0.0.0.0", port=pdf_port, debug=False)

def create_unified_app():
    """Create a unified app that handles both API and PDF generation"""
    from fastapi import FastAPI, Request, Response
    from fastapi.responses import StreamingResponse
    import uvicorn
    from simple_supabase_server import app as backend_app
    from pdf_server import app as pdf_app
    from werkzeug.test import Client
    from werkzeug.serving import WSGIRequestHandler
    import io
    
    # Create a new FastAPI app that combines both services
    app = FastAPI(title="DZMetall Unified Service")
    
    # Import the backend routes directly
    from simple_supabase_server import app as backend_app
    
    # Add health check at root level
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "unified-server"}
    
    # Mount the backend app only for /api routes
    app.mount("/api", backend_app)
    
    # Create a wrapper for PDF generation
    @app.post("/generate-pdf")
    async def generate_pdf_wrapper(request: Request):
        """Proxy PDF generation requests to Flask app"""
        # Get the request body
        body = await request.body()
        
        # Create a test client for the Flask app
        client = Client(pdf_app, Response)
        
        # Make the request to Flask app
        response = client.post(
            '/generate-pdf',
            data=body,
            content_type='application/json',
            headers=dict(request.headers)
        )
        
        # Return the response
        return StreamingResponse(
            io.BytesIO(response.get_data()),
            media_type=response.content_type,
            headers=dict(response.headers)
        )
    
    return app

def main():
    """Main entry point"""
    port = int(os.getenv("PORT", 10000))
    is_render = os.getenv("RENDER") == "true"
    
    print(f"Environment check: RENDER={os.getenv('RENDER')}, is_render={is_render}, PORT={port}")
    
    if is_render:
        # On Render, run unified app on single port
        print(f"Starting unified service on Render (port {port})...")
        
        # Import here to avoid circular imports
        import uvicorn
        from fastapi import FastAPI, Request, Response
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import StreamingResponse
        from simple_supabase_server import app as backend_app
        from pdf_server import app as pdf_app
        from werkzeug.test import Client
        import io
        
        # Create unified app directly here
        unified_app = FastAPI(title="DZMetall Unified Service")
        
        # Add health endpoint
        @unified_app.get("/health")
        async def health():
            return {"status": "healthy", "service": "unified-server"}
        
        # Mount backend for API routes
        unified_app.mount("/api", backend_app)
        
        # Add PDF generation endpoint
        @unified_app.post("/generate-pdf")
        async def generate_pdf(request: Request):
            print("PDF generation endpoint called")
            body = await request.body()
            client = Client(pdf_app, Response)
            response = client.post(
                '/generate-pdf',
                data=body,
                content_type='application/json',
                headers=dict(request.headers)
            )
            return StreamingResponse(
                io.BytesIO(response.get_data()),
                media_type=response.content_type,
                headers=dict(response.headers)
            )
        
        # Add CORS middleware
        unified_app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # List all registered routes
        print("\nRegistered routes:")
        for route in unified_app.routes:
            if hasattr(route, 'path'):
                print(f"  {route.methods if hasattr(route, 'methods') else 'MOUNT'} {route.path}")
        
        # Run the unified app
        import uvicorn
        print(f"\nStarting unified app on port {port}...")
        uvicorn.run(unified_app, host="0.0.0.0", port=port, log_level="info")
    else:
        # Check if we're actually on Render but env var is not set correctly
        if os.getenv("PORT") == "10000":
            print("WARNING: Port 10000 detected, might be Render environment")
            print("Forcing unified mode...")
            # Force unified mode
            is_render = True
            # Restart with unified mode
            return main()  # Call main again
            
        # Local development - run services separately
        print(f"Starting services for local development (RENDER env not 'true', got: {os.getenv('RENDER')})...")
        
        # Start backend in a thread
        backend_thread = threading.Thread(target=run_backend)
        backend_thread.daemon = True
        backend_thread.start()
        
        # Start PDF server in main thread
        time.sleep(2)  # Give backend time to start
        run_pdf_server()

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    print("\nShutting down services...")
    sys.exit(0)

if __name__ == "__main__":
    print("\n" + "="*50)
    print("STARTING start_services.py")
    print(f"Script: {__file__}")
    print(f"Working directory: {os.getcwd()}")
    print(f"RENDER env: {os.getenv('RENDER')}")
    print("="*50 + "\n")
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start services
    main()