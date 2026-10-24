"""사이트 렌더 검증: JS 에러 0, 깨진 이미지 0, 내부 링크 404 0.

사용법: python3 tools/check.py [출력폴더] [페이지...]
  site/ 폴더를 로컬 서버로 띄우고 Playwright(Chromium)로 각 페이지를 연다.
  데스크톱(1440)·모바일(390) 전체 스크린샷을 출력폴더에 저장한다.
"""
import http.server, threading, functools, sys, os, re
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site')
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/paulah-check'
PAGES = sys.argv[2:] or ['/']
os.makedirs(OUT, exist_ok=True)

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f'http://127.0.0.1:{srv.server_address[1]}'

REVEAL = '.rev,[class*=rev]{opacity:1!important;transform:none!important} html{scroll-behavior:auto!important}'
problems = 0
with sync_playwright() as p:
    b = p.chromium.launch()
    for vw, vh, tag in [(1440, 900, 'desktop'), (390, 844, 'mobile')]:
        ctx = b.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=1)
        for path in PAGES:
            pg = ctx.new_page()
            errs, bad = [], []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
            pg.on('response', lambda r: bad.append(f'{r.status} {r.url}') if r.status >= 400 and r.url.startswith(BASE) else None)
            pg.goto(BASE + path, wait_until='networkidle')
            pg.add_style_tag(content=REVEAL)
            # 접힌 <details>·숨은 달(진료일정)의 lazy 이미지도 실제로 불러와 확인
            pg.evaluate('document.querySelectorAll("details").forEach(d=>d.open=true);document.querySelectorAll("img[loading=lazy]").forEach(i=>i.loading="eager")')
            pg.evaluate('''async()=>{for(let y=0;y<document.body.scrollHeight;y+=600){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,60));}}''')
            pg.wait_for_timeout(500)
            pg.evaluate('window.scrollTo(0, 0)')
            pg.wait_for_timeout(300)
            broken = pg.evaluate('[...document.images].filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.getAttribute("src"))')
            # 내부 링크 확인
            links = pg.evaluate('[...document.querySelectorAll("a[href]")].map(a=>a.getAttribute("href"))')
            dead = []
            if tag == 'desktop':
                for h in set(links):
                    if h.startswith(('http', 'tel:', 'mailto:', 'javascript:')):
                        continue
                    u = urljoin(BASE + path, h)
                    frag = urlparse(u).fragment
                    target = u.split('#')[0]
                    r = ctx.request.get(target)
                    if r.status >= 400:
                        dead.append(f'{h} -> {r.status}')
                    elif frag:
                        body = r.text()
                        if f'id="{frag}"' not in body:
                            dead.append(f'{h} -> #{frag} 없음')
            ow = pg.evaluate('document.documentElement.scrollWidth')
            name = (path.strip('/').replace('/', '_') or 'index') + f'_{tag}.png'
            pg.screenshot(path=os.path.join(OUT, name), full_page=True)
            status = 'OK'
            # 샌드박스에서 Google Fonts 접속이 막혀 생기는 오류는 제외
            errs = [e for e in errs if 'ERR_TUNNEL_CONNECTION_FAILED' not in e and 'ERR_NAME_NOT_RESOLVED' not in e]  # 외부(구글폰트·네이버 wcslog) 차단
            issues = errs + bad + [f'깨진 이미지 {x}' for x in broken] + [f'죽은 링크 {x}' for x in dead]
            if ow > vw + 1:
                issues.append(f'가로 스크롤 발생 (scrollWidth {ow} > {vw})')
            if issues:
                status = 'PROBLEM'
                problems += len(issues)
            print(f'[{tag}] {path}: {status}')
            for i in issues:
                print('   -', i)
            pg.close()
        ctx.close()
    b.close()
srv.shutdown()
print('TOTAL PROBLEMS:', problems)
sys.exit(1 if problems else 0)
