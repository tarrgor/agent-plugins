---
name: generate-branding
description: This skill should be used to produce or refresh a project's brand identity — a written brand guide and visual assets (logo, icon, social/marketing templates) — in `.project/Branding/`. Trigger phrases include "create the branding", "generate our brand identity", "let's do branding", "generate a logo", "make an icon", "refresh the color palette", or whenever the project needs a brand guide or design asset produced or updated. Standalone and on-demand — never triggered automatically by kick-off, create-spec-issues, or project-meeting.
---

# Generate Branding

Runs standalone, on demand. Produces or updates a brand identity guide and visual assets in `.project/Branding/` — does not touch code.

Written-deliverable sizing is defined in `../_shared/conventions.md` (relative to this skill's directory).

## 1. Determine scope: full identity or partial update

- Missing `.project/Branding/BRAND.md`: fresh, complete run — produce the full identity (Steps 3-7 in full).
- Existing `BRAND.md`: an update. Scope to exactly what the user asked for (e.g. "just the logo", "refresh the palette"); if the request is ambiguous, ask which section(s) or asset(s) to regenerate. Treat everything else in `BRAND.md` as already-decided fact — reuse it, don't re-ask or overwrite it silently.

## 2. Gather context

- Read `.project/SPEC.md` and the highest-numbered `.project/SPEC-milestone-*.md`, if present, for project name, audience, positioning, and tone. Anything found there is a fact — never ask for it. Neither file is required; proceed without them if absent.
- On a partial update, also read the existing `BRAND.md` in full and reuse its unaffected decisions (palette, type, voice) as fact.

## 3. Map the decision tree

Sketch the decision branches in scope per Step 1 and not already resolved by Step 2 — brand personality/adjectives, target audience & desired emotional impression, color palette (preferences, constraints, accessibility), typography style, logo direction (wordmark, lettermark, symbol, or combination), imagery/iconography style, competitors or inspiration references, must-avoid (styles, colors, competitor look-alikes), tone of voice for copy, which specific assets are wanted and their usage contexts (digital, print, social) — expanding into sub-branches as answers reveal dependencies.

## 4. Interview one question at a time

- One question per turn; wait for the answer before asking the next.
- Propose a recommended answer with a short rationale for every question.
- Ask only about decisions the user hasn't already made. Skip anything resolved by Step 2, or by the existing `BRAND.md` on a partial update.
- Resolve branches in dependency order — don't ask about something whose answer depends on an unresolved earlier decision.
- Keep going until every relevant branch from Step 3 is resolved in concrete, specific terms (exact hex ranges, named typefaces or styles, explicit logo direction) — not just until it feels "enough." Vague answers ("something modern") need a follow-up to pin down specifics before moving on.

## 5. Confirm before generating

Summarize the full brand direction in detail — every decision from Step 4, in the specific terms agreed, not a vague paraphrase — (or, on a partial update, exactly what will change). Do not write or generate anything until the user explicitly confirms it's correct and complete. This is the shared understanding both of you are designing against; do not proceed on an assumption the user hasn't confirmed.

## 6. Write or update the brand guide

`.project/Branding/BRAND.md`, with these sections: positioning summary, color palette (hex values + usage), typography (typefaces, pairing, usage rules), voice & tone (adjectives + do/don't examples), logo concept description, and an asset inventory (filename, description, generated-image or written-brief).

On a partial update, edit only the section(s) in scope; leave the rest of the file untouched.

## 7. Generate visual assets

For each asset in scope (logo concepts, icon, social/marketing templates):

- Check what design or image-generation tools are available in the current environment (MCP servers, installed skills) and pick the best fit. Do not assume any specific tool is present.
- Available: generate the asset directly into `.project/Branding/Assets/`, matching the palette and typography from `BRAND.md`. Name files by role, e.g. `logo-concept-1.png`, `icon.png`, `social-<platform>-<use>.png`.
- Unavailable: write `.project/Branding/Assets/<asset-slug>-brief.md` instead — a creative brief precise enough to execute later or hand to a designer (concept, composition, colors, typography, mood references).
- Record every asset produced (or briefed) in `BRAND.md`'s asset inventory.

## 8. Report

Summarize what was written and generated (or briefed), and where. Note any asset that fell back to a written brief for lack of tooling, and what would be needed to produce it directly.
