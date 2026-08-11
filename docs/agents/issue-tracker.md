# Issue tracker: Local Markdown

Issues and specs for this repo live as Markdown files in `.scratch/`.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The spec is `.scratch/<feature-slug>/spec.md`
- Implementation issues are one file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`
- Triage state is a `Status:` line near the top
- Comments append under a `## Comments` heading

## Skill operations

- Publish: create a file under `.scratch/<feature-slug>/`
- Fetch: read the referenced issue path
- Blocking: record `Blocked by: NN, NN`
- Claim: set `Status: claimed`
- Resolve: add an `## Answer` and set `Status: resolved`
