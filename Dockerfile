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

# 정적 파일 수집 nginx는 프로젝트 구조를 몰라서 gunicorn이 이걸 통해 정적 파일을 모아서 제공하면 그걸 보고 nginx가 실행
RUN python manage.py collectstatic --noinput

# 5. 실행 명령
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# 바로 장고 실행이 아니라 gunicorn을 사용해서 실행
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]