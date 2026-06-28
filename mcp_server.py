#!/usr/bin/env python3
"""
Servidor MCP para o ecossistema Agent Auth Proxy.
Expõe a ferramenta resolve_issue via SSE e REST.
"""

import os
import json
import asyncio
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import uvicorn

load_dotenv()

# Configurações
PROXY_URL = os.getenv("PROXY_URL", "https://gateway-mcp-varejo.onrender.com")
SECRET = os.getenv("AUTO_APPROVE_SECRET")
if not SECRET:
    print("⚠️ AUTO_APPROVE_SECRET não configurado")

app = FastAPI(title="MCP Server - Agent Auth Proxy")

# ========== ROTA PRINCIPAL (SSE) ==========
@app.get("/mcp")
@app.get("/mcp/")
async def mcp_sse():
    """Endpoint SSE para conexão MCP."""
    async def event_generator():
        # Lista de ferramentas disponíveis
        tools = [
            {
                "name": "resolve_issue",
                "description": "Solicita a resolução de um problema (ex: reembolso, cancelamento)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {"type": "string", "description": "ID do agente solicitante"},
                        "problem_type": {"type": "string", "description": "Tipo do problema"},
                        "description": {"type": "string", "description": "Descrição detalhada"},
                        "order_id": {"type": "string", "description": "ID do pedido (opcional)"},
                        "max_cost": {"type": "integer", "description": "Custo máximo em centavos"}
                    },
                    "required": ["agent_id", "problem_type", "description"]
                }
            }
        ]
        yield f"event: tools\ndata: {json.dumps(tools)}\n\n"
        yield f"event: ready\ndata: {{'status': 'listening'}}\n\n"
        # Mantém a conexão aberta
        while True:
            await asyncio.sleep(30)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# ========== ROTA REST (para API Integration) ==========
@app.get("/")
async def list_tools():
    """Lista de ferramentas para integração REST."""
    return {
        "tools": [
            {
                "name": "resolve_issue",
                "description": "Solicita a resolução de um problema",
                "parameters": {
                    "agent_id": {"type": "string"},
                    "problem_type": {"type": "string"},
                    "description": {"type": "string"},
                    "order_id": {"type": "string"},
                    "max_cost": {"type": "integer"}
                }
            }
        ]
    }

@app.post("/")
async def call_tool(request: Request):
    """Executa uma ferramenta via REST."""
    body = await request.json()
    tool_name = body.get("name")
    args = body.get("arguments", {})

    if tool_name != "resolve_issue":
        return {"error": f"Ferramenta '{tool_name}' não suportada"}

    # Valida argumentos
    agent_id = args.get("agent_id")
    problem_type = args.get("problem_type")
    description = args.get("description")
    if not agent_id or not problem_type or not description:
        return {"error": "Campos obrigatórios: agent_id, problem_type, description"}

    # Monta payload para a API /api/resolve
    payload = {
        "agent_id": agent_id,
        "secret": SECRET,
        "problem_type": problem_type,
        "description": description,
        "attachments": [],
        "order_id": args.get("order_id"),
        "max_cost": args.get("max_cost", 100)
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{PROXY_URL}/api/resolve",
                json=payload,
                timeout=30.0
            )
            result = resp.json()
            status = resp.status_code
        except Exception as e:
            result = {"error": str(e)}
            status = 500

    return {
        "status": status,
        "result": result
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)