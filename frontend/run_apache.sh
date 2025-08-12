#!/bin/sh

set -e

CERT_PATH="/etc/letsencrypt/live/$FRONTEND_DOMAIN/fullchain.pem"
CONF_DIR="/usr/local/apache2/conf"

echo "Populating httpd.conf with .env variables"

envsubst < $CONF_DIR/httpd_no_ssl.conf > $CONF_DIR/httpd_no_ssl.conf.tmp
mv $CONF_DIR/httpd_no_ssl.conf.tmp $CONF_DIR/httpd_no_ssl.conf

envsubst < $CONF_DIR/httpd_ssl_part.conf > $CONF_DIR/httpd_ssl_part.conf.tmp
mv $CONF_DIR/httpd_ssl_part.conf.tmp $CONF_DIR/httpd_ssl_part.conf

echo "httpd.conf populated with .env variables"

# Prepare initial config based on cert presence
if [ ! -f "$CERT_PATH" ]; then
    echo "No SSL certificate yet. Starting Apache in HTTP mode"
    cat $CONF_DIR/httpd_no_ssl.conf > $CONF_DIR/httpd.conf
else
    echo "SSL certificate found. Starting Apache in HTTPS mode"
    cat $CONF_DIR/httpd_no_ssl.conf $CONF_DIR/httpd_ssl_part.conf > $CONF_DIR/httpd.conf
fi

# Start Apache in background
httpd-foreground &

# Save Apache PID
apache_pid=$!

# Watch for cert and reload Apache when needed
while true; do
    if [ -f "$CERT_PATH" ] && ! grep -q "$CONF_DIR/httpd_ssl_part.conf" $CONF_DIR/httpd.conf; then
        echo "Certificate detected, switching Apache to HTTPS"
        cat $CONF_DIR/httpd_no_ssl.conf $CONF_DIR/httpd_ssl_part.conf > $CONF_DIR/httpd.conf
        apachectl graceful
    fi
    sleep 10
done &

# Reload Apache every 12 hours for renewal
while true; do
    sleep 43200
    echo "Reloading Apache for certificate renewal"
    apachectl graceful
done &

# Wait for Apache to exit
wait $apache_pid
