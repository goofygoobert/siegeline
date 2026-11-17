"""Bundle art/blender/kit.py (+ optional --lib files) + one script into a single bpy script for gpu5070.
Usage: bundle_blend.py SCRIPT OUT [--lib art/blender/scenery.py ...]"""
import sys, pathlib, re
root = pathlib.Path(__file__).resolve().parents[1] / "art" / "blender"
args = sys.argv[1:]; libs = []
while "--lib" in args:
    i = args.index("--lib"); libs.append(pathlib.Path(args[i + 1])); del args[i:i + 2]
src = pathlib.Path(args[0]); out = pathlib.Path(args[1])
strip = lambda t: re.sub(r"^from (kit|scenery|\w+_lib) import \*\s*$", "", t, flags=re.M)
parts = [(root / "kit.py").read_text()] + [strip(l.read_text()) for l in libs] + [strip(src.read_text())]
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n\n# ----\n".join(parts))
print(out)
