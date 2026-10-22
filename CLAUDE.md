# 24시 폴 동물병원 홈페이지 (paulah.co.kr)

## 배포 구조

```
GitHub (artokp-dev/paulah)  ──push──▶  Netlify  ──▶  https://paulah.co.kr
```

- `main` 브랜치에 push하면 Netlify가 자동 배포한다.
- 공개되는 건 **`site/` 폴더뿐**이다 (`netlify.toml`의 `publish = "site"`).
  이 CLAUDE.md, netlify.toml 등은 공개되지 않는다.
- 빌드 과정 없음. 정적 HTML 그대로 서빙.

## 폴더 구조

```
CLAUDE.md            이 문서 (비공개)
netlify.toml         배포 설정 (비공개)
site/                ← 공개되는 사이트
  index.html         단일 페이지, 약 100KB
  images/            사진 14장 (외부 파일)
  favicon.ico        16/32/48/64 멀티사이즈
  favicon-16.png, favicon-32.png
  apple-touch-icon.png
  og-image.jpg       1200x630 병원 외관
  logo-512.png       구조화 데이터용 로고
  robots.txt, sitemap.xml
  naver6442f436681a37ef7fe920069521652b.html    네이버 소유확인 (현재)
  navere162167ea930c64cb51b04d8ffed2905.html    네이버 소유확인 (구, 남겨둠)
```

## 기본 정보

| 항목 | 값 |
|---|---|
| 병원명 | 24시 폴 동물병원 / PAUL ANIMAL HOSPITAL |
| 주소 | 경기도 성남시 분당구 성남대로 385 분당클리닉빌딩 1층 |
| 전화 | 031-717-7558 |
| 좌표 | **37.3705297, 127.1076281** (정확한 값. 예전 37.362120/127.113920은 900m 틀렸음) |
| 블로그 | blog.naver.com/hwrat |
| 인스타 | @24paulah |
| 카카오 채널 | http://pf.kakao.com/_xfkxekM/chat |
| 네이버 예약 | https://naver.me/xKyevLBK |

## 이미지

| 파일 | 내용 |
|---|---|
| hospital-exterior.jpg | 외관 (PAUL 간판). 히어로 배경 + 소개 |
| reception.jpg | 리셉션/로비 |
| doctor-kim-yulhyun.jpg | 김율현 원장 (안경, 골든리트리버 강아지) |
| doctor-kim-pyeong.jpg | 김평 원장 (안경 없음) |
| doctor-kim-serim.jpg | 김세림 원장 |
| doctor-kim-jongwan.jpg | 김종완 진료수의사 |
| facility-echo.jpg | 심장초음파 진료 장면 |
| facility-operating-room.jpg | 수술실 |
| facility-exam-room.jpg | 진료실 |
| blog-dog-checkup.jpg / blog-cat-checkup.jpg | 2026 건강검진 프로그램 카드 |
| blog-night-er.jpg | 야간응급 블로그 카드 (복도 고양이 액자) |
| logo-nav.webp | 상단 로고 (라인 로고) |
| logo-footer.jpg | 하단 로고 (십자가+고양이 로고) |

이미지를 교체하면 파일명은 유지한다. og-image를 바꾸면 index.html의 `og-image.jpg?v=N` 버전을 올린다.

## 파비콘

로고(강아지+고양이 라인아트)가 16px에서 뭉개져서 크기별로 다른 그림을 쓴다.
- 16px → 세리프 **P** (브라우저 탭)
- 32/48/64/180px → 강아지+고양이 심볼 (선 굵게)

PIL의 ICO 저장은 `append_images`를 무시하므로 멀티사이즈 ICO는 바이너리를 직접 쓴다.
로고 배경색은 `#021a43` (2, 26, 67).

## 표현 규칙

- **'전문' 금지** (수의사법 광고 심의). 노령동물 전문 → **중점진료**, 심장초음파 전문 → **정밀 진단**.
  '전문성을 갖춘' 같은 서술형은 허용.
- 과장된 직함·수식 금지. 담백한 톤.
- 의료 효과를 단정하는 표현 금지 ("완치", "100%" 등).

## 의료진

| 이름 | 직함 | 분야 |
|---|---|---|
| 김율현 | 원장 | 치과, 외과·일반내과, 노령동물, 특수동물 |
| 김평 | 원장 | 심장·내과, 노령동물 만성질환, 건강검진 |
| 김세림 | 원장 | 건강검진·예방의학, 심장초음파, 내과 심화 |
| 김종완 | 진료수의사 | 중증·응급, 내과·영상진단, 건국대 수의대 |

## SEO 현황

- 네이버 서치어드바이저 등록 + 사이트맵 제출 ✅ (인증: `6442f436681a37ef7fe920069521652b`)
- 구글 서치콘솔 DNS TXT 인증 + 사이트맵 제출 ✅ (메타: `fb2IMgi83T_PYPyM84LkgRmpzPlgItX_kkPykhau4JI`)
- title 30자 / description 67자 (네이버 권장 40/80자 이내)
- 구조화 데이터: VeterinaryCare + FAQPage
- og:image = 병원 외관 사진 (로고는 잘리면 파란 사각형만 남아서 안 씀)

진단은 반드시 **`https://paulah.co.kr`** (www 없이)로 할 것.
www는 apex로 301 리다이렉트되어 "robots.txt 없음" 같은 거짓 경고가 뜬다.

## 작업 원칙

1. 페이지 구조를 크게 바꾸는 작업(페이지 분리 등)은 **먼저 원장님께 물어본다.**
2. 원인을 단정하기 전에 확인한다.
3. 수정 후 Playwright로 렌더 검증: JS 에러 0, 깨진 이미지 0.
   (`.rev` 리빌 애니메이션 때문에 스크린샷이 비면
   `.rev,[class*=rev]{opacity:1!important;transform:none!important}` 주입)
4. 커밋 메시지는 한국어로, 무엇을 왜 바꿨는지 한 줄.

## 우선순위 인식

신규 환자 유입: **네이버 플레이스 ≫ 블로그 ≫ 홈페이지.**
홈페이지는 블로그·플레이스를 보고 온 사람이 확인하는 신뢰 검증 채널.

## 검토 중

- 페이지 분리 / AI 검색 최적화(GEO) — 진행 여부 원장님 결정 대기
- 네이버 검색결과 이미지 노출 대기 (1~2주)
- 네이버 플레이스에 새 인테리어 사진·로고·김종완 수의사 반영 여부 점검
