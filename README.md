# chaosen3

AI and automation engineer, with a background in Microsoft 365, infrastructure and PowerShell.

My projects cover email diagnostics, media serving and game-server tooling. I also run the Linux and Docker infrastructure behind them, including local GPU inference, storage, networking and deployment.

## Selected work

### [MailTools](https://mailtools.hashemlabs.com)
Email deliverability and DNS diagnostics, with free tools for SPF, DKIM, DMARC, TLS, blocklists and message analysis. Includes DMARC and TLS-RPT report ingestion, monitoring and alerting.

Its Deliverability Reasoning Engine runs diagnostic checks first, then uses a local model to explain the findings. A 31-case evaluation harness checks the explanations against the diagnostic engine.

**React · Node.js · PostgreSQL · Docker** · In production · Source private

### Viewarr
A self-hosted media server built in Go and Next.js. Handles library scanning, metadata, artwork, playback, transcoding, subtitles, watch history and user permissions.

The scanner protects the catalogue when a NAS mount disappears: an unexpectedly empty scan leaves existing records intact and reports the failure.

**Go · Next.js · SQLite · FFmpeg** · Self-hosted · Source private

### Dank City
A London-themed FiveM roleplay server on GTA V Enhanced, developed by a three-person team. Work includes the custom framework, resource integration, in-game interfaces and synchronised radio.

The supporting **Preflight** tooling checks CfxLua syntax, manifests, dependency cycles, asset versions, map streaming extents and duplicates across resources on every pull request.

**Lua · Python · Docker · GitHub Actions** · Source private

## Infrastructure & automation

- **Self-hosting:** Linux hosts managed through Portainer, NAS-backed storage, reverse proxies, Cloudflare tunnels and Tailscale.
- **Networking:** UniFi, local DNS and a dedicated VLAN routed through a WireGuard VPN gateway.
- **Local inference:** llama.cpp with Vulkan on an AMD GPU, including the model serving MailTools.
- **Automation:** n8n and JavaScript for API workflows and reporting; PowerShell and Bash for deployment.
- **Development tooling:** Python agent loops, separate implementation and review stages, and automated checks on pull requests.

## Homelab pulse

Service health and recent automation activity, published from the homelab.

<!-- pulse:start -->
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/chaosen3/chaosen3/main/assets/pulse-dark.svg?v=20261106040000">
    <img alt="Homelab pulse" src="https://raw.githubusercontent.com/chaosen3/chaosen3/main/assets/pulse-light.svg?v=20261106040000" width="840">
  </picture>
</p>
<!-- pulse:end -->

[Renderer](https://github.com/chaosen3/chaosen3/blob/main/scripts/render_pulse.py) · [Workflow](https://github.com/chaosen3/chaosen3/blob/main/.github/workflows/pulse.yml) · [Latest data](https://github.com/chaosen3/chaosen3/blob/main/data/pulse.json)

<details>
<summary>How the pulse is generated</summary>

A scheduled job pushes a JSON snapshot to this repository. GitHub Actions renders the light and dark SVGs using Python's standard library and updates the image URLs in this README.

```text
Homelab → data/pulse.json → GitHub Actions → SVG cards → Profile
```

The homelab only makes outbound connections for this pipeline. The cards support light and dark themes, and timestamped image URLs refresh GitHub's cached copies when new data arrives.

</details>
