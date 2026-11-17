#!/bin/bash
# Restart the preview server for dist/ on 127.0.0.1:5194 (pid kept in $TMPDIR/preview.pid)
cd "$(dirname "$0")/.."
P=${TMPDIR:-/tmp}/preview.pid
[ -f $P ] && kill $(cat $P) 2>/dev/null; sleep 0.5
nohup npx vite preview --host 127.0.0.1 --port 5194 --strictPort > ${TMPDIR:-/tmp}/preview.log 2>&1 &
echo $! > $P; sleep 2; curl -s -o /dev/null -w "preview %{http_code}\n" http://127.0.0.1:5194/
