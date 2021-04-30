#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
python3 $SCRIPT_DIR/utils/accounter.py & python3 $SCRIPT_DIR/utils/payer.py