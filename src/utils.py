"""
Utility functions for RCN processing.
"""


def local(tag: str) -> str:
    """
    Return tag name without XML namespace.
    Example: '{uri}name' -> 'name'
    """
    if tag and "}" in tag:
        return tag.split("}", 1)[1]
    return tag

