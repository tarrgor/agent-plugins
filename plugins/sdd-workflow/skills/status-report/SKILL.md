---
name: status-report
description: Render the reusable STATUS.html project report from saved status or report JSON supplied by another skill. Use for "status report", "render the status page" or to regenerate HTML without a GitHub refresh.
---

# Status Report

Render only; do not gather from GitHub, update the snapshot, or publish. Resolve the project root (Git work tree root, otherwise current directory), then use a caller-provided report JSON file or that project's `.project/status.json`. The contract is in [status-snapshot.md](../_shared/status-snapshot.md).

```
python3 <skills/_shared/scripts/status-page.py> <project-root> <report.json>
```

Use the Python command for the host from [runtime-adapters.md](../_shared/runtime-adapters.md). For supplied JSON, a file or stdin is required; never interpolate report text into a shell argument. To render saved status, use `--snapshot` explicitly. Leave a prior page intact on failure. For absent or invalid saved status, suggest `project-status` to rebuild it. Return the page path. Never upload the report.
