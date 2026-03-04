#!/bin/sh
set -eu

TEMPLATE_DIR="/opt/nginx-templates/conf.d"
OUTPUT_DIR="/etc/nginx/conf.d"

render() {
  variables="$1"
  template_name="$2"
  output_name="$3"
  envsubst "$variables" < "${TEMPLATE_DIR}/${template_name}" > "${OUTPUT_DIR}/${output_name}"
}

mkdir -p "${OUTPUT_DIR}"
rm -f "${OUTPUT_DIR}"/*.conf

case "${DEPLOY_MODE:-ip}" in
  ip)
    render '' "ip.conf.template" "ip.conf"
    ;;
  domain)
    : "${APP_DOMAIN:?APP_DOMAIN is required when DEPLOY_MODE=domain}"
    if [ "${ENABLE_TLS:-false}" = "true" ]; then
      : "${TLS_CERT_PATH:?TLS_CERT_PATH is required when ENABLE_TLS=true}"
      : "${TLS_KEY_PATH:?TLS_KEY_PATH is required when ENABLE_TLS=true}"
      render '${APP_DOMAIN}' "app.redirect.conf.template" "app.conf"
      render '${APP_DOMAIN} ${TLS_CERT_PATH} ${TLS_KEY_PATH}' "app.tls.conf.template" "app-tls.conf"
    else
      render '${APP_DOMAIN}' "app.conf.template" "app.conf"
    fi
    ;;
  *)
    echo "Unsupported DEPLOY_MODE: ${DEPLOY_MODE}" >&2
    exit 1
    ;;
esac
