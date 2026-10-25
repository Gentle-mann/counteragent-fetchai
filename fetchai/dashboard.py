"""Read-only, loopback-only observability server. Never exposes role-private memory."""
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from memory import CaseMemory

ROOT = Path(__file__).parent
store = CaseMemory(ROOT / '.runtime' / 'cases.sqlite3')

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/events':
            snapshot = store.snapshot()
            from closing_view import closing_receipt
            closings=[]
            for path in sorted((ROOT/'.runtime').glob('*-audit.json')):
                try:
                    record=json.loads(path.read_text(encoding='utf-8'))
                    if not any(e.get('mode')=='live_model' for e in record['events']):continue
                    receipt=closing_receipt(record['state'],record['events'])
                    if receipt:closings.append(receipt)
                except (ValueError,KeyError,TypeError,OSError):continue
            result_path=ROOT / '.runtime' / 'scenario-results.json'
            scenarios=json.loads(result_path.read_text(encoding='utf-8')) if result_path.exists() else []
            body = json.dumps({'events': [e for e in snapshot['events'] if e.get('mode') == 'live_model'],
                'scenarios':scenarios,'closings':closings,
                'case_stats': [{'deal':m['deal'],'role':m['role'],'memory_steps':len(m['steps'])} for m in snapshot['memories']]}).encode()
            content_type = 'application/json'
        elif self.path in ('/', '/index.html'):
            body = (ROOT / 'dashboard.html').read_bytes()
            content_type = 'text/html; charset=utf-8'
        elif self.path in ('/dashboard.js','/dashboard.css'):
            body=(ROOT / self.path[1:]).read_bytes()
            content_type='application/javascript' if self.path.endswith('.js') else 'text/css'
        elif re.fullmatch(r'/documents/[0-9a-f]{12}/[0-9]{1,3}/[0-9a-f]{12}',self.path):
            _,_,deal,revision,hashed=self.path.split('/')
            path=ROOT/'.runtime'/'contracts'/(deal+'-r'+revision+'-'+hashed+'.json')
            if not path.is_file():
                self.send_error(404)
                return
            packet=json.loads(path.read_text(encoding='utf-8'))
            from contracts import verify_signature
            checks={r:verify_signature(packet['bundle'],s,s.get('signer_address',''),r) for r,s in packet['signatures'].items()}
            escape=__import__('html').escape
            body=('<!doctype html><meta charset="utf-8"><title>CounterAgent signed documents</title>'
                '<style>body{font:16px system-ui;max-width:1000px;margin:40px auto;padding:24px;background:#101820;color:#eee}pre{white-space:pre-wrap;overflow-wrap:anywhere}h1{font-size:28px}</style>'
                '<h1>CounterAgent agreement bundle</h1><p>Fictional demo documents. Agent signatures prove integrity; they do not establish legal corporate authority.</p>'
                '<h2>Signature verification</h2><pre>'+escape(json.dumps(checks,indent=2))+'</pre><h2>Order form · MSA · DPA · implementation SOW</h2><pre>'
                +escape(json.dumps(packet,indent=2))+'</pre>').encode()
            content_type='text/html; charset=utf-8'
        elif re.fullmatch(r'/t/[0-9a-f]{12}', self.path):
            path = ROOT / '.runtime' / (self.path.rsplit('/', 1)[-1] + '.json')
            if not path.is_file():
                self.send_error(404)
                return
            manifest = json.loads(path.read_text(encoding='utf-8'))
            body = ('<!doctype html><meta charset="utf-8"><title>CounterAgent local workspace</title>'
                '<style>body{font:18px system-ui;background:#101820;color:#e9f0ee;padding:48px}pre{line-height:1.8}</style>'
                '<h1>Demo workspace provisioned</h1><p>Local resource only. No vendor SaaS tenant was created.</p><pre>'
                + __import__('html').escape(json.dumps(manifest, indent=2)) + '</pre>').encode()
            content_type = 'text/html; charset=utf-8'
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass

if __name__ == '__main__':
    print('CounterAgent graph: http://127.0.0.1:8060', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8060), Handler).serve_forever()
