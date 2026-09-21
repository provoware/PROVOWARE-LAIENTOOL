from __future__ import annotations
import hashlib, json, os, shutil, subprocess, tempfile, unittest
from pathlib import Path
from zipfile import ZipFile
from scripts.build_portable_zip import PACKAGE_ROOT, build_zip, verify_zip

class I32PortablePackageTests(unittest.TestCase):
    def test_reproducible_and_manifested(self):
        with tempfile.TemporaryDirectory() as t:
            a=build_zip(Path(t)/"a.zip"); b=build_zip(Path(t)/"b.zip")
            self.assertEqual(a.read_bytes(),b.read_bytes()); verify_zip(a)
            with ZipFile(a) as z:
                m=json.loads(z.read(f"{PACKAGE_ROOT}/PACKAGE_MANIFEST.json"))
                self.assertFalse(m["contains_venv"]); self.assertEqual(m["canonical_entrypoint"],"start.sh")
                self.assertFalse(any("/.venv/" in n or "/.git/" in n or "__pycache__" in n for n in z.namelist()))

    def test_foreign_unicode_path_help_and_check_are_offline_fail_closed(self):
        with tempfile.TemporaryDirectory() as t:
            base=Path(t); arc=build_zip(base/"p.zip"); dest=base/"Fremder Pfad äöü"/"Unter Ordner"; dest.mkdir(parents=True); shutil.unpack_archive(str(arc),str(dest)); pkg=dest/PACKAGE_ROOT
            env=dict(os.environ); env.update({"PIP_NO_INDEX":"1","http_proxy":"http://127.0.0.1:9","https_proxy":"http://127.0.0.1:9","HTTP_PROXY":"http://127.0.0.1:9","HTTPS_PROXY":"http://127.0.0.1:9"})
            before=sorted(p.relative_to(pkg).as_posix() for p in pkg.rglob("*"))
            h=subprocess.run(["bash",str(pkg/"start.sh"),"--help"],cwd=base,env=env,text=True,capture_output=True,timeout=20)
            self.assertEqual(h.returncode,0); self.assertIn("PROVOWARE Venv-Starter",h.stdout)
            c=subprocess.run(["bash",str(pkg/"start.sh"),"--check"],cwd=base,env=env,text=True,capture_output=True,timeout=20)
            self.assertEqual(c.returncode,3); self.assertIn("Nichts verändert",c.stderr); self.assertFalse((pkg/".venv").exists())
            after=sorted(p.relative_to(pkg).as_posix() for p in pkg.rglob("*")); self.assertEqual(before,after)

    def test_desktop_launcher_only_delegates_to_start_sh(self):
        with tempfile.TemporaryDirectory() as t:
            arc=build_zip(Path(t)/"p.zip")
            with ZipFile(arc) as z: s=z.read(f"{PACKAGE_ROOT}/PROVOWARE.desktop").decode()
            for x in ("start.sh","--gui","%k"): self.assertIn(x,s)
            for x in ("python3 start.py","sudo ","apt install","curl ","wget "): self.assertNotIn(x,s)
if __name__=="__main__": unittest.main()
