#!/bin/bash
# Bundle + render scenery jobs on the 5070, then pack: art/blender/bg/render_all.sh [bg castles fx title worldmap]
cd "$(dirname "$0")/../../.."
SC="--lib art/blender/scenery.py"
declare -A SRC=([bg]=r1_bgs [castles]=castles [fx]=fx [title]=title [worldmap]=worldmap)
declare -A FR=([bg]=1-8 [castles]=1-8 [fx]=1-25 [title]=1 [worldmap]=1)
for j in "${@:-bg castles fx title worldmap}"; do for k in $j; do
  case $k in
    bg) L="$SC --lib art/blender/bg/r1_lib.py";;
    worldmap) L="$SC --lib art/blender/bg/map_lib.py";;
    title) L="$(cat art/build/title_libs.txt)";;
    *) L="$SC";;
  esac
  python3 tools/bundle_blend.py art/blender/bg/${SRC[$k]}.py art/build/sc_$k.py $L >/dev/null
  python3 -m py_compile art/build/sc_$k.py || { echo "SYNTAX $k"; continue; }
  for try in 1 2 3; do
    timeout 900 gpu5070 render art/build/sc_$k.py --frames ${FR[$k]} --engine eevee --wait-busy 30 --out art/out/scenery/$k > art/build/sc_$k.log 2>&1 && break
    grep -q "unreachable\|not answering" art/build/sc_$k.log && gpu5070 wake >/dev/null 2>&1
    grep -q "failed" art/build/sc_$k.log && { echo "FAIL $k"; grep -m3 Error art/build/sc_$k.log; break; }
    sleep 30
  done
  grep -q "Look at a frame" art/build/sc_$k.log && .venv/bin/python tools/pack_scenery.py $k
done; done
