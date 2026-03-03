FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d /opt/nginx-templates/conf.d
COPY render.sh /docker-entrypoint.d/99-render-config.sh

RUN chmod +x /docker-entrypoint.d/99-render-config.sh
