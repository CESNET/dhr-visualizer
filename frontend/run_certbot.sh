#!/bin/sh

CERT_DIR="/etc/letsencrypt"
WEBROOT="/var/www/certbot"

if [ ! -f "$CERT_DIR/live/$FRONTEND_DOMAIN/fullchain.pem" ]; then
    # HTTPS certificate does not exist
    echo "Requesting new HTTPS certificate"
    certbot certonly --webroot -w $WEBROOT -d $FRONTEND_DOMAIN --non-interactive --agree-tos --email $FRONTEND_EMAIL
else
    # HTTPS certificate exists
    echo "HTTPS certificate exist, attempting renewal"
    certbot renew --webroot -w $WEBROOT --non-interactive
fi

echo "HTTPS certificate obtained"

# Renew certificate every 12 hours
while true; do
    renewal_time=43200
    echo "Certificate renewal will occur in $(( renewal_time / 3600 )) hours."
    sleep $renewal_time # 43200 seconds == 12 hours
    certbot renew --webroot -w $WEBROOT --non-interactive
done
