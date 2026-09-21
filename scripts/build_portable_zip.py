#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, stat, subprocess
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT=Path(__file__).resolve().parents[1]
PACKAGE_ROOT="PROVOWARE-LAIENTOOL"
ROOT_FILES=("README.md","AGENTS.md","PROVOWARE_TODO_INPUT_POOL0.md","todo.txt","start.sh","start.py","requirements-gui.txt")
TREE_ROOTS=("src","scripts","docs")
EXCLUDED={"__pycache__",".venv","venv","build","dist",".git"}
DESKTOP='''[Desktop Entry]
Type=Application
Name=PROVOWARE LAIENTOOL
Comment=PROVOWARE über start.sh starten
Terminal=false
TryExec=bash
Categories=Utility;
Exec=bash -c "launcher_dir=\\$(dirname \\"\\$1\\"); exec \\"\\$launcher_dir/start.sh\\" --gui" _ %k
'''

def commit_id():
    r=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,text=True,capture_output=True,check=False)
    return r.stdout.strip() if r.returncode==0 and r.stdout.strip() else "unknown"

def files():
    out=[]
    for rel in ROOT_FILES:
        p=ROOT/rel
        if not p.is_file(): raise FileNotFoundError(rel)
        out.append(p)
    for top in TREE_ROOTS:
        for p in sorted((ROOT/top).rglob("*")):
            if not p.is_file() or p.is_symlink(): continue
            rel=p.relative_to(ROOT)
            if any(part in EXCLUDED for part in rel.parts) or p.suffix in {".pyc",".pyo",".zip"}: continue
            out.append(p)
    unique={p.relative_to(ROOT).as_posix():p for p in out}
    return [unique[k] for k in sorted(unique)]

def digest(data): return hashlib.sha256(data).hexdigest()

def zi(name, executable=False):
    info=ZipInfo(name,(1980,1,1,0,0,0)); info.compress_type=ZIP_DEFLATED; info.create_system=3
    info.external_attr=(stat.S_IFREG | (0o755 if executable else 0o644)) << 16
    return info

def build_zip(output):
    src=files(); entries=[]
    for p in src:
        rel=p.relative_to(ROOT).as_posix(); data=p.read_bytes()
        entries.append({"path":rel,"size_bytes":len(data),"sha256":digest(data),"executable":rel=="start.sh"})
    ld=DESKTOP.encode()
    entries.append({"path":"PROVOWARE.desktop","size_bytes":len(ld),"sha256":digest(ld),"executable":True})
    entries.sort(key=lambda x:x["path"])
    manifest={"schema_version":"1","package_kind":"portable-source-zip","source_commit":commit_id(),"canonical_entrypoint":"start.sh","contains_venv":False,"contains_bundled_gui_dependencies":False,"files":entries}
    mb=(json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode()
    output=Path(output); output.parent.mkdir(parents=True,exist_ok=True); tmp=output.with_suffix(output.suffix+".tmp"); tmp.unlink(missing_ok=True)
    with ZipFile(tmp,"w",compression=ZIP_DEFLATED,compresslevel=9) as z:
        for p in src:
            rel=p.relative_to(ROOT).as_posix()
            z.writestr(zi(f"{PACKAGE_ROOT}/{rel}",rel=="start.sh"),p.read_bytes(),compresslevel=9)
        z.writestr(zi(f"{PACKAGE_ROOT}/PROVOWARE.desktop",True),ld,compresslevel=9)
        z.writestr(zi(f"{PACKAGE_ROOT}/PACKAGE_MANIFEST.json"),mb,compresslevel=9)
    tmp.replace(output); return output

def verify_zip(path):
    with ZipFile(path) as z:
        names=z.namelist()
        if names!=sorted(names): raise RuntimeError("ZIP-Dateiliste nicht sortiert")
        if any(any(x in n for x in ("/.venv/","/.git/","/dist/","/build/","__pycache__")) for n in names): raise RuntimeError("verbotene Paketreste")
        mn=f"{PACKAGE_ROOT}/PACKAGE_MANIFEST.json"; sn=f"{PACKAGE_ROOT}/start.sh"; dn=f"{PACKAGE_ROOT}/PROVOWARE.desktop"
        for req in (mn,sn,dn):
            if req not in names: raise RuntimeError(f"Pflichtdatei fehlt: {req}")
        m=json.loads(z.read(mn))
        for e in m["files"]:
            data=z.read(f"{PACKAGE_ROOT}/{e['path']}")
            if len(data)!=e["size_bytes"] or digest(data)!=e["sha256"]: raise RuntimeError(f"Manifestabweichung: {e['path']}")
        if not ((z.getinfo(sn).external_attr>>16)&stat.S_IXUSR): raise RuntimeError("start.sh nicht ausführbar")
        launcher=z.read(dn).decode()
        for marker in ("start.sh","--gui","%k"):
            if marker not in launcher: raise RuntimeError(f"Launcher-Vertrag fehlt: {marker}")
        if any(x in launcher for x in ("sudo ","apt install","curl ","wget ")): raise RuntimeError("Launcher enthält verbotenen Aufruf")

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,default=ROOT/"dist/PROVOWARE-LAIENTOOL-portable.zip"); p.add_argument("--verify-only",type=Path); a=p.parse_args(argv)
    if a.verify_only:
        verify_zip(a.verify_only); print(f"🟢 Portable-ZIP geprüft: {a.verify_only}"); return 0
    out=build_zip(a.output.resolve()); verify_zip(out); print(f"🟢 Portable-ZIP erstellt: {out}"); print(f"SHA-256: {digest(out.read_bytes())}"); return 0
if __name__=="__main__": raise SystemExit(main())
