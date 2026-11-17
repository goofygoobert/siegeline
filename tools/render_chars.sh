#!/bin/bash
# Usage: tools/render_chars.sh JOB [JOB...]      JOB = units | field | boss | ui   (see art/blender/cast.py)
#        tools/render_chars.sh one:ID[,ID...]    quick preview of a few ids (uses the first id's job layout)
# Bundles kit + cast + every character script into ONE bpy script, compile-checks it, renders the whole job
# as one EEVEE animation on the 5070 (all characters on a grid). Review sheets: tools/pack_sprites.py --sheets
cd "$(dirname "$0")/.."
CHARS=$(ls art/blender/chars/_*.py; ls art/blender/chars/*.py | grep -v '/_' | grep -v -E '/(a|b|c)_[a-z]+\.py$')
LIBS=""; for f in art/blender/cast.py art/blender/kit2.py $CHARS; do LIBS="$LIBS --lib $f"; done
mkdir -p art/build art/out
OLDCHARS=$(echo "$CHARS" | tr ' ' '\n' | grep -v '/v2_')
declare -A MINE=([look_h1]="torchbow cinder_runner bellringer" [look_h2]="maulwright lamplighter marshal" [look_h3]="gnawer spitter bloater" [look_h4]="brute husk_warden" [look_boss]="cinder_matron" [look]="ashguard husk")
for J in "$@"; do
  # a helper's test job bundles only that helper's own new files, so one broken file cannot stop the others
  if [[ -n "${MINE[$J]}" ]]; then
    LIBS=""; for f in art/blender/cast.py art/blender/kit2.py $OLDCHARS; do LIBS="$LIBS --lib $f"; done
    for id in ${MINE[$J]}; do [ -f art/blender/chars/v2_$id.py ] && LIBS="$LIBS --lib art/blender/chars/v2_$id.py"; done
  fi
  if [[ $J == one:* ]]; then
    ids=${J#one:}; name="one_${ids//,/_}"
    job=$(python3 -c "import sys;sys.path.insert(0,'art/blender');import cast;i='$ids'.split(',')[0];print(next(k for k,v in cast.JOBS.items() if i in v['ids']))")
    echo "render_job('$job', only=[$(echo $ids | sed "s/[^,]*/'&'/g")])" > art/build/drv_$name.py
    N=$(python3 -c "import sys;sys.path.insert(0,'art/blender');import cast;print(max(sum(a[1] for a in cast.anims_of(i)) for i in '$ids'.split(',')))")
  else
    name=$J
    echo "render_job('$J')" > art/build/drv_$name.py
    N=$(python3 -c "import sys;sys.path.insert(0,'art/blender');import cast;print(cast.job_frames('$J'))")
  fi
  python3 tools/bundle_blend.py art/build/drv_$name.py art/build/$name.py $LIBS >/dev/null
  python3 -m py_compile art/build/$name.py || { echo "SYNTAX $name"; continue; }
  rm -rf art/out/$name
  for try in 1 2 3; do
    timeout 1500 gpu5070 render art/build/$name.py --frames 1-$N --engine eevee --wait-busy 60 --out art/out/$name > art/build/$name.log 2>&1 && break
    grep -q "unreachable\|not answering" art/build/$name.log && gpu5070 wake >/dev/null 2>&1
    echo "retry $name ($try)"; sleep 60
  done
  if ls art/out/$name/frame_*.png >/dev/null 2>&1; then
    echo "OK $name ($(ls art/out/$name/frame_*.png | wc -l)/$N frames)"; grep -E "FAILED|Error|JOB " art/build/$name.log | head -20
  else
    echo "FAIL $name"; tail -5 art/build/$name.log
  fi
done
