# Odysseus no Render

Deploy automatizado do Odysseus (agente autônomo MCP) no Render.

## Variáveis de ambiente obrigatórias

| Key | Exemplo |
|-----|---------|
| `AUTH_SECRET_KEY` | `gerar_string_aleatoria` |
| `OPENROUTER_API_KEY` | `sk-...` |

## Como usar

1. Crie um Web Service no Render com este repositório.
2. Defina as variáveis acima.
3. Acesse a URL do serviço e crie o usuário admin.
4. Em Settings → MCP Servers, adicione seu servidor MCP.

## Manutenção

Use cron-job.org para pingar `/health` a cada 5 minutos e evitar hibernação.
