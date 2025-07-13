"""Helper functions for backend implementations"""

from __future__ import annotations

import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


# Pacman helpers
def parse_pacman_query_line(line: str) -> Optional[Tuple[str, str]]:
    """Safely parse a single line from ``pacman -Q`` output.

    The expected format is ``"<name> <version>"``.  If the line cannot be
    parsed for example, because it is empty, contains too many/few tokens, or
    either the *name* or *version* part is missing. The function returns
    ``None`` instead of raising an exception so that callers can simply skip
    invalid lines.

    Parameters

    line:
        Raw text line from pacman output **including** the trailing newline
        character.

    Returns:
            tuple[str, str] | None:
            A tuple ``(name, version)`` if the line was parsed successfully,
            otherwise ``None``.
    """

    # Trim whitespace and ignore completely empty lines
    line = line.strip()
    if not line:
        return None
    # A valid pacman line has exactly one space separating *name* and *version*.
    try:
        name, version = line.rsplit(" ", 1)
    except ValueError:
        logger.debug("Skipping malformed pacman line (split error): %s", line)
        return None

    # Guard against empty components which indicate a malformed entry.
    if not name or not version:
        logger.debug("Skipping malformed pacman line (empty fields): %s", line)
        return None

    return name, version
