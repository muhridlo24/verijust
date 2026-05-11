"""Backwards compatibility shim; see :mod:`app.core.aws_connection`.

This module previously contained an ``AWSClient`` implementation.  During a
refactor the real logic was moved to ``aws_connection.py`` and this file now
merely re-exports the public symbols so that existing imports continue to
work.

New code should import directly from ``app.core.aws_connection``.
"""

from app.core.aws_connection import aws_client, AWSClient, init_aws

# expose the same names that used to live here
__all__ = ["aws_client", "AWSClient", "init_aws"]
