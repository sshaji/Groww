#!/bin/bash
cd "$(dirname "$0")" || exit 1
if [ -x .venv/bin/python ]; then
    .venv/bin/python -m sip_lab.connect
else
    echo 'The project virtual environment is missing. Ask the assistant to set it up.'
fi
read -r -p 'Press Enter to close.'
