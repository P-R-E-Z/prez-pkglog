import subprocess
from typing import List, Optional


def run_and_log(cmd: List[str], name_pos: int, manager: str) -> Optional[int]:
    """Execute a package management command and log the installation

    Args:
        cmd: The command to execute as a list of strings
        name_pos: The index in cmd where the package name is located
        manager: The name of the package manager being used

    Returns:
        int: The return code of the package manager command, or None if logging fails
    """
    if not cmd or name_pos >= len(cmd):
        return None

    # Run the package manager command
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        return result.returncode

    try:
        name = cmd[name_pos]
        log_result = subprocess.run(
            ["prez-pkglog", "install", name, manager], check=False
        )
        if log_result.returncode != 0:
            # Log the failure but don't fail the operation
            print(f"Warning: Failed to log install of {name} with {manager}")
        return result.returncode
    except (IndexError, subprocess.SubprocessError) as e:
        print(f"Error during logging: {e}")
        return result.returncode
