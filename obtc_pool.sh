SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

$SCRIPT_DIR/src/ckpool -c $SCRIPT_DIR/ckpool.conf -l 5 & (sleep 5 && $SCRIPT_DIR/tools/parser/accounting.sh)
