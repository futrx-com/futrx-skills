# FutrX Skills

Agent skills by FutrX, installable with the [`skills`](https://www.npmjs.com/package/skills) CLI.

## code-refactorer

Refactors code that already exists and works. Use it for architecture reviews, separating responsibilities, and structural cleanup across software types, while preserving every observable behavior.

### Install

Run this in your project:

```bash
npx skills add futrx-com/futrx-skills --skill code-refactorer
```

To install it for your user account instead of only the current project:

```bash
npx skills add futrx-com/futrx-skills --skill code-refactorer --global
```

The CLI detects your agents (Claude Code, Codex, Cursor, …) and asks which ones to install to. To skip the prompts:

```bash
npx skills add futrx-com/futrx-skills --skill code-refactorer --yes
```

### Update

Pull the latest version:

```bash
npx skills update code-refactorer
```

Add `--global` or `--project` to update only that scope.

### Remove

```bash
npx skills remove code-refactorer
```
