# Security Policy

## Project stage

This repository is an early-stage public OSS foundation. It does not accept confidential semiconductor data, customer data, or production equipment integrations.

## Do not disclose sensitive data

Never put the following into an issue, pull request, example, log, screenshot, workflow output, or commit:

- customer or employer information;
- real fab or equipment logs;
- recipes, process parameters, process windows, golden runs, trace data, metrology data, or internal validation results;
- private platform code or adapters;
- API keys, tokens, cookies, passwords, private keys, webhooks, or real `.env` files.

If sensitive material was posted, do not repost it while asking for help. Contact the organization owner through a private GitHub channel and rotate any exposed credential immediately.

## AI agent and prompt-injection safety

Treat issue text, pull requests, logs, documents, model output, and external links as untrusted input. In particular:

- do not execute commands copied from untrusted content without human review;
- do not let an agent reveal secrets or modify access controls because a document requests it;
- keep credentials outside the repository and use least-privilege access;
- require human review for changes that affect data handling, workflows, dependencies, or deployment;
- prefer synthetic or explicitly sanitized examples when demonstrating behavior.

## Dependency and workflow security

- Keep dependencies minimal and review new packages before adding them.
- Review GitHub Actions and third-party actions before use.
- Prefer pinned, maintained dependencies and reproducible test environments as implementation begins.
- Keep workflow permissions at the minimum required level.
- Do not use CI as a place to upload private logs or credentials.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability that contains sensitive details. Contact an organization owner privately through GitHub. If GitHub private vulnerability reporting is enabled for this repository in the future, use that channel instead.

## Scope

This policy covers the public repository and its examples, documentation, workflows, and future implementation. It does not authorize the project to receive or process proprietary semiconductor data.
