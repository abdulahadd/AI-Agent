FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y asterisk && \
    rm -rf /var/lib/apt/lists/*

COPY pjsip.conf /etc/asterisk/pjsip.conf
COPY extensions.conf /etc/asterisk/extensions.conf

EXPOSE 5060/udp 10000-20000/udp

CMD ["asterisk", "-f"]