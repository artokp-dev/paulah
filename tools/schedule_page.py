"""의료진 진료일정 페이지(/schedule/) 부품 — tools/build.py 가 불러 씁니다.

매달 할 일 (자세한 순서는 CLAUDE.md '의료진 진료일정' 참고)
  1) 원장님이 승인한 일정을 tools/schedule/YYYY-MM.csv 로 저장
     (구글 시트에서 바로 만들 때: python3 tools/schedule/from_sheet.py 받은파일.xlsx 2026 12)
  2) (선택) 따로 만든 일정 이미지 4장을 tools/schedule/images/YYYY-MM/1.png ~ 4.png 로 넣기
     1=김평 원장, 2=김율현 원장, 3=김세림 내과 과장, 4=김종완 수의사
     넣지 않으면 CSV로 이미지 4장을 자동으로 만든다.
  3) python3 tools/build.py

CSV 형식
  # 로 시작하는 줄은 메모(화면에 안 나옴)
  안내: 로 시작하는 줄은 그 달 일정 위에 안내문으로 표시
  날짜,김평,김율현,김세림,김종완
  1,오전,오전,휴무,오후          ← 값은 오전 / 오후 / 휴무 셋 중 하나
  그 달 1일부터 말일까지 하루도 빠짐없이 있어야 빌드된다 (빈 날을 임의로 채우지 않기 위해).
"""
import calendar
import datetime
import hashlib
import html
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'tools' / 'schedule'
IMG_SRC = SRC / 'images'
SITE = ROOT / 'site'
IMG_OUT = SITE / 'schedule' / 'img'
CACHE = SRC / '.image-hash.json'

# 표시 순서 = 이미지 번호 순서
VETS = [
    ('kim-pyeong', '김평', '원장'),
    ('kim-yulhyun', '김율현', '원장'),
    ('kim-serim', '김세림', '내과 과장'),
    ('kim-jongwan', '김종완', '수의사'),
]
STATUS = {'오전': 'am', '오후': 'pm', '휴무': 'off'}
WD = '월화수목금토일'          # date.weekday(): 0=월
HEAD = ['날짜'] + [n for _, n, _ in VETS]
e = html.escape


class ScheduleError(SystemExit):
    pass


def load_months():
    months = []
    for f in sorted(SRC.glob('[0-9][0-9][0-9][0-9]-[0-9][0-9].csv')):
        y, m = map(int, f.stem.split('-'))
        days = calendar.monthrange(y, m)[1]
        rows, notice, header = {}, [], None
        for no, line in enumerate(f.read_text(encoding='utf-8-sig').splitlines(), 1):
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            if s.startswith('안내:'):
                notice.append(s[3:].strip())
                continue
            cells = [c.strip() for c in s.split(',')]
            if header is None:
                header = cells
                if header != HEAD:
                    raise ScheduleError(f'{f.name}: 첫 줄은 "{",".join(HEAD)}" 이어야 합니다. (지금: {s})')
                continue
            try:
                d = int(cells[0].rstrip('일'))
            except ValueError:
                raise ScheduleError(f'{f.name} {no}번째 줄: 날짜를 읽을 수 없습니다 → {s}')
            vals = cells[1:]
            if len(vals) != len(VETS) or any(v not in STATUS for v in vals):
                raise ScheduleError(f'{f.name} {no}번째 줄: 값은 오전/오후/휴무 4칸이어야 합니다 → {s}')
            if not 1 <= d <= days or d in rows:
                raise ScheduleError(f'{f.name} {no}번째 줄: 날짜 {d}일이 잘못됐거나 두 번 있습니다.')
            rows[d] = vals
        missing = [d for d in range(1, days + 1) if d not in rows]
        if missing:
            raise ScheduleError(f'{f.name}: 빠진 날짜가 있습니다 {missing} — 임의로 채우지 말고 확정 일정을 받아 넣어 주세요.')
        months.append({'key': f.stem, 'y': y, 'm': m, 'days': days, 'rows': rows, 'notice': notice, 'src': f})
    return months


def updated_date():
    """일정 자료(CSV)가 마지막으로 바뀐 날"""
    files = [str(p) for p in SRC.glob('*.csv')]
    if not files:
        return datetime.date.today().isoformat()
    dirty = subprocess.run(['git', 'status', '--porcelain', '--', *files], cwd=ROOT,
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        return datetime.date.today().isoformat()
    r = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', *files], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() or datetime.date.today().isoformat()


# ───────────────────────── 페이지 HTML ─────────────────────────

def chip(v):
    return f'<span class="sc-c {STATUS[v]}">{v}</span>'


def dclass(y, m, d):
    wd = datetime.date(y, m, d).weekday()
    return ' sun' if wd == 6 else (' sat' if wd == 5 else '')


def month_html(mo, imgs):
    y, m, key = mo['y'], mo['m'], mo['key']
    th = ''.join(f'<th scope="col">{n}<small>{t}</small></th>' for _, n, t in VETS)
    trs = []
    for d in range(1, mo['days'] + 1):
        wd = WD[datetime.date(y, m, d).weekday()]
        tds = ''.join(f'<td>{chip(v)}</td>' for v in mo['rows'][d])
        trs.append(f'<tr data-d="{key}-{d:02d}" class="r{dclass(y, m, d)}"><th scope="row"><b>{d}</b><span>{wd}</span></th>{tds}</tr>')
    notice = ''.join(f'<p class="sc-notice">{e(n)}</p>' for n in mo['notice'])

    first_wd = (datetime.date(y, m, 1).weekday() + 1) % 7      # 일요일 시작 달력
    heads = ''.join(f'<span class="h{" sun" if i == 0 else " sat" if i == 6 else ""}">{w}</span>'
                    for i, w in enumerate('일월화수목금토'))
    vets = []
    for i, (slug, name, title) in enumerate(VETS):
        cells = ['<span class="b"></span>'] * first_wd
        for d in range(1, mo['days'] + 1):
            v = mo['rows'][d][i]
            cells.append(f'<span class="c {STATUS[v]}{dclass(y, m, d)}" data-d="{key}-{d:02d}"><b>{d}</b>{chip(v)}</span>')
        vets.append(f'''      <div class="sc-vet" data-v="{slug}" hidden>
        <p class="sc-vt">{name} <small>{title}</small> · {m}월</p>
        <div class="sc-cal" aria-label="{name} {title} {m}월 진료일정">{heads}{"".join(cells)}</div>
      </div>''')

    gallery = ''
    if imgs:
        cards = ''.join(
            f'<a href="img/{fn}" target="_blank" rel="noopener" class="sc-img"><img loading="lazy" decoding="async" '
            f'src="img/{fn}" width="1080" height="1350" alt="{y}년 {m}월 {name} {title} 진료일정표"><span>{name} {title}</span></a>'
            for fn, (_, name, title) in zip(imgs, VETS))
        gallery = f'''      <details class="sc-imgs">
        <summary>{m}월 일정표 이미지로 보기 <small>저장·공유용 4장</small></summary>
        <p class="sp-note">이미지를 누르면 크게 열립니다. 휴대폰에서는 이미지를 길게 눌러 저장할 수 있습니다.</p>
        <div class="sc-gal">{cards}</div>
      </details>'''

    return f'''    <div class="sc-month" data-m="{key}" id="m-{key}">
      <h2 class="sc-mt">{y}년 {m}월 진료일정</h2>
{notice}      <div class="sc-all">
        <table class="sc-table">
          <caption class="sr">{y}년 {m}월 날짜별 의료진 진료일정 (오전·오후·휴무)</caption>
          <thead><tr><th scope="col">날짜</th>{th}</tr></thead>
          <tbody>
{chr(10).join("            " + t for t in trs)}
          </tbody>
        </table>
      </div>
{chr(10).join(vets)}
{gallery}
    </div>'''


def render(months, image_files):
    tabs = ''.join(f'<button type="button" class="sc-tab" data-m="{mo["key"]}" hidden><b>{mo["m"]}월</b><span></span></button>'
                   for mo in months)
    vet_btns = '<button type="button" class="sc-vb on" data-v="all" aria-pressed="true">전체</button>' + ''.join(
        f'<button type="button" class="sc-vb" data-v="{s}" aria-pressed="false">{n}<small>{t}</small></button>'
        for s, n, t in VETS)
    body = '\n'.join(month_html(mo, image_files.get(mo['key'], [])) for mo in months)
    data = {mo['key']: [mo['rows'][d] for d in range(1, mo['days'] + 1)] for mo in months}
    vets = [[n, t] for _, n, t in VETS]
    return f'''<section class="sp-sec sc" id="schedule">
  <div class="sc-today" id="scToday" hidden></div>
  <div class="sc-empty" id="scEmpty" hidden>
    <p><b id="scEmptyM"></b> 진료일정은 확정되는 대로 이곳에 올라옵니다.</p>
    <p>특정 수의사 진료를 원하시면 <a href="tel:031-717-7558">031-717-7558</a>로 문의해 주세요. 24시간 수의사가 상주합니다.</p>
  </div>
  <div class="sc-bar">
    <div class="sc-tabs" id="scTabs" role="group" aria-label="월 선택">{tabs}</div>
    <div class="sc-vbs" id="scVets" role="group" aria-label="수의사 선택">{vet_btns}</div>
  </div>
  <div class="sc-legend"><span><span class="sc-c am">오전</span>오전부터 진료</span><span><span class="sc-c pm">오후</span>오후부터 진료</span><span><span class="sc-c off">휴무</span>휴무</span></div>
{body}
  <p class="sc-next" id="scNext" hidden></p>
  <p class="sc-pastw"><button type="button" class="sc-past" id="scPast" hidden>지난 일정 보기</button></p>
  <script type="application/json" id="scData">{json.dumps({"vets": vets, "months": data}, ensure_ascii=False, separators=(",", ":"))}</script>
</section>'''


# ───────────────────────── 일정 이미지 4장 ─────────────────────────

def _img_html(mo, i, logo_uri):
    y, m = mo['y'], mo['m']
    _, name, title = VETS[i]
    first_wd = (datetime.date(y, m, 1).weekday() + 1) % 7
    cells = ['<div class="b"></div>'] * first_wd
    for d in range(1, mo['days'] + 1):
        v = mo['rows'][d][i]
        cells.append(f'<div class="c {STATUS[v]}{dclass(y, m, d)}"><b>{d}</b><span>{v}</span></div>')
    while len(cells) % 7:
        cells.append('<div class="b"></div>')
    rows = len(cells) // 7
    heads = ''.join(f'<div class="h{" sun" if k == 0 else " sat" if k == 6 else ""}">{w}</div>'
                    for k, w in enumerate('일월화수목금토'))
    en = datetime.date(y, m, 1).strftime('%B').upper()
    cell_h = 136 if rows <= 5 else 113
    return f'''<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{width:1080px;height:1350px;font-family:"Noto Sans CJK KR","Noto Sans KR",sans-serif;background:#f7f6f3;color:#0f2045;}}
.top{{height:300px;background:#021a43;color:#fff;padding:56px 72px 0;position:relative;overflow:hidden;}}
.top::after{{content:"";position:absolute;left:0;right:0;bottom:0;height:6px;background:#c8a96e;}}
.brand{{display:flex;align-items:center;gap:16px;font-size:27px;font-weight:700;letter-spacing:-0.01em;}}
.brand img{{width:72px;height:72px;border-radius:14px;border:1.5px solid rgba(200,169,110,0.45);}}
.brand small{{display:block;font-size:15px;font-weight:500;letter-spacing:0.16em;color:#dfc08a;margin-top:2px;}}
.mo{{position:absolute;left:72px;bottom:44px;display:flex;align-items:flex-end;gap:22px;}}
.mo b{{font-family:"Noto Serif CJK KR",serif;font-size:132px;line-height:0.8;font-weight:700;}}
.mo span{{font-size:22px;line-height:1.35;color:rgba(255,255,255,0.78);padding-bottom:4px;}}
.mo span em{{font-style:normal;display:block;font-size:30px;font-weight:700;color:#fff;}}
.who{{position:absolute;right:72px;bottom:50px;text-align:right;}}
.who b{{display:block;font-family:"Noto Serif CJK KR",serif;font-size:50px;font-weight:700;line-height:1.1;}}
.who b small{{font-family:"Noto Sans CJK KR",sans-serif;font-size:30px;font-weight:700;color:#dfc08a;margin-left:12px;}}
.who span{{display:block;font-size:21px;color:rgba(255,255,255,0.7);margin-top:12px;}}
.cal{{padding:38px 64px 0;}}
.grid{{display:grid;grid-template-columns:repeat(7,1fr);gap:10px;}}
.h{{text-align:center;font-size:23px;font-weight:700;color:#464660;padding-bottom:4px;}}
.h.sun{{color:#c0392b;}} .h.sat{{color:#1e3a7a;}}
.c{{height:{cell_h}px;border-radius:16px;background:#fff;border:2px solid rgba(26,58,107,0.12);display:flex;flex-direction:column;justify-content:space-between;padding:12px 12px 16px;}}
.c b{{font-size:24px;font-weight:700;color:#18182a;text-align:right;}}
.c.sun b{{color:#c0392b;}} .c.sat b{{color:#1e3a7a;}}
.c span{{align-self:center;font-size:28px;font-weight:700;letter-spacing:0.02em;}}
.c.am span{{color:#1e3a7a;}}
.c.pm{{background:#fbf5e9;border-color:rgba(200,169,110,0.55);}}
.c.pm span{{color:#7d5a12;}}
.c.off{{background:#e2e3e8;border-color:#e2e3e8;}}
.c.off b{{color:#8a8b96;}}
.c.off span{{background:#7c7e8a;color:#fff;font-size:23px;padding:4px 18px;border-radius:30px;}}
.leg{{display:flex;gap:26px;align-items:center;justify-content:center;margin-top:26px;font-size:21px;color:#464660;}}
.leg i{{display:inline-block;width:22px;height:22px;border-radius:6px;vertical-align:-3px;margin-right:8px;border:2px solid rgba(26,58,107,0.15);background:#fff;}}
.leg i.pm{{background:#fbf5e9;border-color:rgba(200,169,110,0.55);}} .leg i.off{{background:#7c7e8a;border-color:#7c7e8a;}}
.foot{{position:absolute;left:64px;right:64px;bottom:44px;display:flex;justify-content:space-between;align-items:center;border-top:2px solid rgba(26,58,107,0.12);padding-top:24px;font-size:21px;color:#464660;}}
.foot b{{font-size:30px;color:#0f2045;letter-spacing:0.02em;}}
.foot span{{text-align:right;line-height:1.5;}}
</style></head><body>
<div class="top">
  <div class="brand"><img src="{logo_uri}" alt=""><div>24시 폴 동물병원<small>PAUL ANIMAL HOSPITAL</small></div></div>
  <div class="mo"><b>{m}</b><span><em>{y}</em>{en}</span></div>
  <div class="who"><b>{name}<small>{title}</small></b><span>{m}월 진료일정</span></div>
</div>
<div class="cal"><div class="grid">{heads}{"".join(cells)}</div>
<div class="leg"><span><i></i>오전부터 진료</span><span><i class="pm"></i>오후부터 진료</span><span><i class="off"></i>휴무</span></div></div>
<div class="foot"><b>031-717-7558</b><span>일정은 바뀔 수 있으니 내원 전 확인해 주세요<br>paulah.co.kr/schedule · 365일 24시간 수의사 상주</span></div>
</body></html>'''


def _hash(mo, i):
    raw = json.dumps([mo['key'], i, [mo['rows'][d][i] for d in range(1, mo['days'] + 1)]], ensure_ascii=False)
    import inspect                     # 이미지 틀(_img_html)이 바뀔 때만 다시 그림
    tpl = hashlib.md5(inspect.getsource(_img_html).encode()).hexdigest()[:8]
    return hashlib.md5((raw + tpl).encode()).hexdigest()[:12]


def build_images(months):
    """월별 이미지 4장: tools/schedule/images/YYYY-MM/1~4.(png|jpg|webp) 가 있으면 그것을, 없으면 CSV로 자동 생성"""
    from PIL import Image
    IMG_OUT.mkdir(parents=True, exist_ok=True)
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    out, todo = {}, []
    for mo in months:
        names = []
        for i in range(len(VETS)):
            fn = f'{mo["key"]}-{i + 1}.webp'
            dst = IMG_OUT / fn
            given = [p for ext in ('png', 'jpg', 'jpeg', 'webp') for p in [IMG_SRC / mo['key'] / f'{i + 1}.{ext}'] if p.exists()]
            if given:
                h = 'given:' + hashlib.md5(given[0].read_bytes()).hexdigest()[:12]
                if cache.get(fn) != h or not dst.exists():
                    im = Image.open(given[0]).convert('RGB')
                    if im.width > 1080:
                        im = im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS)
                    im.save(dst, 'WEBP', quality=88, method=6)
                    cache[fn] = h
            else:
                h = 'auto:' + _hash(mo, i)
                if cache.get(fn) != h or not dst.exists():
                    todo.append((mo, i, dst, fn, h))
            names.append(fn)
        out[mo['key']] = names
    if todo:
        import base64
        import io
        from playwright.sync_api import sync_playwright
        logo = 'data:image/jpeg;base64,' + base64.b64encode((SITE / 'images' / 'logo-footer.jpg').read_bytes()).decode()
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={'width': 1080, 'height': 1350})
            for mo, i, dst, fn, h in todo:
                pg.set_content(_img_html(mo, i, logo))
                pg.wait_for_timeout(150)
                png = pg.screenshot(clip={'x': 0, 'y': 0, 'width': 1080, 'height': 1350})
                Image.open(io.BytesIO(png)).convert('RGB').save(dst, 'WEBP', quality=88, method=6)
                cache[fn] = h
                print(f'  일정 이미지 생성: site/schedule/img/{fn}')
            b.close()
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1, sort_keys=True) + '\n')
    return out


def build():
    """build.py 가 부르는 입구: (일정 HTML 블록, 갱신일)"""
    months = load_months()
    imgs = build_images(months)
    return render(months, imgs), updated_date()
