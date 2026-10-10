# Arsenal Forge v0.1

Arsenal Forge turns a GitHub repository into a **reviewable, testable Agent capability package**.

## Design goal

The upstream project is useful at collecting repository context, but the first Arsenal Forge milestone adds explicit gates between "repository discovered" and "skill trusted".

```text
GitHub repository
      |
      v
Repository Intelligence
      |
      v
Skill Compiler
      |
      v
Security Gate
      |
      v
Smoke / Functional Eval
      |
      v
Verified Skill
      |
      v
Top Agent Arsenal
```

## v0.1 modules

- `arsenal_forge/scanner.py`
  - deterministic path ranking
  - entry-point and dependency-manifest discovery
  - stable contract for future AST/import/call-graph analysis
- `arsenal_forge/security.py`
  - static risk rules
  - explicit high/critical blocking
  - security score for triage, not a guarantee of safety
- `arsenal_forge/evals.py`
  - shell-free smoke command runner
  - timeout and output capture
  - pass-rate summary
- `arsenal_forge/compiler.py`
  - deterministic draft `SKILL.md`
  - source provenance
  - verification state defaults to `unverified`

## Compatibility principle

The original `github-skill-forge/scripts/forge.py` remains untouched in v0.1.
This branch therefore preserves the current upstream workflow while the new
pipeline is built beside it and progressively integrated.

## Acceptance criteria for v0.1

1. `main` remains an untouched upstream mirror.
2. Development occurs on `arsenal-forge-v0.1`.
3. New modules import without third-party dependencies.
4. Static security gate blocks high/critical findings.
5. Smoke runner never uses `shell=True`.
6. Generated manifests carry source provenance and default to `unverified`.

## Next milestones

### v0.2 — Repository Intelligence
- recursive GitHub tree ingestion
- AST/symbol extraction for Python/JS/TS
- import/dependency graph
- API/CLI surface discovery
- README claims vs code-evidence cross-check

### v0.3 — Skill Packaging
- `references/`
- generated wrappers under `scripts/`
- environment/secret requirements
- platform compatibility metadata

### v0.4 — Verification
- isolated execution
- functional task fixtures
- with-skill vs baseline evaluation
- reproducible verification report

### v1.0 — Arsenal Registry
- capability index
- semantic skill routing
- version/update tracking
- trust score and provenance
- automated re-verification after upstream changes
