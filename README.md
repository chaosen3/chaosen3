<h1 align="center">chaosen3</h1>

<p align="center">
  <em>AI and automation engineer. Team of one at a managed service provider.<br>
  I turn repetitive operational work into things that run themselves.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/focus-agents%20%26%20orchestration-7c3aed?style=flat-square" alt="focus">
  <img src="https://img.shields.io/badge/stack-n8n%20%C2%B7%20Docker%20%C2%B7%20Power%20Automate-2563eb?style=flat-square" alt="stack">
  <img src="https://img.shields.io/badge/homelab-4%20hosts%2C%20zero%20chill-0891b2?style=flat-square" alt="homelab">
</p>

<!-- pulse:start -->
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/chaosen3/chaosen3/main/assets/pulse-dark.svg?v=20260817060000">
    <img alt="Homelab pulse" src="https://raw.githubusercontent.com/chaosen3/chaosen3/main/assets/pulse-light.svg?v=20260817060000" width="840">
  </picture>
</p>
<!-- pulse:end -->

### What I actually do

Thirteen years in IT, from apprentice through first and second line to senior engineer, now sitting in an automation role where the brief is roughly "make the toil disappear." That means Copilot Studio agents, Rewst and Power Automate orchestration, Microsoft Graph plumbing, and a lot of PowerShell that runs unattended across a fleet. Deep background in M365, Intune, Entra ID and Exchange, which is mostly useful now as the context that tells me which automations are worth building and which ones will page someone at 3am.

Everything above happens behind a client boundary, so it does not live here. What lives here is the stuff I build for myself, which is usually where I learn the thing first.

### Building

| | |
|---|---|
| **MailTools** | Self-hosted email infrastructure analysis. SPF, DKIM and DMARC evaluation, DNS and RBL lookups, header parsing, plus Graph-based DMARC and TLS-RPT report ingestion. React and Node, shipped in Docker. |
| **Media orchestration** | n8n workflows that stitch Plex, Tautulli, Radarr, Sonarr and Seerr into weekly digests. Half the work is automation, the other half is refusing to accept an ugly report. |
| **Knowledge vault** | A markdown vault that acts as shared long-term memory across Claude, Codex and local agents. Same context, whichever model I happen to be driving. |
| **Solo mining rig** | A Raspberry Pi with a custom OLED display playing the world's least favourable lottery. Expected value is terrible. Learning value was not. |

### How the card above works

It is not a stats widget. My homelab is behind CGNAT, so instead of exposing anything inbound, an n8n workflow on the inside collects the numbers, commits `data/pulse.json` through the GitHub contents API, and a workflow in this repo renders the SVGs and rewrites the block. Push-based, no open ports, no third-party service holding a token that can read my repos.

<details>
<summary>Elsewhere in the rack</summary>

<br>

Proxmox and Docker across four nodes plus an Oracle Cloud instance, Portainer for orchestration, Caddy terminating TLS for a handful of subdomains, AdGuard Home doing DNS, and Tailscale so none of it needs to be publicly reachable. Configuration lives in compose files, compose files live in git, and the parts that are not in git yet are a known and mildly embarrassing item on the list.

</details>

<p align="center">
  <sub>Built in public where I can, behind an NDA where I cannot.</sub>
</p>
