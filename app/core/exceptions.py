# app/exceptions.py

class InvalidTopicsError(Exception):
    """Raised when the topics input is invalid."""
    pass

class InvalidProviderConfigError(Exception):
    """Raised when the provider configuration is invalid."""
    pass
