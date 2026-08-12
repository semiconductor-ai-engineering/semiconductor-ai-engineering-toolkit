# Public Alpha Release Readiness v0.1

## Status

This document records readiness for a possible public alpha tag `v0.1.0-alpha.1`. It does not create a Git tag, GitHub Release, PyPI publication, or claim that the project is production-ready.

## Alpha scope

The alpha scope is a small, inspectable public foundation for synthetic semiconductor engineering data workflows. It includes:

- public run-centric data model documentation;
- RunRecord v0.1 JSON Schema;
- a deterministic Python validation API and `semi-ai validate` CLI;
- synthetic RunRecord fixtures and synthetic document/DocumentChunk examples;
- a machine-readable synthetic dataset manifest;
- CI tests and a tag-triggered build verification workflow.

## Quick Start verification

From a clean checkout with Python 3.10 or newer:

```text
python -m venv .venv
```

Activate the environment using the platform-appropriate command:

```powershell
.venv\Scripts\Activate.ps1
```

```text
source .venv/bin/activate
```

Install the package and validate the real checked-in fixture:

```text
python -m pip install -e .
semi-ai validate examples/synthetic_dataset_v0_1/runs/completed/run_completed_001.json
```

Expected output:

```text
Valid RunRecord v0.1
```

For development tests:

```text
python -m pip install -e ".[test]"
python -m pytest -q
```

## Package and build verification

The package uses PEP 440 version `0.1.0a1`. The proposed human-facing tag is `v0.1.0-alpha.1`. `pyproject.toml` is authoritative for package metadata. `setup.py` is retained because its build hook bundles the checked-in canonical JSON Schema into non-editable distributions.

The release workflow at [`.github/workflows/release-build.yml`](../.github/workflows/release-build.yml) triggers for tags matching `v*` or an explicit manual dispatch, builds both wheel and sdist, checks that both artifacts exist, installs the wheel into a clean virtual environment, and runs a CLI smoke validation. It does not publish to PyPI and does not require PyPI credentials.

## Known limitations

- The schema is a v0.1 public contract, not a complete semiconductor engineering ontology.
- Units remain explicit free-form strings; no universal unit registry or conversion system is included.
- Synthetic fixtures are small, deterministic, generic, and not representative of production distributions.
- DocumentChunk JSON uses the existing example shape; a separate formal document schema is future work.
- The package is an alpha/pre-alpha developer toolkit, not a validated industrial product.

## Security boundaries

- Repository data is synthetic or explicitly public-safe only.
- The validator reads only the explicit local file supplied by the caller.
- Record and document text is untrusted data; it is not executed, imported, interpolated into shell commands, or treated as instructions.
- The validator does not make network requests or retrieve external schemas.
- No credentials, tokens, cookies, private paths, real fab data, HDP data, customer data, or proprietary process information are included.
- The release workflow uses `contents: read` and performs build/smoke verification only.

## Synthetic-data-only policy

The synthetic dataset is intended for software testing, evaluation, and education only. It does not represent real semiconductor process windows, equipment behavior, recipe limits, or root-cause relationships. Its identifiers, values, units, event codes, messages, documents, and relationships are fictional.

Contributors must not add real fab logs, HDP private data, customer information, equipment serials, recipe names, vendor manual text, proprietary process knowledge, credentials, or copied alarm tables.

## Unsupported functionality

The toolkit does not currently:

- control semiconductor equipment;
- modify recipes;
- provide process safety guidance;
- diagnose real fab failures;
- connect to HDP/private systems;
- execute AI agents;
- perform RAG;
- parse arbitrary vendor logs.

It also does not make OpenAI API calls or provide closed-loop process optimization.

## Release verification checklist

- [x] README Quick Start uses an actual synthetic RunRecord fixture.
- [x] Package metadata is internally consistent and uses PEP 440 `0.1.0a1`.
- [x] CHANGELOG describes completed capabilities and limitations without unverifiable adoption claims.
- [x] CI, MIT license, and supported Python badges are verifiable references.
- [x] Release workflow builds wheel and sdist without PyPI publishing.
- [x] Clean wheel installation and CLI smoke validation pass locally.
- [x] Existing synthetic RunRecords pass validation.
- [x] Tests, package checks, UTF-8, links, and security/data-boundary scans pass.
- [ ] Human maintainer decides whether to create tag `v0.1.0-alpha.1`.
- [ ] Human maintainer decides whether to create a GitHub alpha Release.
