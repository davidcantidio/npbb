FROM postgres:15-alpine

RUN apk add --no-cache bash gettext tzdata

COPY backup.sh /usr/local/bin/backup.sh
COPY start-crond.sh /usr/local/bin/start-crond.sh
COPY crontab /etc/cron.template

RUN chmod +x /usr/local/bin/backup.sh /usr/local/bin/start-crond.sh

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=5 \
  CMD sh -c "ps | grep '[c]rond' >/dev/null && test -s /etc/crontabs/root"

CMD ["/usr/local/bin/start-crond.sh"]
