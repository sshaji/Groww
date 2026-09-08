"""Local login and read-only snapshot with user-authorized credential persistence."""
import argparse
import getpass
import json
import os
import tempfile
import warnings
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from .auth import save_credentials, authenticated_client


def snapshot(client):
    holdings = client.get_holdings_for_user(timeout=10)
    if not isinstance(holdings, dict) or not isinstance(holdings.get('holdings'), list):
        raise ValueError('Unexpected holdings response')
    orders = []
    seen = set()
    for page in range(100):
        response = client.get_order_list(segment='CASH', page=page, page_size=25)
        batch = response.get('order_list') if isinstance(response, dict) else None
        if not isinstance(batch, list):
            raise ValueError('Unexpected orders response')
        for order in batch:
            identity = order.get('groww_order_id')
            if not identity or identity in seen:
                raise ValueError('Orders pagination could not be verified')
            seen.add(identity)
            orders.append(order)
        if len(batch) < 25:
            break
    else:
        raise ValueError('Too many orders; snapshot is incomplete')
    return {'fetched_at': datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),
            'holdings': holdings['holdings'], 'today_orders': orders,
            'note': 'Read-only account snapshot. Orders cover today only. No live market quotes requested.'}


def main():
    parser = argparse.ArgumentParser(description='Read Groww account using local credentials')
    parser.add_argument('--setup', action='store_true', help='Privately enter and save credentials in .env')
    args = parser.parse_args()
    print('Connect Groww — read holdings and today\'s orders. No trades will be placed.')
    try:
        # Refuse a fallback that could echo a secret if no controlling terminal exists.
        if args.setup:
            print('Credentials will be saved in this project\'s private .env file.')
            with warnings.catch_warnings():
                warnings.simplefilter('error', getpass.GetPassWarning)
                key = getpass.getpass('API key (hidden): ').strip()
                secret = getpass.getpass('API secret (hidden): ').strip()
            values = {'GROWW_API_KEY': key, 'GROWW_API_SECRET': secret}
            client = authenticated_client(values)
            save_credentials(key, secret)
            print('Credentials saved locally with owner-only file permissions.')
        else:
            client = authenticated_client()
        result = snapshot(client)
        directory = Path(__file__).resolve().parents[1] / 'data'
        directory.mkdir(exist_ok=True)
        target = directory / 'account-snapshot.json'
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', dir=directory, delete=False) as handle:
                temp_path = Path(handle.name)
                json.dump(result, handle, indent=2, allow_nan=False)
            os.replace(temp_path, target)
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
        print('Connected. Saved fresh account data to data/account-snapshot.json.')
        print('You can now ask the assistant to refresh or read your account.')
    except (KeyboardInterrupt, EOFError):
        print('\nCancelled. No new snapshot saved.')
        return 1
    except Exception:
        # Never print SDK exception messages, which may contain authentication data.
        print('Connection failed. Check API key, secret, daily approval and network access.')
        print('No new snapshot saved; any previous snapshot remains unchanged.')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
