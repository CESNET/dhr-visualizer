FROM httpd:latest

RUN apt-get update && apt-get install -y --no-install-recommends gettext-base && rm -rf /var/lib/apt/lists/*

COPY apache/httpd_no_ssl.conf /usr/local/apache2/conf/httpd_no_ssl.conf
COPY apache/httpd_ssl_part.conf /usr/local/apache2/conf/httpd_ssl_part.conf

COPY html/ /usr/local/apache2/htdocs/

COPY run_apache.sh /run_apache.sh
RUN chmod +x /run_apache.sh

CMD ["/run_apache.sh"]
