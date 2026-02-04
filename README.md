<div align=center>

 # 🎮 취향 기반 게임 추천 커뮤니티 플랫폼

</div>

---
<div align=center> 

### 🔗 <a href="https://swbak.cloud/api/schema/swagger-ui" target="_blank"> 게임 추천 커뮤니티 플랫폼 사이트 바로가기</a>
</div>

---
## 📖 프로젝트 소개
<div align=center>

> 본 프로젝트는 사용자의 선호도를 분석하여 개인 맞춤형 게임을 큐레이션 해주는 취향 기반 게임 추천 커뮤니티 입니다. <br>단순히 인기 순위에 의존하는 기존 방식을 탈피하고, 빅데이터 분석을 통해 숨겨진 인생 게임을 찾아주며, <br>비슷한 취향을 가진 유저들이 소통할 수 있는 순환형 생태계 구축을 목표로 합니다.

</div>

---
## 🗓️ 프로젝트 기간
<div align="center">

### 2026년 1월 6일 ~ 2026년 2월 9일

</div>

---
## 🛠️ 사용 스택 
<div align=center> 
    <img src="https://img.shields.io/badge/Amazon%20EC2-FF9900?style=for-the-badge&logo=Amazon%20EC2&logoColor=white">
    <img src="https://img.shields.io/badge/Amazon%20S3-569A31?style=for-the-badge&logo=Amazon%20S3&logoColor=white">
    <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"> 
    <img src="https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white">
    <img src="https://img.shields.io/badge/Python_3.13-3776AB?style=for-the-badge&logo=python&logoColor=white">
    <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white"> 
    <img src="https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white"> 
    <img src="https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white">
</div>


---
## 📊 ERD
<div align="center">
    <a href="https://dbdiagram.io/d/PLayType-ERD-698175fdbd82f5fce26dd3e0" target="_blank">
        <img src="https://github.com/oz-union-14-team1/oz-union-be-14-team1/blob/develop/PLayType%20ERD.png?raw=true" alt="ERD 다이어그램" width="100%" />
    </a>
</div>

---
## 👨‍💻 팀원 소개 

<table align="center">
  <tr>
    <td align="center" width="200px"><b>회원 파트</b></td>
    <td align="center" width="200px"><b>게임 파트</b></td>
    <td align="center" width="200px"><b>AI 파트</b></td>
    <td align="center" width="200px"><b>댓글 파트</b></td>
  </tr>
  <tr>
    <td align="center">
      <a href="https://github.com/minseokgyang">
        <img src="https://avatars.githubusercontent.com/u/227292159?v=4" width="100px" style="border-radius:50%"/>
      </a><br/>
      <b>양민석</b><br/>
      <a href="https://github.com/minseokgyang">@Yang Minseok</a>
    </td>
    <td align="center">
      <a href="https://github.com/sowon-bak">
        <img src="https://avatars.githubusercontent.com/u/227296029?v=4" width="100px" style="border-radius:50%"/>
      </a><br/>
      <b>박성우</b><br/>
      <a href="https://github.com/sowon-bak">@sowon-bak</a>
    </td>
    <td align="center">
      <a href="https://github.com/KIHOON-KOR">
        <img src="https://avatars.githubusercontent.com/u/221495533?v=4" width="100px" style="border-radius:50%"/>
      </a><br/>
      <b>김기훈</b><br/>
      <a href="https://github.com/KIHOON-KOR">@KIHOON-KOR</a>
    </td>
    <td align="center">
      <a href="https://github.com/j-lee03">
        <img src="https://avatars.githubusercontent.com/u/225314533?v=4" width="100px" style="border-radius:50%"/>
      </a><br/>
      <b>이현직</b><br/>
      <a href="https://github.com/j-lee03">@j-lee03</a>
    </td>
  </tr>
</table>

---
# 🖥️ 서비스 소개
## 회원 





---
## 게임





---
## 📝 리뷰 / 🤖 AI 및 취향 분석 
### ` 💬 게임 리뷰 커뮤니티 / 🤖 AI 요약 및 성향 분석 / 🎯 취향 관리 `

> 사용자의 생생한 게임 경험을 공유하는 리뷰 커뮤니티와, 축적된 데이터를 분석하여 개인화된 인사이트를 제공하는 AI 시스템입니다.



<details>
<summary><strong>게임 리뷰 및 커뮤니티 (Community)</strong></summary><br>

**1. 게임 리뷰**
- **통합 리뷰 피드 (Community Feed)**
    - 모든 게임의 리뷰를 한곳에서 모아보기
    - **장르별 필터링**: 쿼리 파라미터(`?genre=`)를 통한 장르별 리뷰 큐레이션
- 리뷰 작성 및 관리
    - 게임별 리뷰 등록, Markdown 내용 작성, 평점 부여
- 리뷰 조회
    - 최신순/인기순 정렬, 페이지네이션(`Pagination`)
    - DB 조회 최적화 (`Selectors` 패턴 적용)
- 리뷰 상호작용
    - 리뷰 좋아요 및 취소 (`ReviewLike`)
    - 본인 리뷰 수정 및 삭제


<br></details>

<details>
<summary><strong>🤖 AI 분석 시스템 (AI)</strong></summary><br>

**1. 리뷰 요약 (Review Summary)**
- AI 기반 리뷰 분석
    - 긴 리뷰 텍스트의 핵심 내용 요약 및 키워드 추출
- 비동기 처리
    - `Celery` & `Redis`를 활용한 백그라운드 AI 연산 처리 (`tasks.py`)
    - 대용량 데이터 처리 시 사용자 경험(UX) 저하 방지

<br>

**2. 유저 성향 분석 (User Tendency)**
- 플레이 성향 도출
    - 작성된 리뷰와 활동 이력을 바탕으로 유저 성향 분석
    - 분석된 데이터를 기반으로 개인화 추천에 활용
- 비동기 처리
    - `Celery` & `Redis`를 활용한 백그라운드 AI 연산 처리 (`tasks.py`)
    - 대용량 데이터 처리 시 사용자 경험(UX) 저하 방지

<br></details>

<details>
<summary><strong>🎯 사용자 취향 관리 (Preference)</strong></summary><br>

**1. 선호도 데이터 관리**
- 장르(Genre) 선호도
    - 유저가 선호하는 게임 장르 수집 및 관리
- 태그(Tag) 선호도
    - 게임별 세부 태그에 대한 유저 선호도 분석
- 취향 기반 추천 데이터 제공
    - 수집된 선호도(`Preference`) 데이터를 추천 알고리즘의 가중치로 활용

<br></details>

<details>
<summary><strong>👤 회원 프로필 관리 (User)</strong></summary><br>

**1. 프로필 이미지 관리**
- **이미지 업로드 및 수정**
    - `UUID` 기반 파일명 난수화로 파일 중복 방지 및 보안 강화
    - 기존 이미지 자동 삭제 후 새로운 이미지로 교체 (`Media Storage`)
- **이미지 삭제**
    - 프로필 사진 삭제 시 기본(Default) 이미지로 초기화
    - 스토리지 내 실제 파일까지 완벽하게 정리 (`Cleanup`)

<br></details>





---
## 📝 댓글 기능 
### ` 💬 리뷰에 대한 의견 공유 / 🗣️ 유저 간 소통 / ↳ 대댓글 토론 `

> 사용자가 작성한 리뷰에 대해 자유롭게 의견을 제시하고, 대댓글을 통해 깊이 있는 소통을 이어가는 커뮤니티 공간입니다.

<details>
<summary><strong>💬 댓글 시스템 (Comment)</strong></summary>

<br>

**1. 대댓글 지원 게시판**
- **계층형 댓글 구조**
    - 리뷰에 대한 댓글 및 대댓글(Nested Comment) 작성 지원
    - 부모 댓글 참조를 통한 논리적 계층 형성

**2. 댓글 관리 및 조회**
- **댓글 목록 조회**
    - `select_related`를 활용한 쿼리 최적화로 데이터 조회 성능 개선
- **댓글 작성 및 수정/삭제**
    - 작성자 본인 확인 로직을 통한 수정 및 삭제 권한 관리

</details>




---
# 📂 프로젝트 구조

---
```
```text
📦 PLayType
├── 📂 apps                      # 핵심 기능 애플리케이션 모음
│   ├── 📂 ai                    # AI 분석 및 추천 관련 앱
│   │   ├── 📂 models            # 사용자 성향(UserTendency) 등 모델 정의
│   │   ├── 📂 services          # 리뷰 요약 및 성향 분석 비즈니스 로직
│   │   └── 📂 tasks             # Celery 비동기 작업 (AI 연산 등)
│   ├── 📂 community             # 커뮤니티 기능 앱
│   │   ├── 📂 models            # 리뷰, 댓글, 좋아요 모델
│   │   ├── 📂 selectors         # DB 조회 최적화 로직 (QuerySet 분리)
│   │   └── 📂 services          # 리뷰/댓글 작성 및 수정 로직
│   ├── 📂 core                  # 전역 유틸리티 및 공통 모듈
│   │   ├── 📂 exceptions        # 커스텀 예외 처리 핸들러
│   │   └── 📂 utils             # 공통 함수 모음
│   ├── 📂 game                  # 게임 데이터 관리 앱
│   │   ├── 📂 models            # 게임, 장르, 태그, 위시리스트 모델
│   │   ├── 📂 services          # RAWG API 연동 및 게임 데이터 수집(Importer)
│   │   └── 📂 views             # 게임 목록, 상세, 추천, 위시리스트 API
│   ├── 📂 preference            # 사용자 취향 분석 앱
│   │   ├── 📂 models            # 장르/태그 선호도 모델
│   │   └── 📂 services          # 선호도 데이터 처리 로직
│   └── 📂 user                  # 회원 관리 및 인증 앱
│       ├── 📂 models            # 사용자, 소셜 로그인 모델
│       ├── 📂 services          # 프로필 이미지 처리 등 유저 관련 로직
│       ├── 📂 utils             # JWT 토큰, SMS 발송, 인증 유틸리티
│       └── 📂 views             # 로그인, 회원가입, 프로필 관리 API
├── 📂 config                    # Django 프로젝트 설정
│   ├── celery.py                # Celery 비동기 큐 설정
│   ├── settings.py              # 전체 프로젝트 환경 설정
│   └── urls.py                  # 루트 URL 라우팅
├── 📂 media                     # 업로드 된 미디어 파일 저장소
├── 📂 nginx                     # Nginx 리버스 프록시 설정
│   └── nginx.conf
├── 📂 static                    # 정적 파일 (Swagger YAML 등)
├── 📄 Dockerfile                # Django 앱 도커 빌드 설정
├── 📄 docker-compose.yml        # 전체 서비스(Web, DB, Redis, Nginx) 오케스트레이션
├── 📄 manage.py                 # Django 관리 명령어 진입점
├── 📄 poetry.lock               # 패키지 의존성 잠금 파일
└── 📄 pyproject.toml            # Poetry 프로젝트 및 의존성 명세

```
---

# 📘 프로젝트 규칙 (Project Rules)

---
## 📏 코드 컨벤션(Code Convention)

### ❓네이밍 규칙
| 구분 | 규칙 | 예시 |
| :--- | :--- | :--- |
| **파일명** | snake_case | `user_service.py` |
| **클래스명** | PascalCase | `UserService` |
| **함수명** | snake_case | `get_user_info()` |
| **상수** | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |

### 💅 Code Formatting
- mypy
- ruff
- black
  - 위 세 가지를 사용하여 코드 포매팅과 타입 어노테이션을 준수한다.

### 🧪 Test Code
- Django 내부에 포함된 `TestClient`를 활용하여 테스트코드를 작성한다.
- Coverage 80% 이상을 유지한다.

###  🏷️ Swagger 문서
- Swagger 문서 자동화를 위한 라이브러리로 `drf-spectacular`를 사용한다.
- `extend_schema` 데코레이터를 사용하여 스키마를 구성하고 각 API 별 태깅, API 요약, 구체적인 설명, 파라미터 등을 지정한다.
  - Tag는 해당 API가 해당되는 요구사항 정의서의 카테고리 명을 사용
  - Summary에 해당 API의 요약 설명을 기재
  - Description에 해당 API의 구체적인 동작 설명

---
## 💾 커밋 컨벤션(Commit Convention)

### 기본 구조 ✅
```
<type>(#이슈번호): <작업요약>
```
### 예시 ✅
```
✨ feat(#100): Spring Boot
🐛 fix(#139): 휴무 신청 승인 시 NPE 해결
♻️ refactor(#139): 근무 스케줄 조회 로직 리팩터링
📝 docs(#139):  README 배포 구조 업데이트
```
---
## 🏷️ 커밋 메시지 타입 (Commit Types)

| 타입           | 설명 | 예시 |
|:-------------| :--- | :--- |
| **✨ feat**   | 새로운 기능 추가 | `✨ feat(#210): 근무 교대 기능 추가` |
| **🐛 fix**   | 버그 수정 | `🐛 fix(#314): 급여 내역 조회 오류 수정` |
| **♻️ refactor** | 코드 리팩터링 | `♻️ refactor(#271): UserService 구조 개선` |
| **🚚 build**    | 빌드 관련 변경 | `🚚 build(#477): vite 설정 변경` |
| **💡 chore** | 설정, 빌드, 의존성 변경 | `💡 chore(#490): Spring Boot Actuator 추가` |
| **📝 docs**  | 문서 수정 | `📝 docs(#450): API 명세 업데이트` |
| **✅ test**   | 테스트 코드 추가/수정 | `✅ test(#515): 교대 근무 테스트 코드 추가` |
| **🚑 hotfix**   | 긴급 수정 | `🚑 hotfix(#470): 잘못된 리팩터링 롤백` |
| **style**    | 코드 포맷 변경 | `style(#301): isort 적용 및 포맷 정리` |
| **perf**     | 성능 개선 | `perf(#502): 급여 조회 쿼리 최적화` |
| **ci**       | CI/CD 관련 변경 | `ci(#480): GitHub Actions 수정` |
| **revert**   | 이전 커밋 되돌리기 | `revert(#470): 잘못된 리팩터링 롤백` |

### 작성 규칙 ✅
- 반드시 관련 이슈 번호 포함
  - `✨ feat(#210) : ...`
- 명령형 어조 사용, 50자 이내
- 본문(optional)에 상세 변경 내역 작성 가능

---
## 🌿 브랜치 전략
| 브랜치 | 설명 | 예시 |
| :--- | :--- | :--- |
| **main** | 운영/배포용 메인 브랜치 | - |
| **dev** | 개발 통합 브랜치 | - |
| **feature/01-기능** | 기능 추가 | `feature/490-actuator-health-check` |
| **fix/** | 버그 수정 | `fix/512-leave-request-error` |
| **refactor/** | 리팩터링 | `refactor/478-schedule-service` |
| **chore/** | 설정, 빌드 등 기타 | `chore/490-actuator-config` |
| **docs/** | 문서 수정 | `docs/450-readme-update` |


---
## 📑 Documents

### [ 🧚 요구사항 정의서 ](https://docs.google.com/spreadsheets/d/1Xt9cDKG0CBOWRZlahPszes8hQvRcOftvTBJnDmApnCc/edit?gid=0#gid=0)
 
### [ 🪄 API 명세서 ](https://docs.google.com/spreadsheets/d/1RjxUrxGCCx23wks4-FlZUcoi_1WG0JOlw0Zle4wQaeU/edit?gid=0#gid=0)

### [ 🔦 테이블 명세서 ](https://docs.google.com/spreadsheets/d/1aaw_16uQTA1ycstLEDB9pAvGDtfifOdXr9Lm1JmyAIA/edit?gid=0#gid=0)


















