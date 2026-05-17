"""Built-in credential sources."""

from craik.runtime.auth.sources.api_key import EnvVarApiKeySource
from craik.runtime.auth.sources.cli_bridge import (
    CLIBridgeCredentialError,
    CLIBridgeCredentialSource,
)
from craik.runtime.auth.sources.local_cli_oauth import (
    DEFAULT_CLAUDE_CREDENTIALS_PATH,
    LocalCLICredentialError,
    LocalCLICredentialSource,
)

__all__ = [
    "DEFAULT_CLAUDE_CREDENTIALS_PATH",
    "CLIBridgeCredentialError",
    "CLIBridgeCredentialSource",
    "EnvVarApiKeySource",
    "LocalCLICredentialError",
    "LocalCLICredentialSource",
]
