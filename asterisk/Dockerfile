FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y asterisk gettext-base && \
    rm -rf /var/lib/apt/lists/*

# Copy configuration files directly into the image
COPY pjsip.conf.template /etc/asterisk/pjsip.conf.template
COPY extensions.conf /etc/asterisk/extensions.conf
COPY modules.conf /etc/asterisk/modules.conf
COPY http.conf /etc/asterisk/http.conf
COPY ari.conf /etc/asterisk/ari.conf
COPY entrypoint.sh /entrypoint.sh


RUN chmod +x /entrypoint.sh

EXPOSE 5060/udp 8088 8089 10000-20000/udp 10000-20000/tcp

CMD ["asterisk", "-f"]

ENTRYPOINT ["/entrypoint.sh"]