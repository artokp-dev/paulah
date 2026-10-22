"""진료 안내 페이지 생성기.

  python3 tools/build.py

하는 일
  1) site/index.html 의 <style> 블록들을 그대로 모아 site/assets/base.css 로 저장
     (메인 페이지 디자인을 안내 페이지에서도 똑같이 쓰기 위한 복사본)
  2) tools/pages/<slug>.html 원고를 공통 틀(상단 메뉴·하단·구조화 데이터)에 끼워
     site/<slug>/index.html 로 저장

안내 페이지 문구를 고칠 때는 site/<slug>/index.html 이 아니라
tools/pages/<slug>.html 을 고친 뒤 이 스크립트를 다시 실행한다.
"""
import html
import json
import pathlib
import re
import datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
PAGES = ROOT / 'tools' / 'pages'
DOMAIN = 'https://paulah.co.kr'
TODAY = datetime.date.today().isoformat()
PUBLISHED = '2026-10-22'  # 진료 안내 페이지 최초 게시일
TODAY_KO = f'{int(TODAY[:4])}년 {int(TODAY[5:7])}월 {int(TODAY[8:])}일'
FONT = ('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900'
        '&family=Noto+Serif+KR:wght@400;600;700&display=swap')

# 진료 안내 페이지 목록 (하단 '다른 진료 안내'와 푸터 링크에 쓰임)
TOPICS = [
    ('checkup', '건강검진', 'i-checkup', '나이별 검진 주기 · 3단계 프로그램'),
    ('heart', '심장 · 노령동물 내과', 'i-heart', '심장초음파 · 만성질환 관리'),
    ('dental', '치과 · 스케일링', 'i-tooth', '스케일링 · 발치 · 치주 치료'),
    ('emergency', '24시 응급 · 오시는 길', 'i-emergency', '24시간 수의사 상주 · 위치 안내'),
]

CLINIC = {
    '@type': 'VeterinaryCare',
    '@id': f'{DOMAIN}/#clinic',
    'name': '24시 폴 동물병원',
    'url': f'{DOMAIN}/',
    'telephone': '+82-31-717-7558',
    'image': f'{DOMAIN}/og-image.jpg?v=2',
    'address': {
        '@type': 'PostalAddress',
        'streetAddress': '성남대로 385 분당클리닉빌딩 1층 102호',
        'addressLocality': '성남시 분당구',
        'addressRegion': '경기도',
        'addressCountry': 'KR',
    },
    'openingHoursSpecification': [{
        '@type': 'OpeningHoursSpecification',
        'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        'opens': '00:00', 'closes': '23:59',
    }],
}


def text_of(fragment):
    """HTML 조각 → 구조화 데이터용 평문"""
    t = re.sub(r'<br\s*/?>', ' ', fragment)
    t = re.sub(r'<[^>]+>', '', t)
    t = html.unescape(t)
    return re.sub(r'\s+', ' ', t).strip()


def faq_items(main_html):
    out = []
    for m in re.finditer(r'<details class="faq-item">\s*<summary>(.*?)</summary>\s*<div class="faq-a">(.*?)</div>\s*</details>',
                         main_html, re.S):
        q = text_of(m.group(1))
        a = text_of(m.group(2))
        out.append({'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}})
    return out


def build_css(index_html):
    styles = re.findall(r'<style[^>]*>(.*?)</style>', index_html, re.S)
    head = ('/* 자동 생성 파일 — 직접 고치지 마세요.\n'
            '   tools/build.py 가 index.html 의 <style> 블록을 그대로 복사해 만듭니다. */\n')
    (SITE / 'assets').mkdir(exist_ok=True)
    (SITE / 'assets' / 'base.css').write_text(head + '\n'.join(s.strip('\n') for s in styles) + '\n', encoding='utf-8')


def sprite_of(index_html):
    i = index_html.find('<svg width="0" height="0"')
    j = index_html.find('</svg>', i) + len('</svg>')
    return index_html[i:j]


NAV_ITEMS = [('#about', '병원 소개'), ('#doctors', '의료진'), ('#dept', '진료과목'), ('#checkup', '건강검진'),
             ('#equip', '시설·장비'), ('#blog', '블로그'), ('#faq', 'FAQ'), ('#contact', '오시는 길')]


def page_html(slug, meta, hero, main, sprite, ver):
    url = f'{DOMAIN}/{slug}/'
    faqs = faq_items(main)
    graph = [
        {
            '@type': 'WebPage', '@id': url + '#webpage', 'url': url,
            'name': meta['title'], 'description': meta['description'], 'inLanguage': 'ko-KR',
            'isPartOf': {'@type': 'WebSite', '@id': f'{DOMAIN}/#website', 'name': '24시 폴 동물병원', 'url': f'{DOMAIN}/'},
            'about': {'@id': f'{DOMAIN}/#clinic'},
            'primaryImageOfPage': {'@type': 'ImageObject', 'url': f'{DOMAIN}/og-image.jpg?v=2'},
            'datePublished': PUBLISHED,
            'dateModified': TODAY,
            'author': {'@id': f'{DOMAIN}/#clinic'},
            'publisher': {'@id': f'{DOMAIN}/#clinic'},
            'breadcrumb': {'@id': url + '#breadcrumb'},
        },
        {
            '@type': 'BreadcrumbList', '@id': url + '#breadcrumb',
            'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': '홈', 'item': f'{DOMAIN}/'},
                {'@type': 'ListItem', 'position': 2, 'name': meta['crumb'], 'item': url},
            ],
        },
        CLINIC,
    ]
    if faqs:
        graph.append({'@type': 'FAQPage', '@id': url + '#faq', 'mainEntity': faqs})
    jsonld = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False)

    nav_links = '\n'.join(f'    <li><a href="../{h}">{t}</a></li>' for h, t in NAV_ITEMS)
    mob_links = '\n'.join(f'    <li><a href="../{h}" onclick="closeMenu()">{"자주 묻는 질문" if t == "FAQ" else t}</a></li>'
                          for h, t in NAV_ITEMS)
    topic_cards = '\n'.join(
        f'      <a href="../{s}/" class="sp-topic{" on" if s == slug else ""}"><svg class="ic"><use href="#{ic}"></use></svg>'
        f'<b>{name}</b><span>{desc}</span></a>' for s, name, ic, desc in TOPICS)
    foot_topics = ' · '.join(f'<a href="../{s}/">{name}</a>' for s, name, _, _ in TOPICS)
    e = html.escape

    return f'''<!DOCTYPE html>
<html lang="ko"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(meta['title'])}</title>
<meta name="description" content="{e(meta['description'])}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{url}">
<link rel="icon" href="../favicon.ico?v=2" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="../favicon-32.png?v=2">
<link rel="icon" type="image/png" sizes="16x16" href="../favicon-16.png?v=2">
<link rel="apple-touch-icon" sizes="180x180" href="../apple-touch-icon.png?v=2">
<meta property="og:type" content="website">
<meta property="og:site_name" content="24시 폴 동물병원">
<meta property="og:locale" content="ko_KR">
<meta property="og:title" content="{e(meta['title'])}">
<meta property="og:description" content="{e(meta['description'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{DOMAIN}/og-image.jpg?v=2">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#021a43">
<script type="application/ld+json">{jsonld}</script>
<link href="{FONT}" rel="stylesheet">
<link rel="stylesheet" href="../assets/base.css?v={ver}">
<link rel="stylesheet" href="../assets/page.css?v={ver}">
<link rel="alternate" type="application/rss+xml" title="24시 폴 동물병원" href="{DOMAIN}/rss.xml">
</head>
<body>{sprite}

<!-- 이 파일은 tools/build.py 가 tools/pages/{slug}.html 로 만든 결과물입니다. 문구는 원고 파일에서 고치세요. -->
<nav id="topnav">
  <a href="../" class="nl">
    <div class="nlm-img" style="background:#0D1F3C;display:flex;align-items:center;justify-content:center;"><img src="../images/logo-nav.webp" alt="" style="width:100%;height:100%;object-fit:contain;"></div>
    <div><div class="nn">폴 동물병원</div><div class="ne">PAUL ANIMAL HOSPITAL</div></div>
  </a>
  <ul class="nls">
{nav_links}
  </ul>
  <div class="nr">
    <div class="lp"><div class="ld"></div><span>24시간 진료</span></div>
    <a href="tel:031-717-7558" class="nt"><svg class="ic"><use href="#i-phone"></use></svg> 031-717-7558</a>
  </div>
  <div id="hamburger" onclick="toggleMenu()"><span></span><span></span><span></span></div>
</nav>
<div class="mobile-menu" id="mobileMenu">
  <ul>
{mob_links}
    <li><a href="tel:031-717-7558" style="color:var(--gold);font-weight:700;"><svg class="ic"><use href="#i-phone"></use></svg> 031-717-7558</a></li>
  </ul>
</div>

<header class="sp-hero">
  <div class="sp-wrap">
    <div class="sp-crumb"><a href="../">24시 폴 동물병원</a><span>›</span><span>{e(meta['crumb'])}</span></div>
    <p class="ey">{e(meta['eyebrow'])}</p>
    <h1 class="sp-h1">{meta['h1']}</h1>
    <p class="sp-meta">작성 · 24시 폴 동물병원 수의사 &nbsp;|&nbsp; 최종 수정 <time datetime="{TODAY}">{TODAY_KO}</time></p>
{hero.strip()}
  </div>
</header>

<main class="sp-main">
  <div class="sp-wrap">
{main.strip()}

    <section class="sp-sec">
      <h2 class="sp-h2">다른 진료 안내</h2>
      <div class="sp-topics">
{topic_cards}
      </div>
    </section>
  </div>
</main>

<section class="sp-band">
  <h2>궁금한 점은 편하게 물어보세요</h2>
  <p>365일 24시간 진료 · 24시간 수의사 상주<br>경기도 성남시 분당구 성남대로 385 분당클리닉빌딩 1층 102호</p>
  <div class="sp-cta">
    <a href="tel:031-717-7558" class="bpg"><svg class="ic"><use href="#i-phone"></use></svg> 031-717-7558</a>
    <a href="https://pf.kakao.com/_xfkxekM/chat" target="_blank" rel="noopener" class="bkk"><svg class="ic"><use href="#i-chat"></use></svg> 카카오 상담</a>
    <a href="https://naver.me/xKyevLBK" target="_blank" rel="noopener" class="bnv"><b>N</b> 네이버 예약</a>
  </div>
</section>

<footer>
  <div class="flr">
    <div style="width:34px;height:34px;border-radius:8px;overflow:hidden;border:1px solid rgba(200,169,110,0.28);flex-shrink:0;">
      <img loading="lazy" decoding="async" src="../images/logo-footer.jpg?v=2" alt="폴 동물병원 로고" style="width:100%;height:100%;object-fit:cover;">
    </div>
    <div class="fln">폴 동물병원 · PAUL ANIMAL HOSPITAL</div>
  </div>
  <strong>24시 폴 동물병원 (Paul Animal Hospital)</strong><br>
  경기도 성남시 분당구 성남대로 385 분당클리닉빌딩 1층 102호 · TEL: <a href="tel:031-717-7558" style="color:inherit;font-weight:700;text-decoration:none;">031-717-7558</a><br>
  365일 24시간 진료 · 24시간 수의사 상주<br>
  <div class="ftopics">진료 안내: {foot_topics}</div>
  인스타그램: <a href="https://www.instagram.com/24paulah" target="_blank" rel="noopener" style="color:var(--gold);">@24paulah</a> · 블로그: <a href="https://blog.naver.com/hwrat" target="_blank" rel="noopener">blog.naver.com/hwrat</a><br><br>
  <span style="font-size:0.69rem;color:rgba(255,255,255,0.16);">© 2026 Paul Animal Hospital. All rights reserved.</span>
</footer>

<div class="floaters">
  <a href="https://pf.kakao.com/_xfkxekM/chat" target="_blank" rel="noopener" class="fb fk"><svg class="ic"><use href="#i-chat"></use></svg> 카카오 상담</a>
  <a href="tel:031-717-7558" class="fb ft2"><svg class="ic"><use href="#i-phone"></use></svg> 031-717-7558</a>
</div>

<script>
function toggleMenu(){{document.getElementById('mobileMenu').classList.toggle('open');}}
function closeMenu(){{document.getElementById('mobileMenu').classList.remove('open');}}
const nav=document.getElementById('topnav');
window.addEventListener('scroll',()=>{{nav.style.boxShadow=window.scrollY>60?'0 4px 32px rgba(0,0,0,0.12)':'none';}},{{passive:true}});
</script>
</body></html>
'''


def main():
    index_html = (SITE / 'index.html').read_text(encoding='utf-8')
    build_css(index_html)
    sprite = sprite_of(index_html)
    # CSS 내용이 바뀔 때만 버전이 바뀌도록 (브라우저 캐시 갱신용)
    import hashlib
    css_bytes = (SITE / 'assets' / 'base.css').read_bytes() + (SITE / 'assets' / 'page.css').read_bytes()
    ver = hashlib.md5(css_bytes).hexdigest()[:8]
    built = []
    for f in sorted(PAGES.glob('*.html')):
        src = f.read_text(encoding='utf-8')
        meta = json.loads(re.search(r'<!--META(.*?)META-->', src, re.S).group(1))
        hero = src.split('<!--HERO-->', 1)[1].split('<!--MAIN-->', 1)[0]
        main_html = src.split('<!--MAIN-->', 1)[1]
        slug = f.stem
        out = SITE / slug / 'index.html'
        out.parent.mkdir(exist_ok=True)
        out.write_text(page_html(slug, meta, hero, main_html, sprite, ver), encoding='utf-8')
        built.append((slug, len(faq_items(main_html)), len(meta['title']), len(meta['description'])))
    write_rss(index_html)
    for slug, nfaq, lt, ld in built:
        print(f'{slug:10s}  FAQ {nfaq}개  제목 {lt}자  설명 {ld}자')


def write_rss(index_html):
    """네이버 서치어드바이저 RSS 제출용 피드 (메인 + 진료 안내 페이지)"""
    from email.utils import format_datetime
    pub = format_datetime(datetime.datetime(*map(int, TODAY.split('-')), 9, 0,
                                            tzinfo=datetime.timezone(datetime.timedelta(hours=9))))
    items = []
    t = re.search(r'<title>(.*?)</title>', index_html).group(1)
    d = re.search(r'<meta name="description" content="(.*?)">', index_html).group(1)
    items.append((t, f'{DOMAIN}/', d))
    for f in sorted(PAGES.glob('*.html')):
        meta = json.loads(re.search(r'<!--META(.*?)META-->', f.read_text(encoding='utf-8'), re.S).group(1))
        items.append((meta['title'], f'{DOMAIN}/{f.stem}/', meta['description']))
    e = html.escape
    body = '\n'.join(f"""    <item>
      <title>{e(t)}</title>
      <link>{u}</link>
      <guid>{u}</guid>
      <description>{e(d)}</description>
      <pubDate>{pub}</pubDate>
    </item>""" for t, u, d in items)
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>24시 폴 동물병원</title>
    <link>{DOMAIN}/</link>
    <description>분당 정자동 365일 24시간 수의사 상주 동물병원 진료 안내</description>
    <language>ko</language>
    <lastBuildDate>{pub}</lastBuildDate>
{body}
  </channel>
</rss>
"""
    (SITE / 'rss.xml').write_text(xml, encoding='utf-8')


if __name__ == '__main__':
    main()
