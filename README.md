<h1 align="center">chaosen3</h1>

<p align="center">
  <img src="https://img.shields.io/badge/agents%20%26%20orchestration-7c3aed?style=flat-square" alt="agents and orchestration">
  <img src="https://img.shields.io/badge/n8n%20%C2%B7%20Docker%20%C2%B7%20Python%20%C2%B7%20Node-2563eb?style=flat-square" alt="stack">
  <img src="https://img.shields.io/badge/self--hosted-0891b2?style=flat-square" alt="self-hosted">
</p>

<!-- pulse:start -->
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/chaosen3/chaosen3/main/assets/pulse-dark.svg?v=20260828030000">
    <img alt="Homelab pulse" src="https://raw.githubusercontent.com/chaosen3/chaosen3/main/assets/pulse-light.svg?v=20260828030000" width="840">
  </picture>
</p>
<!-- pulse:end -->

### Projects

| Project | Stack | Notes |
|---|---|---|
| **MailTools** | React, Node, Docker | SPF, DKIM and DMARC evaluation, DNS and RBL lookups, header parsing, aggregate report ingestion |
| **Workflow automation** | n8n, JS, REST | API orchestration and scheduled reporting pipelines |
| **Agent tooling** | Python | Tool-calling loop built from primitives rather than a framework |
| **Deploy scripting** | PowerShell, Bash | Idempotent installers with layered transport fallback and structured logging |

### Pulse pipeline

```
scheduled job ──▶ pulse.json ──▶ GitHub contents API
                                        │
                              push: data/pulse.json
                                        ▼
                              render_pulse.py (Actions)
                                        │
                          ┌─────────────┴─────────────┐
                          ▼                           ▼
                 assets/pulse-*.svg          README block rewrite
```

Push-only, so nothing accepts inbound connections and no external service holds a token. SVG is generated in-repo, themed via `<picture>` and `prefers-color-scheme`, and cache-busted with a query parameter because README images are proxied and cached by URL.

- Renderer: [`scripts/render_pulse.py`](scripts/render_pulse.py) — stdlib only
- Workflow: [`.github/workflows/pulse.yml`](.github/workflows/pulse.yml)
- Schema: [`data/pulse.json`](data/pulse.json)
