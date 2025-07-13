[![Lint Status](https://github.com/P-R-E-Z/prez-pkglog/actions/workflows/lint.yml/badge.svg)](https://github.com/P-R-E-Z/prez-pkglog/actions/workflows/lint.yml)

# prez-pkglog

**prez-pkglog** is a cross-distro/platform package-activity logger that records every install and removal event on your system, then writes an append-only history in both JSON and TOML. It can also monitor your downloads(configurable) folder for new files.

---

## Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Package-manager integration](#package-manager-integration)

<details>
<summary><strong>4. Configuration</strong></summary>

&nbsp;&nbsp;1. [User Scope](#user-scope-default)<br/>
&nbsp;&nbsp;2. [System Scope](#system-scope-requires-administrator)<br/>
&nbsp;&nbsp;3. [DNF Plugin Configuration](#dnf-plugin-configuration)

</details>

<details>
<summary><strong>5. Usage</strong></summary>

&nbsp;&nbsp;1. [Setup](#setup)<br/>
&nbsp;&nbsp;2. [Check Status](#check-status)<br/>
&nbsp;&nbsp;3. [Start Monitoring](#start-monitoring)<br/>
&nbsp;&nbsp;4. [Query Logs](#query-logs)<br/>
&nbsp;&nbsp;5. [Export Logs](#export-logs)<br/>
&nbsp;&nbsp;6. [Manual Logging](#manual-logging)

</details>

6. [Shell Integration](#shell-integration)
7. [Log File Examples](#log-file-examples)
8. [Contributing](CONTRIBUTING.md)

## Features

- **Zero-maintenance Hooks** - hooks directly into DNF; no polling required.
- **Dual Log Formats** - automatically mirrors entries to `packages.json` and `packages.toml` files.
- **Modular Backends** - easily extendable with backends for APT, Pacman, Homebrew, etc.
- **Append-Only History** - entries are never deleted; removals are flagged as removed.
- **Scope-Aware Logging** - choose between user-only (`--scope user`) or system-wide (`--scope system`) package tracking.
- **Download Monitoring** - automatically log files downloaded to your Downloads folder.
- **Log Querying** - search and filter your package history directly from the CLI.

---

## Installation


Package builds will soon be available from my Copr repository.  Until then:

* **Fedora / RHEL** – build & install the RPM as shown below (automatic DNF integration).
* **All other platforms** – install the pure-Python package with `pipx` (or `pip`) and, if you like, add a small hook so your package manager calls the CLI automatically.

### Quick install via pipx (works everywhere)

```bash
# system Python → isolated environment in ~/.local/pipx:
pipx install prez-pkglog==0.5.3

# verify
prez-pkglog --help
```

You can now enable the download-monitoring service:

```bash
systemctl --user daemon-reload   # first time only
systemctl --user enable --now prez-pkglog.service
```

### (Optional) DIY hooks for other package managers

<details>
<summary><strong>APT / Debian & Ubuntu</strong></summary>

1. Create `/etc/apt/apt.conf.d/99prez-pkglog` (system-wide) or `~/.config/apt/apt.conf.d/99prez-pkglog` (user):

```conf
DPkg::Post-Invoke { "prez-pkglog install-apt-hook || true"; };
```

2. Put a tiny helper on your PATH, e.g. `/usr/local/bin/prez-pkglog-install-apt-hook`:

```bash
#!/usr/bin/env bash
# Log every package touched in the most recent dpkg transaction
awk '{print $4}' /var/log/dpkg.log | tail -n +2 | while read -r pkg; do
  prez-pkglog install "$pkg" apt
done
```

Make it executable (`chmod +x …`).

</details>

<details>
<summary><strong>Pacman / Arch</strong></summary>

Create `/etc/pacman.d/hooks/prez-pkglog.hook`:

```ini
[Trigger]
Operation = Install
Operation = Upgrade
Operation = Remove
Type      = Package
Target    = *

[Action]
Description = Log package transaction with prez-pkglog
When        = PostTransaction
Exec        = /usr/bin/prez-pkglog pacman-hook %t
```

`%t` is the transaction database path; you can parse it inside `pacman-hook` to emit individual `prez-pkglog install/remove` calls.

</details>

<details>
<summary><strong>Other managers</strong></summary>

For Homebrew, Chocolatey and Winget, use manual logging or adapt the examples above. Read _Package-manager integration_ and [CONTRIBUTING](CONTRIBUTING.md) for what’s still needed.

</details>

---

## Package-manager integration

<details>
<summary><strong>Linux</strong></summary>

| Package manager | Status | Setup |
|-----------------|--------|-------|
| **DNF** (Fedora/RHEL) | Automatic logging via plugin | See [DNF Plugin Configuration](#dnf-plugin-configuration) and the *Start&nbsp;Monitoring* section. The RPM installs `/usr/lib/dnf/plugins/prez_pkglog.py` and a sample config; enable it with `enabled=1` and restart DNF. |
| **APT** (Debian/Ubuntu) | Planned | Parser exists (`apt.py`), but no hook yet. A `DPkg::Post-Invoke` script is needed. Help welcome → [Contributing](CONTRIBUTING.md) |
| **Pacman** (Arch) | Planned | Parser exists (`pacman.py`). Needs an `alpm` hook (`/etc/pacman.d/hooks/prez-pkglog.hook`). See [Contributing](CONTRIBUTING.md) |

</details>

<details>
<summary><strong>macOS</strong></summary>

| Package manager | Status | Notes |
|-----------------|--------|-------|
| **Homebrew** | Planned | Parsing implemented (`brew.py`). Requires a post-install wrapper or Homebrew *tap* to invoke the CLI automatically. See [Contributing](CONTRIBUTING.md). |

</details>

<details>
<summary><strong>Windows</strong></summary>

| Package manager | Status | Notes |
|-----------------|--------|-------|
| **Chocolatey** | Planned | Parser implemented (`chocolatey.py`). Needs a PowerShell extension/post-install script. |
| **Winget** | Planned | Parser implemented (`winget.py`). Requires a `winget` source extension or scheduled task to call the CLI. |

See the [Contributing guide](CONTRIBUTING.md) if you’d like to help wire up these back-ends.

</details>

---

## Configuration

### User Scope (Default)

User scope logs packages for the current user only. Files are stored in `~/.local/share/prez-pkglog/`.

**Configuration file**: `~/.config/prez-pkglog/prez_pkglog.conf`

```ini
[main]
scope = user
enable_dnf_hooks = true
enable_download_monitoring = true
downloads_dir = ~/Downloads
monitored_extensions = .rpm, .deb, .pkg.tar.zst, .tar.gz, .zip, .AppImage
log_format = both
```

### System Scope (Requires Administrator)

System scope logs packages system-wide. Files are stored in `/var/log/prez-pkglog/`.

**Configuration file**: `/etc/prez-pkglog/prez_pkglog.conf`

```ini
[main]
scope = system
enable_dnf_hooks = true
enable_download_monitoring = false
# downloads_dir and monitored_extensions are ignored in system scope
log_format = both
```

### DNF Plugin Configuration

**User scope**: `~/.config/dnf/plugins/prez_pkglog.conf`

```ini
[main]
enabled = 1
scope = user
```

**System scope**: `/etc/dnf/plugins/prez_pkglog.conf`

```ini
[main]
enabled = 1
scope = system
```

---

## Usage

All commands can be run with `--scope user` (default) or `--scope system` (requires `sudo`).

### Setup

Initializes configuration and directories.
```bash
prez-pkglog setup
```

### Check Status

Show current status and statistics.
```bash
prez-pkglog status
```

### Start Monitoring

Starts the monitoring daemon. For users, this monitors the downloads directory.
```bash
# Start download monitoring (user scope only, foreground)
prez-pkglog daemon

# Run continuously via systemd-user service
# (the unit file is shipped in /usr/lib/systemd/user by the RPM)
#
# 1. Reload user units to ensure systemd sees the new file
systemctl --user daemon-reload
# 2. Enable + start the logger – this will automatically create
#    ~/.config/systemd/user/ if it does not already exist.
systemctl --user enable --now prez-pkglog.service

# Optional: keep the service running even after logging out
sudo loginctl enable-linger "$USER"
```

### Query Logs

Search the package logs.
```bash
# Find all packages with 'nginx' in the name
prez-pkglog query --name nginx

# Find packages installed with dnf in the last 30 days
prez-pkglog query --manager dnf --days 30
```

### Export Logs

Export the full log to stdout.
```bash
# Export user logs as JSON
prez-pkglog export --format json
```

### Manual Logging

Manually log a package installation or removal.
```bash
# Log a package installation
prez-pkglog install package-name dnf

# Log a package removal
prez-pkglog remove package-name dnf

# Log a downloaded file
prez-pkglog install downloaded-file.zip download
```

---

## Shell Integration

### Shell wrapper to log every git clone

#### .zshrc

```bash
function pkglog_preexec() {
    [[ $1 == git\ clone* ]] || return
    local repo=${${1#git clone }##*/}
    repo=${repo%.git}
    prez-pkglog install $repo git
}
autoload -Uz add-zsh-hook
add-zsh-hook preexec pkglog_preexec
```

#### .bashrc

```bash
function _pkglog_bash_preexec() {
   [[ $BASH_COMMAND == git\ clone* ]]  || return
   local repo=${BASH_COMMAND#git clone}
   repo=${repo##*/}
   repo=${repo%.git}
   prez-pkglog install "$repo" git
}
```

#### config.fish

```bash
function fish_preexec --on-event fish_preexec
  if string match -rq '^git clone ' -- $argv[1]
    set repo (basename (string replace -r '^git clone +' '' $argv[1]) .git)
    prez-pkglog install $repo git
  end
end
```

---

## Log File Examples

### JSON Format

```json
[
  {
    "name": "neovim",
    "manager": "dnf",
    "action": "install",
    "date": "2025-06-21T17:02:41-05:00",
    "removed": false,
    "scope": "user",
    "version": "0.9.5-1.fc42",
    "metadata": {
      "arch": "x86_64",
      "repo": "fedora"
    }
  },
  {
    "name": "firefox-120.0.tar.bz2",
    "manager": "download",
    "action": "install",
    "date": "2025-06-21T18:30:15-05:00",
    "removed": false,
    "scope": "user",
    "metadata": {
      "file_path": "/home/user/Downloads/firefox-120.0.tar.bz2",
      "file_size": 52428800,
      "file_type": ".tar.bz2"
    }
  }
]
```

### TOML Format

```toml
[[package]]
name = "neovim"
manager = "dnf"
action = "install"
date = "2025-06-21T17:02:41-05:00"
removed = false
scope = "user"
version = "0.9.5-1.fc42"

[package.metadata]
arch = "x86_64"
repo = "fedora"

[[package]]
name = "firefox-120.0.tar.bz2"
manager = "download"
action = "install"
date = "2025-06-21T18:30:15-05:00"
removed = false
scope = "user"

[package.metadata]
file_path = "/home/user/Downloads/firefox-120.0.tar.bz2"
file_size = 52428800
file_type = ".tar.bz2"
```

---

## File Locations

### User Scope

- **Log files**: `~/.local/share/prez-pkglog/`
  - `packages.json`
  - `packages.toml`
- **Configuration**: `~/.config/prez-pkglog/prez_pkglog.conf`
- **DNF plugin config**: `~/.config/dnf/plugins/prez_pkglog.conf`

### System Scope

- **Log files**: `/var/log/prez-pkglog/`
  - `packages.json`
  - `packages.toml`
- **Configuration**: `/etc/prez-pkglog/prez_pkglog.conf`
- **DNF plugin config**: `/etc/dnf/plugins/prez_pkglog.conf`

---

## Building the RPM yourself

With the provided `Makefile`, building and installing a local version of the RPM is simple.

```bash
# Create the SRPM and RPM packages
make rpm

# Install the newly built package
make install
```

The `Makefile` handles placing the source tarball in the correct `rpmbuild` directory for you.

---

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

---

## License

MIT License (see LICENSE)

---
