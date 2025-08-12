FROM httpd:latest

COPY apache/httpd.conf /usr/local/apache2/conf/httpd.conf
COPY html/ /usr/local/apache2/htdocs/

COPY reload_apache.sh /reload_apache.sh
RUN chmod +x /reload_apache.sh

CMD ["/bin/sh", "-c", "/reload_apache.sh & httpd-foreground"]
