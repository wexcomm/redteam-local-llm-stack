#!/usr/bin/env bash
# Helper: Get Windows host IP from WSL2
# Usage: source ./scripts/get-windows-host.sh && echo $WINDOWS_HOST_IP

WINDOWS_HOST_IP=$(ip route | grep default | awk '{print $3}' | head -1)
if [ -z "$WINDOWS_HOST_IP" ]; then
    WINDOWS_HOST_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}' | head -1)
fi
export WINDOWS_HOST_IP
