#!/bin/bash

# Apply epomaker udev rules
epomakercontroller dev --udev

# Switch to non-root user to run the application
exec su - nonrootuser -s /bin/bash
