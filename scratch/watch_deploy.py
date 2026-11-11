import json,urllib.request,time,sys
def env(k):
    for line in open('.env',encoding='utf-8',errors='ignore'):
        line=line.strip()
        if line.startswith(k+'='): return line.split('=',1)[1].strip().strip('"').strip("'")
    return ''
B='https://mangesh-nanopro.mangeshbagul15.workers.dev'
deadline=time.time()+900
while time.time()<deadline:
    try:
        req=urllib.request.Request(B+'/api/auth/login',data=json.dumps({'username':env('NANOPRO_ADMIN_USERNAME') or 'nanopro','password':env('NANOPRO_ADMIN_PASSWORD')}).encode(),method='POST')
        req.add_header('Content-Type','application/json'); req.add_header('User-Agent','NanoProAudit/1.0')
        with urllib.request.urlopen(req,timeout=45) as x: tok=json.loads(x.read().decode())['session_token']
        r=urllib.request.Request(B+'/'); r.add_header('User-Agent','NanoProAudit/1.0'); r.add_header('X-Session-Token',tok)
        with urllib.request.urlopen(r,timeout=45) as x: html=x.read().decode('utf-8','ignore')
        if 'X-Session-Token' in html:
            print('DEPLOYED', time.strftime('%H:%M:%S')); sys.exit(0)
        print('waiting', time.strftime('%H:%M:%S'), len(html)); sys.stdout.flush()
    except Exception as e:
        print('err',time.strftime('%H:%M:%S'),type(e).__name__); sys.stdout.flush()
    time.sleep(30)
print('TIMEOUT')
