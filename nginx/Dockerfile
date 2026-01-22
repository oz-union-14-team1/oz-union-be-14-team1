FROM nginx:alpine

# 기본 설정 제거
RUN rm /etc/nginx/conf.d/default.conf

# 커스텀 설정 복사
COPY nginx.conf /etc/nginx/conf.d/