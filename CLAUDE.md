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
tools/               (비공개)
  build.py           진료 안내 페이지 생성기
  pages/*.html       진료 안내 페이지 원고 ← 문구는 여기서 고친다
  check.py           렌더 검증 (JS 에러·깨진 이미지·죽은 링크·가로 스크롤)
site/                ← 공개되는 사이트
  index.html         메인 원페이지, 약 100KB (CSS는 <style> 인라인)
  checkup/ heart/ dental/ emergency/   진료 안내 페이지 (build.py 결과물)
  assets/base.css    index.html <style> 자동 복사본 (직접 수정 금지)
  assets/page.css    진료 안내 페이지 전용 스타일
  llms.txt           AI 검색용 병원 요약
  rss.xml            네이버 RSS 제출용 피드 (build.py가 자동 생성)
  14df6dda63ade1e438f73be0740d05b2.txt   IndexNow 키 파일 (빙·ChatGPT 색인 요청용, 지우지 말 것)
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

## 진료 안내 페이지 (2026-10-22 추가, AI 검색 최적화)

| 주소 | 내용 |
|---|---|
| /checkup/ | 건강검진 — 나이별 주기, 3단계 프로그램, 진행 과정 |
| /heart/ | 심장·노령동물 내과 — 심장초음파, 당뇨·쿠싱·신장 |
| /dental/ | 치과·스케일링 — 신호, 마취 이유, 집 관리 |
| /emergency/ | 24시 응급·오시는 길 — 응급 증상, 위험 음식, 위치 |

작업 순서:
1. 문구 수정 → `tools/pages/<slug>.html` (META 안 title 40자·description 80자 이내)
2. `python3 tools/build.py` → site/<slug>/index.html 재생성 + base.css 갱신
   (index.html의 <style>을 고쳤으면 반드시 다시 실행)
3. `python3 tools/check.py /tmp/out / /checkup/ /heart/ /dental/ /emergency/` → TOTAL PROBLEMS: 0 확인
4. FAQ 구조화 데이터는 화면의 `<details class="faq-item">`에서 자동 생성된다.
   index.html의 FAQ를 고치면 FAQPage JSON-LD도 같이 고친다.
5. 새 페이지를 추가하면 build.py의 TOPICS, sitemap.xml, llms.txt, index.html 푸터에도 넣는다.

블로그 글을 홈페이지에 그대로 복사하지 않는다 (네이버 유사문서 판정 위험). 요약 + 블로그 링크 방식.
사이트·블로그에 없는 사실(비용, 소요 시간 등)은 원장님 확인 전까지 쓰지 않는다.

## 기본 정보

| 항목 | 값 |
|---|---|
| 병원명 | 24시 폴 동물병원 / PAUL ANIMAL HOSPITAL |
| 주소 | 경기도 성남시 분당구 성남대로 385, 분당클리닉빌딩 1층 102호 |
| 교통 | 수인분당선·신분당선 **정자역 5번 출구 도보 약 5분** (예전 "1번 출구 도보 3분"은 틀림) |
| 주차 | 건물 뒤편 1층 및 지하 1~4층 주차장, 무료 2시간, 차량 제한 없음 (원장님 확인 2026-10-22) |
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
| doctor-kim-serim.jpg | 김세림 내과과장 |
| doctor-kim-jongwan.jpg | 김종완 진료수의사 |
| facility-echo.jpg | 심장초음파 진료 장면 |
| facility-operating-room.jpg | 수술실 |
| facility-exam-room.jpg | 진료실 |
| blog-dog-checkup.jpg / blog-cat-checkup.jpg | 2026 건강검진 프로그램 카드 |
| blog-night-er.jpg | 야간응급 블로그 카드 (복도 고양이 액자) |
| logo-nav.webp | 상단 로고 (라인 로고) |
| logo-footer.jpg | 하단 로고 (2026 새 로고 심볼, apple-touch-icon과 같은 그림. src에 ?v=2) |

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
- 진료 시간 표현은 **"24시간 수의사 상주 · 언제든 진료 가능"**. "야간 수의사 상주 · 오후 9시~오전 9시"는 쓰지 않는다 (원장님 요청 2026-10-22).

## 의료진

| 이름 | 직함 | 분야 |
|---|---|---|
| 김율현 | 원장 | 치과, 외과·일반내과, 노령동물, 특수동물 |
| 김평 | 원장 | 심장·내과, 노령동물 만성질환, 건강검진 |
| 김세림 | **내과과장** (원장 아님, 2026-10-22 정정) | 건강검진·예방의학, 심장초음파, 내과 심화 |
| 김종완 | 진료수의사 | 중증·응급, 내과·영상진단, 건국대 수의대 |

## SEO 현황

- robots.txt: 네이버(Yeti)·다음·구글·빙·AI 검색 크롤러(OAI-SearchBot, Claude-SearchBot, PerplexityBot 등) 명시 허용
- 안내 페이지에 "작성 · 24시 폴 동물병원 수의사 | 최종 수정일" 표시 (네이버 AI 브리핑은 작성·수정일 명시를 권장)
- 메인 구조화 데이터에 의료진 4명 Person(employee) 포함
- 2026 트렌드 메모: 네이버 AI 브리핑 출처의 약 80%가 네이버 내부(블로그·지도·플레이스), 구글 AI 요약은 구글 비즈니스 프로필이 1순위,
  ChatGPT는 빙 색인 사용 → 홈페이지보다 플레이스·블로그·구글 비즈니스 프로필·빙 웹마스터 등록이 더 큰 효과

- 네이버 서치어드바이저 등록 + 사이트맵 제출 ✅ (인증: `6442f436681a37ef7fe920069521652b`)
- 구글 서치콘솔 DNS TXT 인증 + 사이트맵 제출 ✅ (메타: `fb2IMgi83T_PYPyM84LkgRmpzPlgItX_kkPykhau4JI`)
- title 30자 / description 67자 (네이버 권장 40/80자 이내)
- 구조화 데이터: 메인 = VeterinaryCare + FAQPage + WebSite / 안내 페이지 = WebPage + BreadcrumbList + FAQPage
- 메인에 남아 있는 영문 `SPECIALTY` 배지(진료과목·시설)와 '치과 Specialty'는 '전문'과 같은 뜻이라 광고 심의상 애매함 — 원장님 판단 대기
- og:image = 병원 외관 사진 (로고는 잘리면 파란 사각형만 남아서 안 씀)

진단은 반드시 **`https://paulah.co.kr`** (www 없이)로 할 것.
www는 apex로 301 리다이렉트되어 "robots.txt 없음" 같은 거짓 경고가 뜬다.

## 네이버 광고 전환추적 (wcs.trans, 2026-10-24)

- 공통키(na_account_id) `s_859375249a1`. 광고계정번호 1732929는 다른 값 — 코드에 넣지 말 것.
- 메인 index.html의 `</body>` 앞 + 안내 페이지 4개(build.py 틀)에 같은 블록. 하나를 고치면 둘 다 고친다.
- 페이지뷰 1회 + 클릭 전환: 전화(tel:) custom001 / 카카오 상담(pf.kakao.com) custom002 / 네이버 예약(naver.me) custom003.
  지도·블로그 링크는 수집 안 함. 1초 안 연타는 1건. 개인정보 전송 없음.
- `location.hostname !== "paulah.co.kr"`이면 수집 안 함 (PR 미리보기·로컬 테스트가 광고 보고서에 섞이지 않게).
- 다른 분석 도구(GA·GTM·메타·카카오 픽셀)는 없음. 새로 넣을 때 중복 수집 주의.

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

- AI 검색 최적화 반영 완료 (2026-10-22, PR #1). 미답변: 고양이 대기공간 분리, 심장초음파 무마취, 고양이 치과 블로그 제목, SPECIALTY 배지
- 네이버 검색결과 이미지 노출 대기 (1~2주)
- 네이버 플레이스에 새 인테리어 사진·로고·김종완 수의사 반영 여부 점검
