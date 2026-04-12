FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml .
COPY maxkb_mcp/ maxkb_mcp/

RUN pip install --no-cache-dir .

EXPOSE 8000

ENV MCP_TRANSPORT=sse
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

CMD ["maxkb-mcp"]
