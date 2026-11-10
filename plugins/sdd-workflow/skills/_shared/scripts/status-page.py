#!/usr/bin/env python3
"""Render a project's status report as `STATUS.html` at its root.

`project-status` gathers the project's state and works out the report — every count, state and
next action on the page is its reading. This script only renders: it takes that report as one JSON
object, drops it into `../status-template.html` and writes the page, so the page cannot disagree
with the report and looks the same on every run.

    python3 status-page.py <project-root> [report.json]     # report from the file, or stdin

Issue and PR titles are user-written strings, so the report never travels in a shell word. It is
embedded with `<`, `>` and `&` escaped, so nothing in it can close the script tag it sits in, and
the template inserts every string as text, never as markup.

The page is written to a scratch file beside it and moved into place, so a failed run leaves the
existing page untouched.

Exit: 0 written (the path is printed)   2 usage, or no such project root   3 the report is not a
JSON object   4 the template is missing or carries no placeholder   5 the page could not be written
"""

import json
import os
import sys

PLACEHOLDER = "/*__PROJECT_STATUS__*/"
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir,
                        "status-template.html")


def main(argv):
    if len(argv) not in (2, 3):
        print("usage: status-page.py <project-root> [report.json]", file=sys.stderr)
        return 2
    root = argv[1]
    if not os.path.isdir(root):
        print("status-page.py: %s is not a directory" % root, file=sys.stderr)
        return 2

    try:
        if len(argv) == 3:
            with open(argv[2], encoding="utf-8-sig") as handle:
                report = json.load(handle)
        else:
            report = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
    except (OSError, ValueError) as err:
        print("status-page.py: cannot read the report as JSON: %s" % err, file=sys.stderr)
        return 3
    if not isinstance(report, dict):
        print("status-page.py: the report is not a JSON object", file=sys.stderr)
        return 3

    try:
        with open(TEMPLATE, encoding="utf-8") as handle:
            template = handle.read()
    except OSError as err:
        print("status-page.py: cannot read the template: %s" % err, file=sys.stderr)
        return 4
    if template.count(PLACEHOLDER) != 1:
        print("status-page.py: the template carries %d placeholders, expected 1"
              % template.count(PLACEHOLDER), file=sys.stderr)
        return 4

    data = (json.dumps(report, ensure_ascii=False)
            .replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e"))
    page = template.replace(PLACEHOLDER, data)

    target = os.path.join(root, "STATUS.html")
    scratch = target + ".tmp"
    try:
        with open(scratch, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(page)
        os.replace(scratch, target)
    except OSError as err:
        print("status-page.py: cannot write %s: %s" % (target, err), file=sys.stderr)
        try:
            os.remove(scratch)
        except OSError:
            pass
        return 5
    print(target)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
