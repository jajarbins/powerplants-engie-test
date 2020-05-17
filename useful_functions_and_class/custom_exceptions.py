class AlgorithmError(Exception):
    """Raised when case is not coovered by the algorithm."""
    pass


class SanityCheckInternalError(Exception):
    """Raised when sanity check function's parameters are not properly set"""
    pass
