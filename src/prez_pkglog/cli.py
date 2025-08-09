import click
import os
from functools import wraps
import datetime as dt
import json


def get_default_scope() -> str:
    """Get the default scope from configuration, falling back to 'user' if not configured.

    Checks system config first, then user config.
    """
    import json
    from pathlib import Path

    # Check system config first
    system_config = Path("/etc/prez-pkglog/prez-pkglog.conf")
    if system_config.exists():
        try:
            data = json.loads(system_config.read_text())
            if isinstance(data, dict) and data.get("scope") == "system":
                return "system"
        except (OSError, json.JSONDecodeError):
            pass

    # Check user config
    user_config = Path.home() / ".config/prez-pkglog/prez-pkglog.conf"
    if user_config.exists():
        try:
            data = json.loads(user_config.read_text())
            if isinstance(data, dict):
                return data.get("scope", "user")
        except (OSError, json.JSONDecodeError):
            pass

    # Default fallback
    return "user"


def require_sudo_for_system_scope(f):
    @wraps(f)
    def decorated_function(scope, *args, **kwargs):
        """Wrapper that ensures proper privilege for system scope."""
        if scope == "system" and os.geteuid() != 0:
            click.echo("Error: System scope requires administrative privileges.")
            click.echo("Falling back to user scope. Run with sudo or use --scope user.")
            scope = "user"

        return f(*args, scope=scope, **kwargs)

    return decorated_function


@click.group()
def cli():
    """Prez Package Logger a local package installation and removal logger"""
    pass


@cli.command()
@click.option(
    "--setup",
    "scope",
    type=click.Choice(["user", "system"]),
    help="Setup configuration and directories",
    default=get_default_scope,
    show_default=True,
)
@require_sudo_for_system_scope
def setup(scope):
    """Setup configuration and directories"""
    from .config import Config
    from .logger import PackageLogger

    config = Config()
    config.set("scope", scope)
    config.save()

    logger = PackageLogger(config)

    click.echo(f"Setup complete for {scope} scope.")
    click.echo(f"Log directory created at: {logger.data_dir}")
    click.echo(f"Configuration saved to: {config.config_file}")


@cli.command()
@click.option(
    "--scope",
    type=click.Choice(["user", "system"]),
    default=get_default_scope,
    help="Logging scope",
)
@require_sudo_for_system_scope
def status(scope):
    """Show current status and statistics"""
    from .config import Config
    from .logger import PackageLogger

    config = Config()
    config.set("scope", scope)
    config.save()

    logger = PackageLogger(config)
    stats = logger.get_statistics()

    click.echo(f"Scope: {stats['scope']}")
    click.echo(f"Total packages logged: {stats['total']}")
    click.echo(f"Installed: {stats['installed']}")
    click.echo(f"Removed: {stats['removed']}")
    click.echo(f"Downloads: {stats['downloads']}")
    click.echo(f"Log location: {logger.data_dir}")


@cli.command()
@click.option(
    "--scope",
    type=click.Choice(["user", "system"]),
    default=get_default_scope,
    help="Logging scope",
)
@require_sudo_for_system_scope
def daemon(scope):
    """Start monitoring daemon"""
    import time
    from .config import Config
    from .logger import PackageLogger
    from .monitors.downloads import DownloadsMonitor

    config = Config()
    config.set("scope", scope)
    config.save()

    logger = PackageLogger(config)

    if scope == "user":
        monitor = DownloadsMonitor(logger)
        try:
            monitor.start()
            click.echo(f"Monitoring started (scope: {scope}). Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop()
            click.echo("Monitoring stopped.")
    else:
        click.echo(f"System scope monitoring started (scope: {scope}).")
        click.echo("Download monitoring is only available in user scope.")
        click.echo("Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            click.echo("Monitoring stopped.")


@cli.command()
@click.option(
    "--scope",
    type=click.Choice(["user", "system"]),
    default=get_default_scope,
    help="Logging scope",
)
@click.option("--format", default="json", type=click.Choice(["json", "toml"]))
@require_sudo_for_system_scope
def export(scope, format):
    """Export package log in specified format"""
    from .config import Config
    from .logger import PackageLogger

    config = Config()
    config.set("scope", scope)
    config.save()

    logger = PackageLogger(config)

    if format == "json":
        click.echo(logger.json_file.read_text())
    else:
        click.echo(logger.toml_file.read_text())


@cli.command()
@click.argument("name")
@click.argument("manager")
@click.option(
    "--scope",
    type=click.Choice(["user", "system"]),
    default=get_default_scope,
    help="Logging scope",
)
@require_sudo_for_system_scope
def install(name, manager, scope):
    """Log a package installation"""
    from .config import Config
    from .logger import PackageLogger

    config = Config()
    config.set("scope", scope)
    config.save()
    logger = PackageLogger(config)
    logger.log_package(name, manager, "install")
    click.echo(f"Logged install of '{name}' using '{manager}'.")


@cli.command()
@click.argument("name")
@click.argument("manager")
@click.option(
    "--scope",
    type=click.Choice(["user", "system"]),
    default=get_default_scope,
    help="Logging scope",
)
@require_sudo_for_system_scope
def remove(name, manager, scope):
    """Log a package removal"""
    from .config import Config
    from .logger import PackageLogger

    config = Config()
    config.set("scope", scope)
    config.save()
    logger = PackageLogger(config)
    logger.log_package(name, manager, "remove")
    click.echo(f"Logged removal of '{name}' using '{manager}'.")


@cli.command()
@click.option("--name", default=None, help="Filter by package name (contains)")
@click.option("--manager", default=None, help="Filter by package manager")
@click.option("--days", default=None, type=int, help="Filter by days since log entry")
@click.option(
    "--scope",
    type=click.Choice(["user", "system"]),
    default=get_default_scope,
    help="Logging scope",
)
@require_sudo_for_system_scope
def query(name, manager, days, scope):
    """Query the package log"""
    from .config import Config
    from .logger import PackageLogger

    config = Config()
    config.set("scope", scope)
    config.save()
    logger = PackageLogger(config)

    since = None
    if days:
        since = dt.date.today() - dt.timedelta(days=days)

    results = logger.query(name=name, manager=manager, since=since)

    if not results:
        click.echo("No results found.")
        return

    for res in results:
        res_str = json.dumps(res, indent=2)
        click.echo(res_str)
