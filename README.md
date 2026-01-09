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

























