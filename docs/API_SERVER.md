# 🚀 FivcAdvisor API Server

Your FivcAdvisor project now has a **production-ready REST API server** that exposes all your flows through clean HTTP endpoints, perfect for AG-UI integration!

## ✅ What's Been Added

### 🏗️ **Core Server Components**
- **FastAPI Server** (`src/fivcadvisor/servers/__init__.py`) - Production-ready async server
- **Server Schemas** (`src/fivcadvisor/servers/schemas.py`) - Type-safe Pydantic schemas
- **Server Routes** (`src/fivcadvisor/servers/routes.py`) - RESTful endpoints for all flows
- **Enhanced CLI** - New `fivcadvisor serve` command

### 📚 **Documentation & Examples**
- **Complete API Docs** (`docs/API_SERVER.md`) - Full API reference
- **Python Client Example** (`examples/server/api_client_example.py`)
- **Test Scripts** (`examples/server/test_server.py`)

### 🔧 **Dependencies Added**
- `fastapi>=0.104.0` - Modern async web framework
- `uvicorn[standard]>=0.24.0` - ASGI server with performance extras

## 🚀 Quick Start

### 1. Install Dependencies
```bash
uv sync  # or pip install -e .
```

### 2. Start the Server
```bash
# Basic server (localhost:8000)
fivcadvisor serve

# Custom configuration
fivcadvisor serve --host 0.0.0.0 --port 8080 --reload
```

### 3. Test the API
```bash
# Health check
curl http://localhost:8000/api/v1/health

# List available flows
curl http://localhost:8000/api/v1/flows

# Execute a flow
curl -X POST http://localhost:8000/api/v1/flows/default/execute \
  -H "Content-Type: application/json" \
  -d '{"user_query": "Calculate 15 * 23", "verbose": true}'
```

### 4. View Interactive Documentation
Open http://localhost:8000/docs in your browser for full API documentation with interactive testing!

## 🎯 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Server health check |
| `GET` | `/api/v1/flows` | List available flows |
| `GET` | `/api/v1/flows/{type}` | Get flow information |
| `POST` | `/api/v1/flows/{type}/execute` | Execute a flow |

### Flow Types
- **`default`** - Intelligent complexity assessment and routing
- **`simple`** - Direct execution for simple tasks
- **`complex`** - Multi-step planning for complex tasks

## 🔗 AG-UI Integration

The API is designed for easy frontend integration:

```javascript
// JavaScript/AG-UI example
async function executeFlow(query, flowType = 'default') {
  const response = await fetch(`http://localhost:8000/api/v1/flows/${flowType}/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_query: query,
      verbose: true
    })
  });

  const result = await response.json();
  return result.status === 'success' ? result.result : result.error;
}

// Usage
const answer = await executeFlow("What is machine learning?");
console.log(answer);
```

## ✅ Tested Features

- ✅ **Server Startup** - Clean startup with proper logging
- ✅ **Health Checks** - `/api/v1/health` endpoint working
- ✅ **Flow Listing** - `/api/v1/flows` returns all available flows
- ✅ **Flow Execution** - Successfully executed default flow with "Calculate 2 + 2"
- ✅ **Error Handling** - Proper error responses and logging
- ✅ **CORS Support** - Ready for web frontend integration
- ✅ **OpenAPI Docs** - Interactive documentation at `/docs`

## 🛠️ Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn fivcadvisor.api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -e .
EXPOSE 8000
CMD ["fivcadvisor", "serve", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
```env
OPENAI_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here
CONFIG_FILE=configs/config.yaml
```

## 🎉 Success!

Your FivcAdvisor project now has:
- **REST API Server** exposing all flows
- **Interactive Documentation** at `/docs`
- **AG-UI Ready** with CORS support
- **Production Ready** with proper logging and error handling
- **Type Safe** with Pydantic schemas
- **Async Support** for high performance

The server maintains all existing flow functionality while providing a clean HTTP interface for integration with any frontend application!

## 📖 Next Steps

1. **Start the server**: `fivcadvisor serve`
2. **Explore the API**: Visit http://localhost:8000/docs
3. **Integrate with AG-UI**: Use the JavaScript examples above
4. **Customize**: Modify `src/fivcadvisor/servers/` for your specific needs

Happy coding! 🚀
