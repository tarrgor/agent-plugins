---
name: create-obsidian-vault
description: Makes the project's `.project/` folder browsable as an Obsidian vault, and refreshes the vault's Home index after the documentation changed. User-invoked only — run it with `/sdd-workflow:create-obsidian-vault`.
disable-model-invocation: true
---

# Create Obsidian vault

Turns `.project/` into an Obsidian vault: vault config plus a generated `Home.md` index of the project's documentation. Documentation only — writes nothing outside `.project/` except a `.gitignore` line.

Re-runnable: config files are never overwritten once they exist, and `Home.md` is refreshed in place.

## 1. Check the target

- `.project/` must exist. If it doesn't, say so and suggest `kick-off` (new project) or `migrate-project` (existing codebase) instead of scaffolding it here.

## 2. Write the vault config

Copy each file from this skill's `references/obsidian/` to `.project/.obsidian/`, **skipping any that already exists** — the user's own settings win.

`app.json` sets `useMarkdownLinks: true` so links stay readable on GitHub, and points attachments at `Branding/Assets`. `graph.json` color-codes SPEC, Knowledge, Inbox, Reports, and Archive in the graph view. `core-plugins.json` must list every plugin it wants **off** explicitly — a plugin omitted from that map keeps Obsidian's default. The network-facing ones (`sync`, `publish`, `webviewer`) are therefore pinned to `false`: a `.project/` vault holds internal specs and findings, so nothing that uploads or fetches should switch itself on. Pin any future outward-facing core plugin the same way.

## 3. Ignore the local-only vault state

Ensure the root `.gitignore` contains these lines (append only what's missing; leave the rest of the file alone):

```
.project/.obsidian/workspace.json
.project/.obsidian/workspace-mobile.json
.project/.obsidian/cache
```

The rest of `.obsidian/` is committed so the whole team gets the same view.

## 4. Generate the Home index

Build `.project/Home.md` from `references/Home.md.template`, filling each section from what's actually on disk:

- **Milestones** — every `.project/SPEC-milestone-*.md`, ordered by number, each with its `Status:` value (lifecycle per `../_shared/conventions.md`, relative to this skill's directory).
- **Knowledge** — one line per `.project/Knowledge/<topic>/` subdirectory with its entry count. Do not read the entries.
- **Inbox** — every `.project/Inbox/findings-*.md`.
- **Reports** — the five most recent `.project/Reports/` entries, newest first.

Omit a section whose source folder is absent; write the template's empty-state line when the folder exists but is empty. Use relative markdown links, not wikilinks.

If `Home.md` already exists, replace only the content between `<!-- lattice:index-start -->` and `<!-- lattice:index-end -->` and preserve everything outside those markers. If the markers are missing from an existing `Home.md`, leave the file untouched and report that.

## 5. Report

Name what was created versus skipped as already present, and tell the user to open the `.project/` folder as a vault in Obsidian ("Open folder as vault"). Do not commit — leave the changes staged in the working tree unless the user asks otherwise.
