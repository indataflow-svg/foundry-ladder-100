"""GitHub Action driver: CI emulation plus git helpers, one file.

CI, lanes, and local runs must never disagree about what "green"
means. The whole file is stdlib-only so CI runners and lane
workspaces without the foundry package run it verbatim; parity tests
against ``foundry.gates``, ``foundry.runner``, ``foundry.github``,
and ``foundry.submit`` guard the shared semantics.
Canonical source: Foundry repository, tools/gh_action.py — copies
elsewhere must be refreshed from here, never edited in place.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_GATES_FILE = "ci-gates.json"


def default_gate_table() -> list[dict[str, str]]:
    """Canonical gate table, pinned to Foundry's own gate defaults.

    Inlined (not imported): vendored contexts have no foundry package
    and the builder-validity gate forbids third-party imports the
    workspace venv cannot satisfy. The parity test
    ``test_defaults_match_foundry_gates`` fails loudly on any drift.
    """
    return [
        {"name": "test", "command": "pytest -q --cov=src --cov-report=term-missing"},
        {"name": "coverage", "command": "pytest -q --cov=src --cov-report=term-missing"},
        {"name": "lint", "command": "ruff check ."},
        {"name": "format", "command": "ruff format --check ."},
        {"name": "typecheck", "command": "mypy src"},
        {"name": "security", "command": "bandit -r src -q"},
        {"name": "secrets", "command": "detect-secrets scan --baseline .secrets.baseline"},
        {"name": "diffcheck", "command": "git diff --check"},
    ]


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
            raise ValueError(f"gate table {path} entries must be objects")  # noqa: TRY004 - ValueError is the pinned public error type here.
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
        proc = subprocess.run(
            argv, cwd=workdir, capture_output=True, text=True, timeout=600, check=False
        )
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

#: Branches Foundry must never mutate. Mirrors
#: ``foundry.github.is_protected_branch`` (this file is stdlib-only and
#: vendored, so it cannot import it — keep the two in sync; the parity
#: test in ``tests/test_gh_action.py`` enforces it).
_PROTECTED_EXACT = ("main", "master")
_PROTECTED_PREFIXES = ("main/", "master/")


def is_protected_branch(name: str) -> bool:
    """True for branches automation must never mutate or push onto."""
    return name in _PROTECTED_EXACT or name.startswith(_PROTECTED_PREFIXES)


def _github_token() -> str | None:
    """Read the GitHub token from the environment (stdlib mirror of
    ``FoundryConfig.github_token``): stripped, empty means unset, never
    logged, never stored in files."""
    value = os.environ.get("GITHUB_TOKEN", "").strip()
    return value or None


def _git(workdir: Path, *args: str, token: str | None = None) -> str:
    """Run git with ambient credentials stripped.

    Mirrors ``workspace.run_git`` semantics within stdlib limits: the
    token never appears in argv; when given it rides a GIT_CONFIG
    ``http.extraHeader`` entry scoped to the child process only.
    """
    import base64

    env = dict(os.environ)
    env.pop("GITHUB_TOKEN", None)
    env.pop("GH_TOKEN", None)
    if token:
        credential = base64.b64encode(f"x-access-token:{token}".encode()).decode()
        env["GIT_CONFIG_COUNT"] = "1"
        env["GIT_CONFIG_KEY_0"] = "http.extraHeader"
        env["GIT_CONFIG_VALUE_0"] = f"Authorization: Basic {credential}"
    proc = subprocess.run(
        ["git", *args],
        cwd=workdir,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env=env,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def current_branch(workdir: Path) -> str:
    """Current branch name (empty when detached)."""
    return _git(workdir, "branch", "--show-current")


def _porcelain_paths(status: str) -> list[str]:
    """Repo-relative paths from ``git status --porcelain`` output.

    Mirrors ``foundry.runner._porcelain_paths`` (stdlib-only copy — keep
    the two in sync; parity test enforces it). ``_git`` strips stdout,
    which eats a leading space on the first line (`` M p`` → ``M p``);
    a fixed ``line[3:]`` offset would then eat one path character.
    Parse the ``XY `` prefix by shape instead.
    """
    paths: list[str] = []
    for line in status.splitlines():
        if len(line) > 3 and line[2] == " ":  # "XY path" (normal)
            path = line[3:]
        elif len(line) > 2 and line[1] == " " and line[0] in "MDATRCU?!":
            path = line[2:]  # "Y path": X was the space stripping removed
        else:
            continue
        path = path.strip().strip('"')
        if path:
            paths.append(path)
    return paths


def assert_feature_branch(branch: str) -> None:
    """Refuse protected branches; mirrors submit's protected-branch guard."""
    if not branch or is_protected_branch(branch):
        raise ValueError(f"refusing git operation on protected branch {branch!r}")


def commit_changes(workdir: Path, message: str, dry_run: bool = False) -> str:
    """Stage committable paths and commit; returns the new HEAD SHA.

    Junk filtering mirrors ``submit.stage_paths`` (local copy — the
    vendored contexts where this driver runs have no foundry package,
    and the builder-validity gate forbids third-party imports the
    workspace venv cannot satisfy; a parity test pins the two).
    """
    branch = current_branch(workdir)
    assert_feature_branch(branch)
    status = _git(workdir, "status", "--porcelain")
    candidates = _porcelain_paths(status)
    paths = _stage_paths(candidates)
    if not paths:
        raise ValueError("nothing committable in the workspace")
    if dry_run:
        return f"dry-run: would commit {len(paths)} paths on {branch}"
    _git(workdir, "add", "--", *paths)
    _git(workdir, "commit", "-m", message)
    return _git(workdir, "rev-parse", "HEAD")


def push_branch(
    workdir: Path,
    branch: str = "",
    remote: str = "origin",
    dry_run: bool = False,
    token: str | None = None,
) -> str:
    """Push exactly once (``-u origin <branch>``); never main.

    Auth rides the same header-injection path as the central boundary;
    ``None`` falls back to the ambient ``GITHUB_TOKEN`` (stripped), and
    a missing token keeps the old credential-helper behavior.
    """
    target = branch or current_branch(workdir)
    assert_feature_branch(target)
    if dry_run:
        return f"dry-run: would push -u {remote} {target}"
    _git(workdir, "push", "-u", remote, target, token=token or _github_token())
    return target


# Minimal GitHub REST client (stdlib-only mirror).
# ---------------------------------------------------------------------------
# The vendored contexts where this driver runs (ladder CI, lane
# workspaces) have no foundry package, and the builder-validity gate
# forbids third-party imports the workspace venv cannot satisfy — so
# the two calls this driver needs are implemented here with urllib
# instead of imported from foundry.github. Parity tests pin the
# endpoints, methods, and payload keys to the canonical client.

#: Generated/derived paths never staged (mirror of submit._JUNK_NAMES).
_JUNK_NAMES = frozenset(
    {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".coverage",
        "coverage.xml",
        "htmlcov",
        ".venv",
    }
)

#: Generated/derived suffixes never staged (mirror of submit._JUNK_SUFFIXES).
_JUNK_SUFFIXES = (".pyc", ".pyo", ".egg-info")


def _stage_paths(paths: list[str]) -> list[str]:
    """Filter candidate paths down to committable ones (drop junk)."""
    kept: list[str] = []
    for path in paths:
        parts = path.replace("\\", "/").split("/")
        if any(part in _JUNK_NAMES or part.endswith(_JUNK_SUFFIXES) for part in parts):
            continue
        kept.append(path)
    return kept


@dataclass(frozen=True)
class _PullData:
    """Opened or adopted pull request (mirror of github.PullData)."""

    number: int
    url: str
    head: str = ""
    base: str = ""


def _api(api_base: str, token: str, method: str, path: str, body: dict[str, Any] | None) -> Any:
    """One authenticated GitHub REST call (mirror of github._api)."""
    cleaned = api_base.rstrip("/")
    if urllib.parse.urlsplit(cleaned).scheme not in ("http", "https"):
        raise ValueError(f"GitHub API base must use http(s): {api_base!r}")
    url = f"{cleaned}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    http_request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(http_request, timeout=30) as response:  # nosec B310 - scheme restricted above
            raw = response.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"github {method} {path} failed: HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"github {method} {path} failed: {exc}") from exc
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise RuntimeError(f"invalid JSON from {url}: {exc}") from exc


def _list_open_pulls(api_base: str, token: str, repo: str, head: str) -> list[_PullData]:
    """List open PRs from ``head`` branch (duplicate-submission guard)."""
    owner = repo.split("/")[0]
    payload = _api(
        api_base, token, "GET", f"/repos/{repo}/pulls?state=open&head={owner}:{head}", None
    )
    if not isinstance(payload, list):
        raise RuntimeError(f"unexpected pull list shape from {repo}")  # noqa: TRY004 - RuntimeError is the pinned public error type here.
    pulls: list[_PullData] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        number = item.get("number")
        url = item.get("html_url")
        if isinstance(number, int) and not isinstance(number, bool) and number:
            pulls.append(
                _PullData(
                    number=number,
                    url=url if isinstance(url, str) else "",
                    head=head,
                    base="",
                )
            )
    return pulls


def _create_pull(
    api_base: str, token: str, repo: str, title: str, head: str, base: str, body: str
) -> _PullData:
    """Open a pull request from ``head`` into ``base``. Creation only."""
    if is_protected_branch(head):
        raise RuntimeError(f"refusing to open a PR from {head!r}")
    payload = _api(
        api_base,
        token,
        "POST",
        f"/repos/{repo}/pulls",
        {"title": title, "head": head, "base": base, "body": body, "draft": False},
    )
    if not isinstance(payload, dict):
        raise RuntimeError(f"PR creation returned no object: {payload!r}")  # noqa: TRY004 - RuntimeError is the pinned public error type here.
    number = payload.get("number")
    url = payload.get("html_url")
    if not isinstance(number, int) or isinstance(number, bool) or not number:
        raise RuntimeError(f"PR creation returned no number: {payload!r}")
    if not isinstance(url, str) or not url:
        raise RuntimeError(f"PR creation returned no URL: {payload!r}")
    return _PullData(number=number, url=url, head=head, base=base)


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
    assert_feature_branch(head)
    if dry_run:
        return {"dry_run": True, "head": head, "base": base, "title": title}
    existing = _list_open_pulls(api_base, token, repo, head)
    if existing:
        pull = existing[0]
        return {"number": pull.number, "url": pull.url, "adopted": True}
    pull = _create_pull(api_base, token, repo, title, head, base, body)
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
    token = _github_token()
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
    except Exception as exc:  # noqa: BLE001 - CLI boundary: report the error and exit 1.
        print(f"error: {exc}")
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
