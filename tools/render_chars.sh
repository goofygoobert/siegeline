#!/bin/bash
# Usage: tools/render_chars.sh id [id...]  — bundle, compile-check, render on 5070, contact sheet
cd "$(dirname "$0")/.."
for c in "$@"; do
  src=$(ls art/blender/chars/$c.py 2>/dev/null) || { echo "no $c"; continue; }
  python3 tools/bundle_blend.py $src art/build/$c.py >/dev/null
  python3 -m py_compile art/build/$c.py || { echo "SYNTAX $c"; continue; }
  N=$(python3 -c "import re;s=open('art/blender/kit.py').read();print(sum(int(n) for n in re.findall(r'\(\"\w+\", (\d+)\)', s.split('ANIMS =')[1].split('\n')[0])))")
  rm -rf art/out/$c
  for try in 1 2 3; do
    timeout 900 gpu5070 render art/build/$c.py --frames 1-$N --engine eevee --wait-busy 60 --out art/out/$c > art/build/$c.log 2>&1 && break
    grep -q "unreachable\|not answering" art/build/$c.log && gpu5070 wake >/dev/null 2>&1
    echo "retry $c ($try)"; sleep 30
  done
  ls art/out/$c/frame_*.png >/dev/null 2>&1 && .venv/bin/python tools/contact.py art/out/$c art/out/${c}_sheet.png 12 >/dev/null && echo "OK $c" || { echo "FAIL $c"; tail -3 art/build/$c.log; }
done
