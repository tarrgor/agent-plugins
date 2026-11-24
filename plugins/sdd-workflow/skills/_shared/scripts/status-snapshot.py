#!/usr/bin/env python3
"""Atomically maintain the local, versioned project status using JSON inputs."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
import tempfile
import time
import uuid


class StatusError(ValueError):
    pass


def load(path):
    if path == "-":
        return json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


@contextmanager
def locked(path):
    # Do not unlink the lock file: another writer may already hold its inode open.
    with path.open("a+b") as lock:
        if sys.platform == "win32":
            import msvcrt

            def acquire():
                lock.seek(0)
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)

            def release():
                lock.seek(0)
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            def acquire():
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)

            def release():
                fcntl.flock(lock, fcntl.LOCK_UN)

        deadline = time.monotonic() + 5
        while True:
            try:
                acquire()
                break
            except OSError as exc:
                if time.monotonic() >= deadline:
                    raise StatusError("status is busy; retry") from exc
                time.sleep(0.05)
        try:
            yield
        finally:
            release()


def atomic_write(path, content):
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=path.parent, delete=False) as handle:
            temp = Path(handle.name)
            handle.write(content)
        temp.replace(path)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


def require(condition, message):
    if not condition:
        raise StatusError(message)


def positive(value):
    return type(value) is int and value > 0


def rows(value, kind):
    require(isinstance(value, list), f"{kind} must be an array")
    result = {}
    for row in value:
        require(isinstance(row, dict) and positive(row.get("number")), f"invalid {kind} number")
        n = row["number"]
        require(n not in result and isinstance(row.get("title"), str), f"invalid/duplicate {kind} #{n}")
        if kind == "issues":
            require(type(row.get("closed")) is bool
                    and isinstance(row.get("labels"), list) and all(isinstance(x, str) for x in row["labels"])
                    and isinstance(row.get("depends_on"), list) and all(positive(x) for x in row["depends_on"]),
                    f"invalid issue facts for #{n}")
        else:
            require(isinstance(row.get("branch"), str) and re.match(r"^issue/[1-9]\d*-", row["branch"])
                    and row.get("checks") in ("passing", "failing", "pending", "none")
                    and type(row.get("unresolved")) is int and row["unresolved"] >= 0, f"invalid PR facts for #{n}")
        result[n] = row
    return result


def strings(value):
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def finding_rows(value):
    require(isinstance(value, dict) and all(isinstance(k, str) and k and
            (v is None or isinstance(v, str) and v) for k, v in value.items()),
            "findings must map stable keys to null or a critical summary")
    return value


def derive(report):
    project = report.get("project")
    require(isinstance(project, dict) and all(isinstance(project.get(k), str) and project[k]
            for k in ("name", "repo", "base")), "project name, repo and base are required")
    milestone = report.get("milestone")
    require("milestone" in report and (milestone is None or
            isinstance(milestone, dict) and isinstance(milestone.get("title"), str) and milestone["title"]),
            "milestone must be null or have a title")
    require(strings(report.get("planned")) and "last_meeting" in report
            and (report["last_meeting"] is None or isinstance(report["last_meeting"], str)),
            "planned and last_meeting are required")
    if milestone is not None:
        require(type(milestone.get("needs_close")) is bool, "milestone.needs_close is required")
    inventory = finding_rows(report.get("finding_items"))
    findings = {"count": len(inventory), "critical": [v for _, v in sorted(inventory.items()) if v is not None]}
    report["findings"] = findings
    issues = rows(report.get("issues"), "issues")
    prs = rows(report.get("prs"), "prs")
    external = report.get("external_blockers")
    require(isinstance(external, dict) and all(re.fullmatch(r"[1-9]\d*", k)
            and type(v) is bool for k, v in external.items()), "invalid external blocker states")
    require(milestone is not None or not issues, "no active milestone for these issues")
    review = {int(re.match(r"^issue/(\d+)-", p["branch"])[1]) for p in prs.values()}
    for n, issue in sorted(issues.items()):
        labels = issue["labels"]
        blockers = sorted({b for b in issue["depends_on"]
                           if (not issues[b]["closed"] if b in issues else external.get(str(b), True))})
        issue["blocked_by"] = [] if issue["closed"] else blockers
        issue["state"] = ("closed" if issue["closed"] else
                          "parked" if "needs-decision" in labels else
                          "in-progress" if "in-progress" in labels else
                          "blocked" if blockers else "in-review" if n in review else "ready")
    report["issues"] = [issues[n] for n in sorted(issues)]
    report["prs"] = [prs[n] for n in sorted(prs)]
    if milestone is not None:
        milestone["closed"] = sum(i["closed"] for i in issues.values())
        milestone["total"] = len(issues)
    # Preserve free-form warnings for display until a different scope invalidates them.
    require(strings(report.get("flags", [])), "invalid flags")

    def action(skill, label, n=None):
        return {"skill": skill, "action": label,
                "command": "/sdd-workflow:" + skill + (f" {n}" if n is not None else "")}

    bad = next((p for p in report["prs"] if p["checks"] == "failing" or p["unresolved"]), None)
    clean = next((p for p in report["prs"] if p["checks"] in ("passing", "none") and not p["unresolved"]), None)
    ready = next((i["number"] for i in report["issues"] if i["state"] == "ready"), None)
    if findings["count"] >= 3 or findings["critical"]:
        next_step = action("project-meeting", "Review pending findings")
    elif bad:
        next_step = action("check-pr-comments", f"Check PR #{bad['number']}", bad["number"])
    elif clean:
        next_step = action("merge-pr", f"Review and merge PR #{clean['number']}", clean["number"])
    elif ready is not None:
        next_step = action("implement-issue", f"Implement issue #{ready}", ready)
    elif any(i["state"] == "parked" for i in issues.values()):
        next_step = action("project-meeting", "Decide parked issues")
    elif report["planned"]:
        next_step = action("create-spec-issues", "Create issues for the planned milestone")
    elif milestone and milestone["total"] and milestone["closed"] == milestone["total"] and milestone["needs_close"]:
        next_step = action("project-meeting", "Decide whether to close the milestone")
    elif milestone is None:
        next_step = action("kick-off", "Plan the next milestone")
    else:
        next_step = None
    report["next"] = next_step
    return report


def patch(report, delta):
    allowed = {"milestone", "planned", "issues", "prs", "remove_prs",
               "external_blockers", "finding_upserts", "remove_findings", "last_meeting", "flags", "refresh_needed"}
    require(isinstance(delta, dict) and delta and not (delta.keys() - allowed), "invalid delta keys")
    project_scope = "milestone" in delta
    if project_scope:
        require("issues" in delta and "external_blockers" in delta, "milestone change needs its complete issue scope")
        if (delta["milestone"] or {}).get("title") != (report["milestone"] or {}).get("title"):
            report.pop("flags", None)
        report["issues"] = delta["issues"]
        report["external_blockers"] = delta["external_blockers"]
    else:
        if "issues" in delta:
            previous = rows(report["issues"], "issues")
            previous.update(rows(delta["issues"], "issues"))
            report["issues"] = list(previous.values())
        if "external_blockers" in delta:
            require(isinstance(delta["external_blockers"], dict), "invalid blocker delta")
            report["external_blockers"].update(delta["external_blockers"])
    prs = rows(report["prs"], "prs")
    prs.update(rows(delta.get("prs", []), "prs"))
    removals = delta.get("remove_prs", [])
    require(isinstance(removals, list) and all(positive(n) for n in removals), "invalid PR removal")
    for n in removals:
        prs.pop(n, None)
    report["prs"] = list(prs.values())
    report["finding_items"].update(finding_rows(delta.get("finding_upserts", {})))
    finding_removals = delta.get("remove_findings", [])
    require(strings(finding_removals), "invalid finding removal")
    for key in finding_removals:
        report["finding_items"].pop(key, None)
    for key in ("milestone", "planned", "last_meeting", "flags"):
        if key in delta:
            report[key] = delta[key]
    if "refresh_needed" in delta:
        require(delta["refresh_needed"] is True, "only a full refresh clears refresh_needed")
        report["_status"]["refresh_needed"] = True
    return derive(report)


def snapshot(root):
    return root / ".project" / "status.json"


def current(path):
    try:
        report = load(path)
        meta = report["_status"]
        require(meta["version"] == 1 and isinstance(meta["revision"], str)
                and isinstance(meta["last_full_refresh"], str) and isinstance(meta["updated_at"], str)
                and type(meta["refresh_needed"]) is bool, "invalid versioned metadata")
        return derive(report)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        raise StatusError("status.json missing or invalid; run project-status to refresh") from exc


def revision(path):
    try:
        return current(path)["_status"]["revision"]
    except StatusError:
        return "missing-or-invalid"


def ignore_generated(root):
    path = root / ".gitignore"
    try:
        old = path.read_bytes()
    except FileNotFoundError:
        old = b""
    patterns = (b"/STATUS.html", b"/.project/status.json", b"/.project/status.json.lock")
    missing = [item for item in patterns if item not in old.splitlines()
               and not (item == b"/STATUS.html" and b"STATUS.html" in old.splitlines())]
    if missing:
        with path.open("ab") as handle:
            handle.write((b"\n" if old and not old.endswith(b"\n") else b"") + b"\n".join(missing) + b"\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("operation", choices=("revision", "replace", "patch"))
    parser.add_argument("input", nargs="?")
    parser.add_argument("--expect")
    args = parser.parse_args()
    try:
        require(args.root.is_dir(), "project root must be a directory")
        path = snapshot(args.root)
        if args.operation == "revision":
            print(revision(path))
            return
        require(args.input is not None and args.expect is not None, "input and --expect revision are required")
        data = load(args.input)
        require(isinstance(data, dict), "input must be a JSON object")
        path.parent.mkdir(exist_ok=True)
        with locked(path.with_suffix(".json.lock")):
            require(args.expect == revision(path), "status changed; re-read confirmed facts and retry")
            now = datetime.now(timezone.utc).isoformat(timespec="seconds")
            if args.operation == "replace":
                report = derive(data)
                report["_status"] = {"version": 1, "last_full_refresh": now, "refresh_needed": False}
            else:
                report = current(path)
                before = json.dumps(report, sort_keys=True)
                patch(report, data)
                if json.dumps(report, sort_keys=True) == before:
                    print(path)
                    return
            report["generated"] = now[:10]
            report["_status"].update(revision=uuid.uuid4().hex, updated_at=now)
            payload = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
            ignore_generated(args.root)
            atomic_write(path, payload)
        print(path)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(f"status-snapshot: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
