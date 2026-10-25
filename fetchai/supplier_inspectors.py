"""Loopback inspector adapters for SDK Bureaus with multiple public agents.

Agentverse's inspector omits the address header required by a multi-agent Bureau.
Each fixed-port adapter adds only that agent's public address. No token is logged.
"""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import threading
import httpx

ADDRESSES={8002:'agent1qwjkyr27kdushevtgze080vyvuv90x6mfzkukrts7kcpctz0lpc97s05lmz',
    8003:'agent1qt52xqnav5p03n6w9ymgryppt8fhug7k7qaycemhzyy0awmgpuylgvvdack'}

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_OPTIONS(self):
        self.send_response(204);self.cors();self.end_headers()
    def cors(self):
        self.send_header('Access-Control-Allow-Origin','https://agentverse.ai')
        self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type, x-uagents-address')
        self.send_header('Access-Control-Allow-Private-Network','true')
    def forward(self):
        if self.path.split('?')[0] not in ('/agent_info','/messages','/connect','/disconnect'):
            self.send_error(404);return
        length=int(self.headers.get('Content-Length','0'))
        if length>65536:self.send_error(413);return
        try:
            response=httpx.request(self.command,'http://127.0.0.1:8001'+self.path,
                content=self.rfile.read(length) if length else None,
                headers={'Content-Type':'application/json','x-uagents-address':ADDRESSES[self.server.server_port]},timeout=25)
            self.send_response(response.status_code);self.cors()
            self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(response.content)
        except (httpx.HTTPError,OSError):self.send_error(502)
    do_GET=forward
    do_POST=forward

if __name__=='__main__':
    for port in ADDRESSES:
        threading.Thread(target=ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever,daemon=True).start()
    print('Supplier inspectors: Beacon 8002, Quickdash 8003 (loopback only)',flush=True)
    threading.Event().wait()
