"""One place to configure logging for the whole app.

Beginners often reach for ``print()`` to see what their code is doing.
Switching to the standard :mod:`logging` module early pays off: you get
severity levels, timestamps, and the ability to turn detail up or down
without editing code. This module wires that up once, driven by two flags.
"""

from __future__ import annotations

import logging


def configure_logging(verbose: bool = False, quiet: bool = False) -> None:
    """Configure the root logger's level and message format.

    * ``verbose`` -> DEBUG   (show everything, including diagnostic detail)
    * ``quiet``   -> WARNING (show only warnings and errors)
    * neither     -> INFO    (the sensible default)

    ``verbose`` wins if both happen to be set. We pass ``force=True`` so that
    calling this more than once (for example across tests) reliably *resets*
    the configuration instead of being silently ignored the second time.
    """
    if verbose:
        level = logging.DEBUG
    elif quiet:
        level = logging.WARNING
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        force=True,
    )
