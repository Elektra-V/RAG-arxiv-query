"""FastAPI application for LangChain agent service."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from rag_api.logging import configure_logging
from rag_api.services.langchain.routes import router
from rag_api.settings import get_settings


def create_app() -> FastAPI:
    """Create the FastAPI app."""

    configure_logging()
    api = FastAPI(
        title="RAG LangChain Service",
        description="RAG API with LangChain agent, LangSmith tracing, and enhanced debugging",
        version="0.1.0",
    )
    api.include_router(router)

    @api.get("/", response_class=HTMLResponse)
    async def root():
        """Simple HTML UI for debugging."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>RAG API - LangChain Debug UI</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
                .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                h1 { color: #333; }
                .form-group { margin-bottom: 20px; }
                label { display: block; margin-bottom: 5px; font-weight: bold; }
                input[type="text"], textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
                textarea { min-height: 100px; resize: vertical; }
                button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
                button:hover { background: #0056b3; }
                .response { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 4px; }
                .debug { margin-top: 15px; padding: 15px; background: #e9ecef; border-radius: 4px; font-family: monospace; font-size: 12px; white-space: pre-wrap; }
                .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
                .status.healthy { background: #d4edda; color: #155724; }
                .status.degraded { background: #fff3cd; color: #856404; }
                .links { margin-top: 20px; }
                .links a { display: inline-block; margin-right: 15px; color: #007bff; text-decoration: none; }
                .links a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔍 RAG API - LangChain Debug Interface</h1>
                <div class="links">
                    <a href="/docs">📚 API Docs (Swagger)</a>
                    <a href="/redoc">📖 ReDoc</a>
                    <a href="/status">⚙️ Status</a>
                </div>
                <div id="status"></div>
                <form id="queryForm">
                    <div class="form-group">
                        <label for="question">Question:</label>
                        <textarea id="question" name="question" placeholder="Enter your question here..."></textarea>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="debug" checked> Include debug information
                        </label>
                    </div>
                    <button type="submit">Submit Query</button>
                </form>
                <div id="response"></div>
            </div>
            <script>
                // Load status on page load
                fetch('/status')
                    .then(r => r.json())
                    .then(data => {
                        const statusDiv = document.getElementById('status');
                        statusDiv.className = 'status ' + data.status;
                        statusDiv.innerHTML = `<strong>Status:</strong> ${data.status.toUpperCase()} | 
                            Provider: ${data.configuration.llm_provider} | 
                            LangSmith: ${data.langsmith.tracing_enabled ? 'Enabled' : 'Disabled'}`;
                    });

                document.getElementById('queryForm').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const question = document.getElementById('question').value;
                    const debug = document.getElementById('debug').checked;
                    const responseDiv = document.getElementById('response');
                    responseDiv.innerHTML = '<div class="response">Processing...</div>';

                    try {
                        const response = await fetch('/query', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ question, debug })
                        });
                        const data = await response.json();
                        
                        let html = '<div class="response"><strong>Answer:</strong><br>' + 
                            data.answer.replace(/\\n/g, '<br>') + '</div>';
                        
                        if (data.debug && Object.keys(data.debug).length > 0) {
                            html += '<div class="debug"><strong>Debug Info:</strong><br>' + 
                                JSON.stringify(data.debug, null, 2) + '</div>';
                        }
                        
                        responseDiv.innerHTML = html;
                    } catch (error) {
                        responseDiv.innerHTML = '<div class="response" style="background: #f8d7da; color: #721c24;">Error: ' + error.message + '</div>';
                    }
                });
            </script>
        </body>
        </html>
        """

    return api


app = create_app()


def main() -> None:
    """Run the FastAPI server."""

    settings = get_settings()
    import uvicorn

    uvicorn.run(
        "rag_api.services.langchain.app:app",
        host=settings.langchain_host,
        port=settings.langchain_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
