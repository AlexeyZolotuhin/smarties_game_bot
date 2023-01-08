#!/bin/sh
exec gunicorn -b :4000 --access-logfile - --error-logfile - main:app_poller
