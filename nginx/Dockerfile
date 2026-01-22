FROM nginx:alpine

# 기본 설정 제거
RUN rm -rf /etc/nginx/conf.d/*

# 커스텀 설정 복사
COPY nginx.conf /etc/nginx/conf.d/default.conf