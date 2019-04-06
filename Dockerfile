FROM verdel/centos-base:latest
MAINTAINER Vadim Aleksandrov <valeksandrov@me.com>

ENV DB_HOST localhost
ENV DB_PORT 3306
ENV DB_USER zabbix
ENV DB_PASS zabbix

# Install zabbix
RUN yum install -y https://repo.zabbix.com/zabbix/4.2/rhel/7/x86_64/zabbix-release-4.2-1.el7.noarch.rpm && \
    yum install -y zabbix-server-mysql zabbix-agent mariadb && \
    pip install --upgrade setuptools && \
    pip install requests librouteros && \
    # Clean up
    yum clean all && \
    rm -rf \
    /usr/share/man \
    /tmp/* \
    /var/cache/yum

# Copy init scripts
COPY rootfs /

RUN chmod 640 /etc/zabbix/zabbix_server.conf
RUN chown root:zabbix /etc/zabbix/zabbix_server.conf

# Export volumes directory
VOLUME ["/etc/zabbix/alertscripts", "/etc/zabbix/externalscripts", "/etc/zabbix/tls"]

# Export ports
EXPOSE 10051/tcp 10052/tcp
