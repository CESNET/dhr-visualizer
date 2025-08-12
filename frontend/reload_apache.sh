#!/bin/sh

while true; do
    sleep 43200  # 43200 seconds == 12 hours
    echo "Reloading Apache2 for certificate renewal"
    apachectl graceful
done
