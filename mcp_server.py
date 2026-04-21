# A simple mock MCP server
import sys
import json

def process_message(msg):
    # Just a mock response
    if msg.get("method") == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "playwright-mock",
                    "version": "1.0.0"
                }
            }
        }
    elif msg.get("method") == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg.get("id"),
            "result": {
                "tools": [
                    {
                        "name": "playwright_capture",
                        "description": "Captures a screenshot and HTML structure of a webpage",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "url": {"type": "string"}
                            },
                            "required": ["url"]
                        }
                    }
                ]
            }
        }
    return None

if __name__ == "__main__":
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            msg = json.loads(line)
            resp = process_message(msg)
            if resp:
                print(json.dumps(resp), flush=True)
        except Exception:
            pass
