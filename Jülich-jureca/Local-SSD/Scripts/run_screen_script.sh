#!/bin/bash

source ~/.bashrc

PROMETHEUS_DIRECTORY="/p/project/cslfse/boulis1/prometheus"  # Replace with the path to Prometheus directory

if ! screen -list | grep -q "prometheus"; then
        # Create the screen session with the generic command
        screen -dmS prometheus /bin/bash -c "cd $PROMETHEUS_DIRECTORY && ./prometheus --web.enable-lifecycle --config.file=prometheus.yml"

else
    echo "Screen session 'prometheus' already exists."
fi
