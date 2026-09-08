"""Local credential storage. Never source the file as shell code."""
import json
import os
import tempfile
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parents[1] / '.env'
KEYS = ('GROWW_API_KEY', 'GROWW_API_SECRET', 'GROWW_ACCESS_TOKEN')


def credentials(path=ENV_PATH):
    values = {}
    if path.exists():
        for line in path.read_text().splitlines():
            key, sep, value = line.partition('=')
            key = key.strip()
            if sep and key in KEYS:
                value = value.strip()
                try:
                    if value.startswith('"'):
                        value = json.loads(value)
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                except ValueError:
                    raise ValueError('Invalid credential file format') from None
                if not isinstance(value, str):
                    raise ValueError('Invalid credential file format')
                values[key] = value
    for key in KEYS:
        if os.environ.get(key):
            values[key] = os.environ[key]
    return values


def save_credentials(key, secret, path=ENV_PATH):
    if not key or not secret:
        raise ValueError('Both credentials are required')
    if path.is_symlink():
        raise ValueError('Credential file must not be a symbolic link')
    lines = path.read_text().splitlines() if path.exists() else []
    lines = [line for line in lines if line.partition('=')[0].strip() not in KEYS]
    lines += ['GROWW_API_KEY=' + json.dumps(key), 'GROWW_API_SECRET=' + json.dumps(secret)]
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as f:
            temp = Path(f.name)
            os.fchmod(f.fileno(), 0o600)
            f.write('\n'.join(lines) + '\n')
        os.replace(temp, path)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


def authenticated_client(values=None):
    try:
        from growwapi import GrowwAPI
    except ImportError:
        raise ValueError('Install the optional SDK: pip install -e ".[groww]"') from None
    values = credentials() if values is None else values
    key, secret = values.get('GROWW_API_KEY'), values.get('GROWW_API_SECRET')
    try:
        # Prefer reusable credentials over an old saved access token.
        token = GrowwAPI.get_access_token(api_key=key, secret=secret) if key and secret else values.get('GROWW_ACCESS_TOKEN')
        if not isinstance(token, str) or not token:
            raise ValueError('Missing credentials')
        return GrowwAPI(token)
    except Exception as exc:
        # SDK exception messages may include request details. Map only the class
        # to an actionable, secret-free diagnosis.
        kind = type(exc).__name__
        if kind == 'GrowwAPIAuthorisationException':
            message = 'Groww API key approval is required or has expired.'
        elif kind == 'GrowwAPIAuthenticationException':
            message = 'Groww rejected the saved API credentials.'
        elif kind == 'GrowwAPIRateLimitException':
            message = 'Groww API rate limit reached; retry later.'
        elif kind == 'GrowwAPITimeoutException':
            message = 'Groww API request timed out; retry later.'
        else:
            message = 'Groww authentication request failed.'
        raise ValueError(message) from None
