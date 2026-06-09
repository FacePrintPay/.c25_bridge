#!/usr/bin/env python3
"""
C25 Bridge • Fixed Version • Port Conflict Resolver
"""
import json, subprocess, os, sys, time, socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path

# Configuration with port conflict detection
def find_free_port(start_port=8080):
    """Find first available port starting from start_port"""
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("localhost", port))
                return port
            except OSError:
                port += 1
                if port > 8100:  # Don't search forever
                    raise OSError("No free ports in range 8080-8100")

PORT = find_free_port(8080)
print(f"🔗 Bridge using port: {PORT}")

# Your existing agent paths
AGENT_PATHS = {
    'pathos': Path.home() / 'PaTHos' / 'pathos_router.py',
    'earth': Path.home() / 'planetary_agents' / 'earth_agent.py',
    'mars': Path.home() / 'sovereign_gtp' / 'mars_deploy.py',
    # ... add all 25 agents
}

class C25Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Silent logging
        
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_GET(self):
        if self.path == '/health':
            self._send_json({
                'status': 'healthy',
                'port': PORT,
                'timestamp': time.time(),
                'agents_online': sum(1 for p in AGENT_PATHS.values() if p.exists())
            })
        else:
            self._send_json({'error': 'Not found'}, 404)
    
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len).decode() if content_len > 0 else '{}'
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self._send_json({'error': 'Invalid JSON'}, 400)
            return
        
        if self.path == '/api/chat':
            agent = data.get('agent', 'pathos')
            prompt = data.get('prompt', '')
            
            if agent not in AGENT_PATHS:
                self._send_json({'error': f'Agent not found: {agent}'}, 404)
                return
            
            script_path = AGENT_PATHS[agent]
            if not script_path.exists():
                self._send_json({'error': f'Script not found: {script_path}'}, 404)
                return
            
            # Execute agent script
            try:
                result = subprocess.run([
                    sys.executable, str(script_path),
                    '--prompt', prompt,
                    '--agent', agent,
                    '--format', 'json'
                ], capture_output=True, text=True, timeout=120, cwd=script_path.parent)
                
                self._send_json({
                    'success': result.returncode == 0,
                    'agent': agent,
                    'prompt': prompt,
                    'response': result.stdout.strip(),
                    'error': result.stderr.strip() if result.returncode != 0 else None,
                    'exit_code': result.returncode
                })
                
            except subprocess.TimeoutExpired:
                self._send_json({
                    'success': False,
                    'error': 'Agent timeout after 120s',
                    'response': '⏱️ Agent processing timeout'
                }, 500)
            except Exception as e:
                self._send_json({
                    'success': False,
                    'error': str(e),
                    'response': f'❌ Agent error: {str(e)}'
                }, 500)
        
        else:
            self._send_json({'error': 'Not found'}, 404)

def run_server():
    server = HTTPServer(('0.0.0.0', PORT), C25Handler)
    print(f"🚀 C25 Bridge running on http://localhost:{PORT}")
    print(f"   Health: GET /health")
    print(f"   Chat: POST /api/chat")
    server.serve_forever()

if __name__ == '__main__':
    run_server()
