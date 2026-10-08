"""GitHub Action driver: CI emulation plus git helpers, one file.

CI, lanes, and local runs must never disagree about what "green"
means. The ``check`` path is stdlib-only (plain subprocesses over a
committed gate table) so CI runners without the foundry package get
byte-identical verdicts; a parity test against ``foundry.gates``
guards the shared semantics. The git side reuses ``submit.py`` guards
so automation stages, pushes, and opens PRs exactly like a lane would.
Canonical source: Foundry repository, tools/gh_action.py — copies
elsewhere must be refreshed from here, never edited in place.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

DEFAULT_GATES_FILE = "ci-gates.json"


def default_gate_table() -> list[dict[str, str]]:
    """Canonical gate table, sourced from Foundry's own gate defaults.

    Imported — never copied — so `foundry gates run` and this driver
    cannot drift apart.
    """
    from foundry.config import GatesConfig

    return [{"name": name, "command": command} for name, command in GatesConfig().as_list()]


def load_gate_table(path: Path | None) -> list[dict[str, str]]:
    """Load a repo-committed gate table, or fall back to the defaults."""
    if path is None:
        return default_gate_table()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"cannot read gate table {path}: {exc}") from exc
    gates = payload.get("gates") if isinstance(payload, dict) else None
    if not isinstance(gates, list) or not gates:
        raise ValueError(f"gate table {path} needs a non-empty 'gates' list")
    table: list[dict[str, str]] = []
    for entry in gates:
        if not isinstance(entry, dict):
            raise ValueError(f"gate table {path} entries must be objects")
        name, command = entry.get("name"), entry.get("command")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"gate table {path} entry needs a name")
        if not isinstance(command, str) or not command.strip():
            raise ValueError(f"gate table {path} entry {name!r} needs a command")
        table.append({"name": name.strip(), "command": command.strip()})
    return table


def _resolve_executable(workdir: Path, argv: list[str]) -> list[str]:
    """Prefer <workdir>/.venv binaries (lanes/CI install the toolchain there)."""
    if not argv:
        return argv
    venv_bin = workdir / ".venv" / "bin" / Path(argv[0]).name
    if venv_bin.is_file():
        return [str(venv_bin), *argv[1:]]
    return argv


def _run_one(workdir: Path, name: str, command: str) -> dict[str, Any]:
    """Run one gate command; fail closed on timeouts, crashes, vacuity."""
    import shlex
    import time as _time

    try:
        argv = shlex.split(command)
    except ValueError as exc:
        return {
            "name": name,
            "passed": False,
            "exit_code": 127,
            "duration_s": 0.0,
            "stdout_tail": "",
            "stderr_tail": f"invalid gate command: {exc}",
        }
    if not argv:
        return {
            "name": name,
            "passed": False,
            "exit_code": 127,
            "duration_s": 0.0,
            "stdout_tail": "",
            "stderr_tail": "empty gate command",
        }
    argv = _resolve_executable(workdir, argv)
    started = _time.monotonic()
    try:
        proc = subprocess.run(argv, cwd=workdir, capture_output=True, text=True, timeout=600)
        duration = _time.monotonic() - started
        passed = proc.returncode == 0
        stdout, stderr = proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return {
            "name": name,
            "passed": False,
            "exit_code": 124,
            "duration_s": 600.0,
            "stdout_tail": "",
            "stderr_tail": "gate timed out after 600s",
        }
    except OSError as exc:
        return {
            "name": name,
            "passed": False,
            "exit_code": 127,
            "duration_s": 0.0,
            "stdout_tail": "",
            "stderr_tail": f"gate execution failed: {exc}",
        }
    if name == "test" and passed and "no tests ran" in stdout.lower():
        stderr = (stderr + "\ntest gate passed vacuously: no tests ran").strip()
        return {
            "name": name,
            "passed": False,
            "exit_code": 1,
            "duration_s": duration,
            "stdout_tail": stdout[-2000:],
            "stderr_tail": stderr[-2000:],
        }
    return {
        "name": name,
        "passed": passed,
        "exit_code": proc.returncode,
        "duration_s": duration,
        "stdout_tail": stdout[-2000:],
        "stderr_tail": stderr[-2000:],
    }


def run_checks(
    workdir: Path, gates: list[dict[str, str]], only: tuple[str, ...] = ()
) -> dict[str, Any]:
    """Run the gate table with plain subprocesses; stdlib only.

    Deliberately independent of ``foundry.gates`` so CI runners without
    the foundry package get byte-identical verdicts: same commands, same
    pass/fail rule (nonzero fails), same vacuous-test guard. Toolchain
    differences (venv vs ambient) are resolved per gate, never guessed.
    """
    selected = [g for g in gates if not only or g["name"] in only]
    if not selected:
        raise ValueError("gate selection matched nothing")
    results = [_run_one(workdir, gate["name"], gate["command"]) for gate in selected]
    return {"passed": all(g["passed"] for g in results), "gates": results}


# ---------------------------------------------------------------------------
# Git helpers (same guards as submit.py, no duplicated policy)
# ---------------------------------------------------------------------------

_PROTECTED = ("main", "master")


def _git(workdir: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=workdir,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def current_branch(workdir: Path) -> str:
    """Current branch name (empty when detached)."""
    return _git(workdir, "branch", "--show-current")


def assert_feature_branch(branch: str) -> None:
    """Refuse protected branches; mirrors submit's protected-branch guard."""
    if branch in _PROTECTED or not branch:
        raise ValueError(f"refusing git operation on protected branch {branch!r}")


def commit_changes(workdir: Path, message: str, dry_run: bool = False) -> str:
    """Stage committable paths and commit; returns the new HEAD SHA.

    Junk filtering reuses ``submit.stage_paths`` so automation stages
    exactly what a lane would stage.
    """
    from foundry.submit import stage_paths

    branch = current_branch(workdir)
    assert_feature_branch(branch)
    status = _git(workdir, "status", "--porcelain")
    candidates = [line[3:] for line in status.splitlines() if len(line) > 3 and line[:2].strip()]
    paths = stage_paths(candidates)
    if not paths:
        raise ValueError("nothing committable in the workspace")
    if dry_run:
        return f"dry-run: would commit {len(paths)} paths on {branch}"
    _git(workdir, "add", "--", *paths)
    _git(workdir, "commit", "-m", message)
    return _git(workdir, "rev-parse", "HEAD")


def push_branch(
    workdir: Path, branch: str = "", remote: str = "origin", dry_run: bool = False
) -> str:
    """Push exactly once (``-u origin <branch>``); never main."""
    target = branch or current_branch(workdir)
    assert_feature_branch(target)
    if dry_run:
        return f"dry-run: would push -u {remote} {target}"
    _git(workdir, "push", "-u", remote, target)
    return target


def open_pull_request(
    api_base: str,
    token: str,
    repo: str,
    title: str,
    head: str,
    base: str,
    body: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Open a PR, adopting the existing one when the branch already has it.

    Mirrors submit's duplicate guard: list-then-create, never two PRs.
    """
    from foundry import github as _github

    assert_feature_branch(head)
    if dry_run:
        return {"dry_run": True, "head": head, "base": base, "title": title}
    existing = _github.list_open_pulls(api_base, token, repo, head)
    if existing:
        pull = existing[0]
        return {"number": pull.number, "url": pull.url, "adopted": True}
    pull = _github.create_pull(api_base, token, repo, title, head, base, body)
    return {"number": pull.number, "url": pull.url, "adopted": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="gh_action", description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    p_check = sub.add_parser("check", help="Run the gate table like CI would.")
    p_check.add_argument("--workdir", required=True)
    p_check.add_argument("--gates-file", default=None)
    p_check.add_argument("--only", default="")
    p_check.add_argument("--json-out", default=None)
    p_commit = sub.add_parser("commit", help="Stage and commit workspace changes.")
    p_commit.add_argument("--workdir", required=True)
    p_commit.add_argument("--message", required=True)
    p_commit.add_argument("--dry-run", action="store_true")
    p_push = sub.add_parser("push", help="Push the feature branch once.")
    p_push.add_argument("--workdir", required=True)
    p_push.add_argument("--branch", default="")
    p_push.add_argument("--remote", default="origin")
    p_push.add_argument("--dry-run", action="store_true")
    p_pr = sub.add_parser("pr", help="Open (or adopt) the pull request.")
    p_pr.add_argument("--api-base", required=True)
    p_pr.add_argument("--repo", required=True)
    p_pr.add_argument("--title", required=True)
    p_pr.add_argument("--head", required=True)
    p_pr.add_argument("--base", required=True)
    p_pr.add_argument("--body", default="")
    p_pr.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    import os

    if args.action == "check":
        table = load_gate_table(Path(args.gates_file) if args.gates_file else None)
        only = tuple(part for part in args.only.split(",") if part.strip())
        try:
            record = run_checks(Path(args.workdir), table, only)
        except ValueError as exc:
            print(f"error: {exc}")
            return 1
        text = json.dumps(record, indent=2, sort_keys=True)
        if args.json_out:
            Path(args.json_out).write_text(text + "\n", encoding="utf-8")
        else:
            print(text)
        return 0 if record["passed"] else 1
    if args.action == "commit":
        try:
            print(commit_changes(Path(args.workdir), args.message, args.dry_run))
        except (ValueError, RuntimeError) as exc:
            print(f"error: {exc}")
            return 1
        return 0
    if args.action == "push":
        try:
            print(push_branch(Path(args.workdir), args.branch, args.remote, args.dry_run))
        except (ValueError, RuntimeError) as exc:
            print(f"error: {exc}")
            return 1
        return 0
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token and not args.dry_run:
        print("error: GITHUB_TOKEN is not set")
        return 1
    try:
        result = open_pull_request(
            args.api_base,
            token,
            args.repo,
            args.title,
            args.head,
            args.base,
            args.body,
            args.dry_run,
        )
    except Exception as exc:
        print(f"error: {exc}")
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
