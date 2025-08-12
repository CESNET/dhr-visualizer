#!/bin/sh

CERT_DIR="/etc/letsencrypt"
WEBROOT="/var/www/certbot"

if [ ! -f "$CERT_DIR/live/$DOMAIN/fullchain.pem" ]; then
  # HTTPS certificate does not exist
  echo "Requesting new HTTPS certificate"
  certbot certonly --webroot -w $WEBROOT -d $FRONTEND__DOMAIN --non-interactive --agree-tos --email $FRONTEND__EMAIL
else
  # HTTPS certificate exists
  echo "HTTPS certificate exist, attempting renewal"
  certbot renew --webroot -w $WEBROOT --non-interactive --quiet
fi

# Renew certificate every 12 hours
while true; do
  sleep 43200  # 43200 seconds == 12 hours
  certbot renew --webroot -w $WEBROOT --non-interactive --quiet
done
