#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os, sys, subprocess, time
from pathlib import Path
from urllib.parse import urlparse, parse_qs

HOME = Path(os.environ.get('HOME', '/data/data/com.termux/files/home'))
LOG = HOME / '.c25_bridge.log'

def log(m): 
    with open(LOG, 'a') as f: f.write(f"[{time.strftime('%H:%M:%S')}] {m}\n")

class Handler(BaseHTTPRequestHandler):
    def _json(self, d, s=200):
        self.send_response(s); self.send_header('Content-Type', 'application/json'); self.send_header('Access-Control-Allow-Origin', '*'); self.end_headers()
        self.wfile.write(json.dumps(d).encode())
    def do_OPTIONS(self): self.send_response(200); self.send_header('Access-Control-Allow-Origin', '*'); self.send_header('Access-Control-Allow-Methods', 'GET, POST'); self.send_header('Access-Control-Allow-Headers', 'Content-Type'); self.end_headers()
    def do_GET(self):
        p = urlparse(self.path).path
        if p == '/health': self._json({'status': 'ok', 'time': time.time()})
        elif p == '/api/projects': self._json([{'name': 'VideoCourts', 'desc': 'Judicial AI', 'icon': '⚖️'}, {'name': 'SovereignGTP', 'desc': 'Agent center', 'icon': '🧠'}])
        elif p == '/api/agents': self._json([{'name': 'Earth', 'role': 'Data', 'status': 'online'}, {'name': 'Mars', 'role': 'Deploy', 'status': 'busy'}])
        elif p == '/api/activity': self._json([{'time': 'NOW', 'msg': '✅ System ready', 'type': 'ok'}])
        else: self._json({'error': 'Not found'}, 404)
    def do_POST(self):
        p = urlparse(self.path).path; cl = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(cl).decode() if cl > 0 else '{}'; data = json.loads(body) if body else {}
        if p == '/api/chat':
            prompt, agent = data.get('prompt', ''), data.get('agent', 'pathos')
            log(f"CHAT: {agent} <- {prompt[:50]}")
            # Mock response (replace with real agent call)
            resp = f"🪐 {agent.upper()} received: {prompt[:50]}... *(local mock)*"
            self._json({'success': True, 'response': resp, 'agent': agent})
        elif p == '/api/deploy':
            proj, tgt = data.get('project', 'test'), data.get('target', 'vercel')
            log(f"DEPLOY: {proj} -> {tgt}")
            self._json({'success': True, 'message': f'{proj} queued for {tgt}', 'url': f'https://{proj}-{time.time()}.vercel.app'})
        else: self._json({'error': 'Not found'}, 404)
    def log_message(self, fmt, *args): pass

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3100
    server = HTTPServer(('0.0.0.0', port), Handler)
    log(f"Bridge running on port {port}")
    print(f"🔗 Backend Bridge: http://0.0.0.0:{port}")
    server.serve_forever()
