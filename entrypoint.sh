#!/bin/bash

# Apply epomaker udev rules if necessary
if [ ! -f /etc/udev/rules.d/99-epomaker-rt100.rules ]; then
    epomakercontroller dev --udev >/dev/null 2>&1
fi

APP_ARGS="$@"

# Switch to non-root user and execute the application with the passed arguments
exec su - nonrootuser -c "epomakercontroller $APP_ARGS"
