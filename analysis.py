import argparse
import json
import logging
import os
from typing import Any, Set


def normalize_username(u: str) -> str:
    if not isinstance(u, str):
        return ''
    u = u.strip()
    if u.startswith('@'):
        u = u[1:]
    return u.lower()


def extract_users_smart(data: Any, users_found: Set[str]):
    """Recursively scans JSON data to find usernames in common Instagram export shapes.

    Tries several heuristics: common keys (`username`, `user`, `title`, `value`),
    list entries under `string_list_data`, and `edge/node` patterns.
    """
    if isinstance(data, dict):
        # common direct fields
        for key in ('username', 'user', 'user_name', 'title'):
            if key in data and isinstance(data[key], str):
                uname = normalize_username(data[key])
                if uname:
                    users_found.add(uname)

        # string_list_data pattern
        if 'string_list_data' in data:
            try:
                data_list = data.get('string_list_data')
                if isinstance(data_list, list):
                    for item in data_list:
                        if isinstance(item, dict) and 'value' in item:
                            uname = normalize_username(item['value'])
                            if uname:
                                users_found.add(uname)
            except Exception:
                pass

        # edge/node pattern common in GraphQL-like exports
        if 'edges' in data and isinstance(data['edges'], list):
            for edge in data['edges']:
                if isinstance(edge, dict) and 'node' in edge:
                    extract_users_smart(edge['node'], users_found)

        # generic recursive descent
        for value in data.values():
            if isinstance(value, (dict, list)):
                extract_users_smart(value, users_found)

    elif isinstance(data, list):
        for item in data:
            extract_users_smart(item, users_found)

def load_users(filename, label):
    users = set()
    if not os.path.exists(filename):
        logging.error("File not found: '%s'", filename)
        return set()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            extract_users_smart(data, users)
    except Exception as e:
        logging.error("Could not read '%s': %s", filename, e)
        return set()

    logging.info("%s: %d users found.", label, len(users))
    return users

def save_list(filename, user_set, header, as_json=False):
    try:
        os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
        if as_json:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(sorted(user_set), f, ensure_ascii=False, indent=2)
        else:
            with open(filename, 'w', encoding='utf-8') as f:
                for user in sorted(user_set):
                    f.write(f"{user}\n")
        logging.info("%s saved to '%s' (%d users).", header, filename, len(user_set))
    except Exception as e:
        logging.error("Could not write to '%s': %s", filename, e)

def main():
    parser = argparse.ArgumentParser(description="Instagram followers/following analysis")
    parser.add_argument('--followers', '-f', default='followers_1.json', help='Followers JSON file')
    parser.add_argument('--following', '-g', default='following.json', help='Following JSON file')
    parser.add_argument('--outdir', '-o', default='.', help='Output directory for lists')
    parser.add_argument('--json', action='store_true', dest='as_json', help='Save outputs as JSON arrays')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable debug logging')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format='[%(levelname)s] %(message)s')

    logging.info('Starting Instagram Connections Analysis')

    followers = load_users(args.followers, 'Followers')
    following = load_users(args.following, 'Following')

    if not followers or not following:
        logging.critical('Analysis aborted. One or both lists are empty. Please check your JSON files.')
        return

    # Set operations
    not_following_back = following - followers
    fans = followers - following

    logging.info('ANALYSIS RESULTS: Not following back=%d, Fans=%d', len(not_following_back), len(fans))

    out_not_following = os.path.join(args.outdir, 'not_following_back.json' if args.as_json else 'not_following_back.txt')
    out_fans = os.path.join(args.outdir, 'fans.json' if args.as_json else 'fans.txt')

    save_list(out_not_following, not_following_back, 'Not Following Back', as_json=args.as_json)
    save_list(out_fans, fans, "Fans (You don't follow back)", as_json=args.as_json)

    logging.info('Process completed.')

if __name__ == "__main__":
    main()