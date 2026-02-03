# 🎮 취향 기반 게임 추천 커뮤니티 플랫폼

---
<div align=center> 

### 🔗 <a href="https://swbak.cloud/api/schema/swagger-ui" target="_blank"> 게임 추천 커뮤니티 플랫폼 사이트 바로가기</a>
</div>

---
## 📖 프로젝트 소개
<div align=center>

> 본 프로젝트는 사용자의 선호도를 분석하여 개인 맞춤형 게임을 큐레이션 해주는 취향 기반 게임 추천 커뮤니티 입니다. 단순히 인기 순위에 의존하는 기존 방식을 탈피하고, 빅데이터 분석을 통해 숨겨진 인생 게임을 찾아주며, 비슷한 취향을 가진 유저들이 소통할 수 있는 순환형 생태계 구축을 목표로 합니다.

</div>

---
## 🗓️ 프로젝트 기간
- ### 2026년 1월 6일 ~ 2026년 2월 9일

---
## 사용 스택 
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
## ERD
<div align="center">
    <a href="https://dbdiagram.io/d/PLayType-ERD-698175fdbd82f5fce26dd3e0" target="_blank">
        <img src="https://github.com/oz-union-14-team1/oz-union-be-14-team1/blob/develop/PLayType%20ERD.png?raw=true" alt="ERD 다이어그램" width="100%" />
    </a>
</div>

---
## 서비스 소개 

### '회원 파트'
| <a href="https://github.com/minseokgyang"><img src="https://avatars.githubusercontent.com/u/227292159?v=4" width="100px"/><br/><sub><b>@Yang Minseok</b></sub></a><br/> |
|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|                                                                                 **양민석**                                                                                 |


---
### '게임 파트'
| <a href="https://github.com/sowon-bak"><img src="https://avatars.githubusercontent.com/u/227296029?v=4" width="100px"/><br/><sub><b>@sowon-bak</b></sub></a><br/> |
|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|                                                                              **박성우**                                                                              |

---
### '리뷰/선호장르 파트'
| <a href="https://github.com/KIHOON-KOR"><img src="https://avatars.githubusercontent.com/u/221495533?v=4" width="100px"/><br/><sub><b>@KIHOON-KOR</b></sub></a><br/> |
|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|                                                                               **김기훈**                                                                               | 

---
### '댓글파트'
| <a href="https://github.com/j-lee03"><img src="https://avatars.githubusercontent.com/u/225314533?v=4" width="100px"/><br/><sub><b>@j-lee03</b></sub></a><br/> |
|:-------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|                                                                            **이현직**                                                                            |








---
## 코드 컨벤션
| 구분 | 규칙 | 예시 |
| :--- | :--- | :--- |
| **파일명** | snake_case | `user_service.py` |
| **클래스명** | PascalCase | `UserService` |
| **함수명** | snake_case | `get_user_info()` |
| **상수** | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |

---
## 커밋 컨벤션

### 기본 구조 ✅
```
<type>(#이슈번호): <작업요약>
```
### 예시 ✅
```
feat (#100): Spring Boot
fix(#512): 휴무 신청 승인 시 NPE 해결
refactor(#478): 근무 스케줄 조회 로직 리팩터링
docs(#501): README 배포 구조 업데이트
```

---
## 브랜치 전략
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
## 커밋 메시지 타입 (Commit Types)
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
## code style
### 1. 린트 및 Import 정리 (자동 수정)
poetry run ruff check . --fix

### 2. 코드 포맷팅 (자동 수정)
poetry run black .

### 3. 타입 검사
poetry run mypy .
























