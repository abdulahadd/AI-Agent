#!/bin/bash
set -e

# Replace environment variables in template and generate pjsip.conf
envsubst '${PUBLIC_IP} ${PJSIP_SECRET}' < /etc/asterisk/pjsip.conf.template > /etc/asterisk/pjsip.conf

# Start Asterisk in foreground
exec asterisk -f