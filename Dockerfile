FROM verdel/centos-base:latest
LABEL maintainer="Vadim Aleksandrov <valeksandrov@me.com>"

ENV DB_HOST localhost
ENV DB_PORT 3306
ENV DB_USER zabbix
ENV DB_PASS zabbix

# Install zabbix
RUN dnf install -y https://repo.zabbix.com/zabbix/5.0/rhel/8/x86_64/zabbix-release-5.0-1.el8.noarch.rpm && \
    dnf install -y zabbix-server-mysql zabbix-agent mariadb && \
    pip3 install --upgrade setuptools && \
    pip3 install requests librouteros && \
    # Clean up
    dnf clean all && \
    rm -rf \
    /usr/share/man \
    /tmp/* \
    /var/cache/dnf

# Copy init scripts
COPY rootfs /

RUN chmod 640 /etc/zabbix/zabbix_server.conf
RUN chown root:zabbix /etc/zabbix/zabbix_server.conf

# Export volumes directory
VOLUME ["/etc/zabbix/alertscripts", "/etc/zabbix/externalscripts", "/etc/zabbix/tls"]

# Export ports
EXPOSE 10051/tcp 10052/tcp
