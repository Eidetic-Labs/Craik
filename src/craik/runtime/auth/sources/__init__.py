"""Built-in credential sources."""

from craik.runtime.auth.sources.api_key import EnvVarApiKeySource
from craik.runtime.auth.sources.cli_bridge import (
    CLIBridgeCredentialError,
    CLIBridgeCredentialSource,
)
from craik.runtime.auth.sources.factory import AuthProfileSourceError, source_for_auth_profile
from craik.runtime.auth.sources.local_cli_oauth import (
    DEFAULT_CLAUDE_CREDENTIALS_PATH,
    LocalCLICredentialError,
    LocalCLICredentialSource,
)
from craik.runtime.auth.sources.oidc_exchange import OIDCTokenExchangeSecretManager
from craik.runtime.auth.sources.secret_ref import (
    EnvVarSecretManager,
    FileSecretManager,
    SecretManager,
    SecretRefCredentialError,
    SecretRefCredentialSource,
)

__all__ = [
    "DEFAULT_CLAUDE_CREDENTIALS_PATH",
    "CLIBridgeCredentialError",
    "CLIBridgeCredentialSource",
    "EnvVarApiKeySource",
    "EnvVarSecretManager",
    "AuthProfileSourceError",
    "FileSecretManager",
    "LocalCLICredentialError",
    "LocalCLICredentialSource",
    "OIDCTokenExchangeSecretManager",
    "SecretManager",
    "SecretRefCredentialError",
    "SecretRefCredentialSource",
    "source_for_auth_profile",
]
