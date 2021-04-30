#!/bin/bash



SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"


mkdir -p $SCRIPT_DIR/logs
touch $SCRIPT_DIR/logs/accounter.log
touch $SCRIPT_DIR/logs/payer.log

payerLog="$SCRIPT_DIR/logs/payer.log"
accounerLog="$SCRIPT_DIR/logs/accounter.log"

(python3 $SCRIPT_DIR/utils/accounter.py ) & (python3 $SCRIPT_DIR/utils/payer.py)