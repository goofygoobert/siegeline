"""Bundle art/blender/kit.py + one character/background script into a single bpy script for gpu5070."""
import sys, pathlib, re
root = pathlib.Path(__file__).resolve().parents[1] / "art" / "blender"
src = pathlib.Path(sys.argv[1]); out = pathlib.Path(sys.argv[2])
kit = (root / "kit.py").read_text()
body = re.sub(r"^from kit import \*\s*$", "", src.read_text(), flags=re.M)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(kit + "\n# ---- " + src.name + "\n" + body)
print(out)
