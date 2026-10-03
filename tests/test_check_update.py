import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_update.py"

# 假的 npx：收到 update --path <目录> 时把那里的版本号改成 99.0.0，并记下调用
FAKE_NPX = """#!/bin/sh
echo "$@" >> "$FAKE_NPX_LOG"
[ -n "$FAKE_NPX_FAIL" ] && exit 1
while [ $# -gt 0 ]; do
  if [ "$1" = "--path" ]; then sed -i.bak 's/version: "0.10.0"/version: "99.0.0"/' "$2/SKILL.md"; fi
  shift
done
"""


class Versions(BaseHTTPRequestHandler):
    payload = {}
    hits = 0

    def do_GET(self):
        Versions.hits += 1
        body = json.dumps(Versions.payload).encode()
        self.send_response(200 if self.path == "/api/store/versions" else 404)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


@unittest.skipIf(sys.platform == "win32", "假 npx 是 shell 脚本")
class CheckUpdateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), Versions)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.skill = self.tmp / "skills" / "oil-ui-pro"
        (self.skill / "scripts").mkdir(parents=True)
        shutil.copy(SCRIPT, self.skill / "scripts" / "check_update.py")
        (self.skill / "SKILL.md").write_text('---\nname: oil-ui-pro\nmetadata:\n  version: "0.10.0"\n---\n', encoding="utf-8")
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        (bin_dir / "npx").write_text(FAKE_NPX, encoding="utf-8")
        (bin_dir / "npx").chmod(0o755)
        self.bin = bin_dir
        self.npx_log = self.tmp / "npx.log"
        Versions.hits = 0
        self.set_latest("99.0.0", free=False)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def set_latest(self, version, free):
        entry = {"latest": version, "history": [{"version": version, "notes": "- 动效改成三处基本动效。\n- 其他修正"}]}
        if free:
            entry["download_url"] = "https://example.com/oil-ui-pro.tar.gz"
        Versions.payload = {"skills": {"oil-ui-pro": entry}}

    def login(self):
        config = self.tmp / "config" / "oil"
        config.mkdir(parents=True)
        (config / "config.json").write_text(json.dumps({"token": "oil_test", "email": "a@example.com"}), encoding="utf-8")

    def run_check(self, api=None, **extra):
        env = {k: v for k, v in os.environ.items() if not k.startswith("OIL_")}
        env.update(XDG_STATE_HOME=str(self.tmp / "state"), XDG_CONFIG_HOME=str(self.tmp / "config"),
                   PATH=f"{self.bin}{os.pathsep}{os.environ['PATH']}", FAKE_NPX_LOG=str(self.npx_log),
                   OIL_API=api or f"http://127.0.0.1:{self.server.server_port}")
        env.update(extra)
        script = self.skill / "scripts" / "check_update.py"
        return subprocess.run([sys.executable, str(script)], capture_output=True, text=True, env=env, timeout=30).stdout

    def npx_calls(self):
        return self.npx_log.read_text(encoding="utf-8").splitlines() if self.npx_log.exists() else []

    def test_logged_in_paid_skill_updates_itself(self):
        self.login()
        out = self.run_check()
        self.assertIn("oil-ui-pro 已自动更新到 99.0.0（原来是 0.10.0）：动效改成三处基本动效。", out)
        self.assertIn(f"update oil-ui-pro --path {self.skill}", self.npx_calls()[0])
        self.assertIn('version: "99.0.0"', (self.skill / "SKILL.md").read_text(encoding="utf-8"))
        self.assertEqual(self.run_check(), "")

    def test_free_skill_updates_without_login(self):
        self.set_latest("99.0.0", free=True)
        self.assertIn("已自动更新到 99.0.0", self.run_check())

    def test_paid_skill_without_login_only_notifies_once_a_day(self):
        out = self.run_check()
        self.assertIn("oil-ui-pro 有新版本 99.0.0（当前 0.10.0）：动效改成三处基本动效。", out)
        self.assertIn("npx github:oil-oil/oil-cli update oil-ui-pro", out)
        self.assertEqual(self.npx_calls(), [])
        self.assertEqual(self.run_check(), "")
        self.assertEqual(Versions.hits, 1)

    def test_failed_update_falls_back_to_notice(self):
        self.login()
        out = self.run_check(FAKE_NPX_FAIL="1")
        self.assertIn("有新版本 99.0.0", out)
        self.assertEqual(len(self.npx_calls()), 1)
        self.assertEqual(self.run_check(FAKE_NPX_FAIL="1"), "")
        self.assertEqual(len(self.npx_calls()), 1)

    def test_auto_update_can_be_turned_off(self):
        self.login()
        self.assertIn("有新版本 99.0.0", self.run_check(OIL_NO_AUTO_UPDATE="1"))
        self.assertEqual(self.npx_calls(), [])

    def test_silent_when_up_to_date_offline_disabled_or_in_a_checkout(self):
        self.set_latest("0.0.1", free=False)
        self.assertEqual(self.run_check(), "")
        self.set_latest("99.0.0", free=False)
        self.assertEqual(self.run_check(api="http://127.0.0.1:9", XDG_STATE_HOME=str(self.tmp / "s2")), "")
        self.assertEqual(self.run_check(OIL_NO_UPDATE_CHECK="1", XDG_STATE_HOME=str(self.tmp / "s3")), "")
        (self.skill / ".git").mkdir()
        self.assertEqual(self.run_check(XDG_STATE_HOME=str(self.tmp / "s4")), "")


if __name__ == "__main__":
    unittest.main()
