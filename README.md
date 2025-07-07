[![Lint Status](https://github.com/<OWNER>/<REPO>/actions/workflows/lint.yml/badge.svg)](https://github.com/<OWNER>/<REPO>/actions/workflows/lint.yml)

# prez-pkglog

**prez-pkglog** is a cross-distro/platform package-activity logger that records every install locally and removal event on your system, then writes an append-only history in both JSON and TOML. This is useful for keeping track of what packages are installed on your system.

---

## Features

- **Zero-maintenance** - hooks directly into DNF and PackageKit; no polling.
- **Two loggers** - automatically mirrors entries to 'packages.json' and 'packages.toml' files.
- **Modular backends** - bolt on APT, Pacman, Homebrew, etc. with a one-liner.
- **Removal provenance** - entries are never deleted; removals get an '# --REMOVED--' sentinel (TOML) or 'removed=true' (JSON).
- **Scope-aware logging** - choose between user-only or system-wide package tracking.
- **Download monitoring** - automatically log files downloaded to your Downloads folder.

---

## Installation

```bash
# one-time enable (Copr)
sudo dnf copr enable prez/prez-pkglog
sudo dnf install prez-pkglog
```

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
log_format = both
```

### DNF Plugin Configuration

**User scope**: `~/.config/dnf/plugins/prez_pkglogger.conf`

```ini
[main]
enabled = 1
scope = user
```

**System scope**: `/etc/dnf/plugins/prez_pkglogger.conf`

```ini
[main]
enabled = 1
scope = system
```

---

## Usage

### Setup

```bash
# Setup for current user (default)
prez-pkglog setup --scope user

# Setup for system-wide logging (requires sudo)
sudo prez-pkglog setup --scope system
```

### Check Status

```bash
# Check user scope status
prez-pkglog status --scope user

# Check system scope status (requires sudo)
sudo prez-pkglog status --scope system
```

### Start Monitoring

```bash
# Start download monitoring (user scope only)
prez-pkglog daemon --scope user

# Start system monitoring (requires sudo)
sudo prez-pkglog daemon --scope system
```

### Export Logs

```bash
# Export user logs as JSON
prez-pkglog export --scope user --format json

# Export system logs as TOML (requires sudo)
sudo prez-pkglog export --scope system --format toml
```

### Manual Logging

```bash
# Log a package installation
prez-pkglog install package-name dnf

# Log a package removal
prez-pkglog remove package-name dnf

# Log a downloaded file
prez-pkglog install downloaded-file download
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
- **DNF plugin config**: `~/.config/dnf/plugins/prez_pkglogger.conf`

### System Scope
- **Log files**: `/var/log/prez-pkglog/`
  - `packages.json`
  - `packages.toml`
- **Configuration**: `/etc/prez-pkglog/prez_pkglog.conf`
- **DNF plugin config**: `/etc/dnf/plugins/prez_pkglogger.conf`

---

## Building the RPM yourself

```bash
python -m build --sdist
rpmbuild -ts dist/prez-pkglog-0.1.0.tar.gz
mock -r fedora-42-x86_64 ~/rpmbuild/SRPMS/prez-pkglog-0.1.0-1.fc42.src.rpm
sudo dnf install ~/rpmbuild/RPMS/noarch/prez-pkglog-0.1.0-1.fc42.noarch.rpm
```

---

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

---

## License

MIT License (see LICENSE)

---
