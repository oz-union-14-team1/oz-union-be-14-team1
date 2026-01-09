FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# 1. 시스템 의존성 설치 (PostgreSQL 빌드 등에 필요할 수 있음) & Poetry 설치
RUN apt-get update && apt-get install -y curl && \
    pip install poetry && \
    poetry config virtualenvs.create false

# 2. 의존성 파일 복사 (캐싱 활용)
COPY pyproject.toml poetry.lock* /app/

# 3. 의존성 설치 (개발용 패키지 제외, 운영용만 설치)
RUN poetry install --no-root --only main

# 4. 소스 코드 복사
COPY . /app/

# 5. 실행 명령
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]