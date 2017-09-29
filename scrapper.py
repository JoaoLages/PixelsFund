from utils import write_json, read_json
import json
import requests
from bs4 import BeautifulSoup
import argparse
import sys
import os.path


UNKNOWN_TOKEN = '__unknown__'
MASTER_WALLET = '0x3d417b8305aa60688385a1ca56530130c77f8739'
initial_wallet2user = {
    '0x4140a568eccb4b8a6b87a69797b4c9bb23c29889': {
        'user': 'celso', 'balance': 30000
    },
    '0xaa523732baf8dfc633f6b30a5cd6b8f688e10dbb': {
        'user': 'Alexandre Santos', 'balance': 25295
    },
    '0x91c897121fed96db5f6c23930aabb1ee8eafe25f': {
        'user': 'Benjamim Junior', 'balance': 30000
    },
    '0x48e6f88f863c3178f470d92f799c6959fe98e2fe': {
        'user': 'Claudio Gamboa', 'balance': 25614
    },
    '0xf116e7c317c1ad1df34c1253685d37587cfd7f0c': {
        'user': 'Andre Cruz', 'balance': 25188
    },
    '0xe90d6f8585f75eb7cef5fba0674cac90bcb852de': {
        'user': 'Nuno Loureiro', 'balance': 25100
    },
    '0xde2f49122f680b24a9cbee64a2c7a28642bc3d64': {
        'user': 'Nuno Jesus', 'balance': 25400
    },
    '0xde67adcc0bd2e4b41c761e8bb4eef8643836bdd0': {
        'user': 'Rita Ralha', 'balance': 25300
    },
    '0xd27678cdaf0c2d1c5c3de4cbbc02eb01f93525bb': {
        'user': 'Renato Leao', 'balance': 25700
    },
    '0xfb721ba0f3e0054a8d5b669103cbcd4d3956b321': {
        'user': 'Luis Kohler', 'balance': 25000
    },
    '0xf98dd488d2e77589461021650026e20a503d0d6c': {
        'user': 'Tocha', 'balance': 27000
    },
    '0x0992a7254fd5a2547795a7a4eb64ec62defa86e4': {
        'user': 'Joao Sil', 'balance': 26100
    },
    '0x4f45c3ebbca659e458ace3984bb7bb3de264b536': {
        'user': 'Julio Faerman', 'balance': 25106
    },
    '0xcefe8abd132eeec1a6299502f7287cb072da6cfc': {
        'user': 'Luis Mendes', 'balance': 25000
    },
    '0xaaf5bdf1c3687dfb7a5b9e9058c64dfba391f8e4': {
        'user': 'Jacques West', 'balance': 25001
    },
    '0x3593de4cb08563806e41a74c39b828689c2e29a4': {
        'user': 'Pedro Ferreira', 'balance': 25000
    }
}


def get_wallet2user(wallet2user=None,
                    url_all_users='https://api.pixels.camp/badges/owners/92',
                    url_user_page='https://api.pixels.camp/users'):
    """
    Constructs wallet2user dict
    :param wallet2user: dict (with 'user' and 'balance')
    :param url_all_users: url of to get all users
    :param url_user_page: url to get specific user info
    :return: wallet2user (new/updated)
    """
    users = json.loads(requests.get(url_all_users).text)['owners']['2017']

    if not wallet2user:
        wallet2user = initial_wallet2user
        usernames = [user['user'] for user in users]
    else:
        assert isinstance(wallet2user, dict)

        existing_users = {wallet2user[wallet]['user'] for wallet in wallet2user
                          if 'user' in wallet2user[wallet]}
        usernames = [user['user'] for user in users
                     if user['user'] not in existing_users]

    for user in usernames:
        wallet = json.loads(requests.get("%s/%s" % (url_user_page, user)).text)['wallet']
        if wallet not in {None, ''}:
            if wallet.lower() != MASTER_WALLET:  # Ignore master wallet
                if wallet.lower() not in wallet2user:
                    wallet2user[wallet.lower()] = {}
                wallet2user[wallet.lower()]['user'] = user

    return wallet2user


def get_projects_and_users(wallet2user=None,
                           projects_page='https://api.pixels.camp/project',
                           balances_page='http://moon.pixels.camp:8548/accounts'):
    """
    Get Project/People Info
    Returns projects info (json) and wallet2user dict (wallet as key and 'user' and 'balance' as values)
    """

    if not wallet2user:
        wallet2user = get_wallet2user()

    projects = json.loads(requests.get(projects_page).text)['projects']
    projects_wallets = []
    for i, project in enumerate(projects):
        # Get wallet
        projects_wallets.append("0x%s" % project['wallet'])

        # Initialize balance
        projects[i]['balance'] = 0

    aux_int = 0
    while True:
        aux_found = False

        page = '%s/%s' % (balances_page, aux_int)
        soup = BeautifulSoup(requests.get(page).content, "html.parser")
        for tr in soup.find_all('tr'):
            tds = [x.text for x in tr.find_all('td')]

            # FIXME: Hardcoded
            if tds and tds[1][-3:] == 'EXP':
                # It's a balance
                aux_found = True

                WALLET, BALANCE = tds[0], int(tds[1][:-3])
                try:
                    project_id = projects_wallets.index(WALLET)
                    projects[project_id]['balance'] = BALANCE
                except ValueError:
                    # Not a project index, user instead
                    if WALLET.lower() != MASTER_WALLET:  # Ignore master wallet
                        if WALLET.lower() not in wallet2user:
                            wallet2user[WALLET.lower()] = {}
                        wallet2user[WALLET.lower()]['balance'] = BALANCE

        if not aux_found:
            return wallet2user, projects

        aux_int += 50


def get_transactions(transactions=None,
                     exposure_page='http://moon.pixels.camp:8548/events',
                     keep_repeated=False):
    """
    Get all transactions of Exposure
    :param transactions: dict of dics(int)
    """
    if not transactions:
        # How much money each investor (key) invested in each project (values)
        transactions = {
            'from_to_amount': {},
            'transaction_ids': set()
        }
    else:

        assert isinstance(transactions['from_to_amount'], dict)

        assert isinstance(transactions['transaction_ids'], list)
        transactions['transaction_ids'] = set(transactions['transaction_ids'])

    aux_int = 0
    while True:
        aux_found = False

        page = '%s/%s' % (exposure_page, aux_int)
        soup = BeautifulSoup(requests.get(page).content, "html.parser")
        for tr in soup.find_all('tr'):
            tds = [x for x in tr.find_all('td')]

            # FIXME: Hardcoded
            if tds and tds[3].text[-3:] == 'EXP':
                # It's a transaction
                aux_found = True

                transaction_id = tds[0].find('a')['href']

                # Check if repeated (finish if so)
                if transaction_id in transactions['transaction_ids'] and not keep_repeated:
                    transactions['transaction_ids'] = list(transactions['transaction_ids'])
                    return transactions

                FROM, TO, AMOUNT = tds[1].text, tds[2].text, int(tds[3].text[:-3])

                if FROM != MASTER_WALLET:  # Ignore master wallet
                    if FROM not in transactions['from_to_amount']:
                        transactions['from_to_amount'][FROM] = {}
                    if TO not in transactions['from_to_amount'][FROM]:
                        transactions['from_to_amount'][FROM][TO] = []

                    transactions['from_to_amount'][FROM][TO].append(
                        {'balance': AMOUNT,
                         'timestamp': int(transaction_id.replace('_', '').replace('/event/', ''))}
                    )
                    transactions['transaction_ids'] |= {transaction_id}

        if not aux_found:
            transactions['transaction_ids'] = list(transactions['transaction_ids'])
            return transactions

        aux_int += 50


def argument_parser(sys_argv):
    # ARGUMENT HANDLING
    parser = argparse.ArgumentParser(
        prog='The script scrapes information from webpages',
    )
    parser.add_argument(
        '--wallet2user-file',
        type=str,
        default='wallet2user.json'
    )
    parser.add_argument(
        '--projects-file',
        type=str,
        default='projects.json'
    )
    parser.add_argument(
        '--transactions-file',
        type=str,
        default='transactions.json'
    )
    parser.add_argument(
        '--re-extract',
        type=bool,
        default=False,
        help='Re-extract everything'
    )
    args = parser.parse_args(sys_argv)

    return args


if __name__ == '__main__':
    # Argument handling
    args = argument_parser(sys.argv[1:])

    if not args.re_extract:
        if args.wallet2user_file and os.path.isfile(args.wallet2user_file):
            wallet2user = read_json(args.wallet2user_file)
        else:
            wallet2user = None

        if args.projects_file and os.path.isfile(args.projects_file):
            projects = read_json(args.projects_file)
        else:
            projects = None

        if args.transactions_file and os.path.isfile(args.transactions_file):
            transactions = read_json(args.transactions_file)
        else:
            transactions = None
    else:
        # Re-extract everything
        wallet2user, projects, transactions = None, None, None

    # FIXME: Some transactions with repeated ids (God knows why)
    if not transactions:
        args.re_extract = True

    # Build dicts
    wallet2user = get_wallet2user(wallet2user=wallet2user)
    wallet2user, projects = get_projects_and_users(wallet2user=wallet2user)
    transactions = get_transactions(transactions=transactions, keep_repeated=args.re_extract)

    # Write JSONS
    write_json(projects, 'projects.json')
    write_json(wallet2user, 'wallet2user.json')
    write_json(transactions, 'transactions.json')
