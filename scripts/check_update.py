#!/usr/bin/env python3
"""检查本 Skill 有没有新版本，有就自动更新。

每天最多联网一次，只请求 ui.oiloil.org 公开的版本列表，不发送任何信息。
发现新版本时用 oil 命令行（npx github:oil-oil/oil-cli）原地更新本目录：
成功打印一行“已自动更新”，不能自动更新时打印一行提示，同一个新版本每天最多提示一次；
没有新版本、网络失败或在开发目录（含 .git）里运行时什么也不输出。
设置环境变量 OIL_NO_UPDATE_CHECK=1 关闭检查，OIL_NO_AUTO_UPDATE=1 只提示不自动更新。
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = os.environ.get("OIL_API", "https://ui.oiloil.org").rstrip("/")
CLI = "github:oil-oil/oil-cli"
DAY = 24 * 3600
RETRY_AFTER_FAILURE = 3600
UPDATE_TIMEOUT = 300


def read_skill() -> tuple[str, str] | None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    name = re.search(r"^name:\s*\"?([\w-]+)\"?\s*$", text, re.MULTILINE)
    version = re.search(r"^\s+version:\s*\"?(\d+\.\d+\.\d+)\"?\s*$", text, re.MULTILINE)
    if not name or not version:
        return None
    return name.group(1), version.group(1)


def state_path(name: str) -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    else:
        base = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local" / "state")
    return base / "oil" / f"{name}-update.json"


def logged_in() -> bool:
    if os.environ.get("OIL_TOKEN"):
        return True
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    try:
        return bool(json.loads((base / "oil" / "config.json").read_text(encoding="utf-8")).get("token"))
    except (OSError, ValueError, AttributeError):
        return False


def load(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save(path: Path, data: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def parse(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def fetch(name: str) -> dict | None:
    request = urllib.request.Request(f"{API}/api/store/versions", headers={"User-Agent": "oil-skill-update-check"})
    with urllib.request.urlopen(request, timeout=3) as response:
        entry = json.load(response).get("skills", {}).get(name)
    if not isinstance(entry, dict) or not re.fullmatch(r"\d+\.\d+\.\d+", str(entry.get("latest", ""))):
        return None
    history = entry.get("history") or []
    notes = next((h.get("notes", "") for h in history if h.get("version") == entry["latest"]), "")
    # 免费版的版本信息带公开下载地址，付费版没有
    return {"latest": entry["latest"], "notes": notes, "free": bool(entry.get("download_url"))}


def headline(notes: str) -> str:
    for line in notes.splitlines():
        line = re.sub(r"^[#>*\-\s]+", "", line).strip().rstrip("。.；;，,")
        if line:
            return line if len(line) <= 60 else line[:59] + "…"
    return ""


def auto_update(name: str, latest: str, free: bool) -> bool:
    if os.environ.get("OIL_NO_AUTO_UPDATE") or not (free or logged_in()):
        return False
    npx = shutil.which("npx")
    if not npx:
        return False
    # CI=1 让命令行在没登录时直接失败，不会停下来等浏览器确认
    env = {**os.environ, "CI": "1"}
    try:
        subprocess.run([npx, "-y", CLI, "update", name, "--path", str(ROOT), "--json"], env=env,
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=UPDATE_TIMEOUT, check=False)
    except (OSError, subprocess.SubprocessError):
        return False
    skill = read_skill()
    return bool(skill) and skill[1] == latest


def main() -> int:
    if os.environ.get("OIL_NO_UPDATE_CHECK") or (ROOT / ".git").exists():
        return 0
    skill = read_skill()
    if not skill:
        return 0
    name, current = skill
    path = state_path(name)
    state = load(path)
    now = time.time()

    if now - float(state.get("checked_at", 0)) >= DAY:
        try:
            found = fetch(name)
        except Exception:
            found = None
        if found:
            state.update(found)
            state["checked_at"] = now
        else:
            # 失败时把检查时间记成 23 小时前，一小时后再试
            state["checked_at"] = now - DAY + RETRY_AFTER_FAILURE
        save(path, state)

    latest = state.get("latest")
    if not isinstance(latest, str) or not re.fullmatch(r"\d+\.\d+\.\d+", latest) or parse(latest) <= parse(current):
        return 0
    summary = headline(state.get("notes", ""))
    detail = f"：{summary}" if summary else ""

    # 同一个新版本自动更新失败后，一天内不再重试
    if state.get("auto_failed_version") != latest or now - float(state.get("auto_failed_at", 0)) >= DAY:
        if auto_update(name, latest, bool(state.get("free"))):
            print(f"{name} 已自动更新到 {latest}（原来是 {current}）{detail}。请重新读取 SKILL.md 再继续。")
            return 0
        state["auto_failed_version"], state["auto_failed_at"] = latest, now
        save(path, state)

    if state.get("notified_version") == latest and now - float(state.get("notified_at", 0)) < DAY:
        return 0
    state["notified_version"], state["notified_at"] = latest, now
    save(path, state)
    print(f"{name} 有新版本 {latest}（当前 {current}）{detail}。"
          f"在终端运行 npx {CLI} update {name} 即可更新。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
