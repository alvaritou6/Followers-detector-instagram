import json

def extract_users_smart(data, users_found):
    """
    Recursively scans JSON data to find usernames, handling multiple Instagram formats.
    """
    if isinstance(data, dict):
        # Check for standard user entry pattern
        if 'string_list_data' in data:
            user_found = None
            
            # STRATEGY 1: Check 'string_list_data' -> 'value' (Standard Followers format)
            try:
                data_list = data['string_list_data']
                if isinstance(data_list, list) and len(data_list) > 0:
                    item = data_list[0]
                    if isinstance(item, dict) and 'value' in item:
                        user_found = item['value']
            except Exception:
                pass

            # STRATEGY 2: Check 'title' field (Standard Following format)
            if not user_found and 'title' in data:
                title = data['title']
                if isinstance(title, str) and title.strip():
                    user_found = title

            if user_found:
                users_found.add(user_found)

        # Recursive search for nested structures
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                extract_users_smart(value, users_found)

    elif isinstance(data, list):
        for item in data:
            extract_users_smart(item, users_found)

def load_users(filename, label):
    users = set()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            extract_users_smart(data, users)
            
    except FileNotFoundError:
        print(f"[ERROR] File not found: '{filename}'")
        return set()
    except Exception as e:
        print(f"[ERROR] Could not read '{filename}': {e}")
        return set()

    print(f"[INFO] {label}: {len(users)} users found.")
    return users

def save_list(filename, user_set, header):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for user in sorted(user_set):
                f.write(f"{user}\n")
        print(f"[SUCCESS] {header} saved to '{filename}' ({len(user_set)} users).")
    except Exception as e:
        print(f"[ERROR] Could not write to '{filename}': {e}")

def main():
    print("--- Instagram Connections Analysis ---")
    
    # Ensure these filenames match your local files
    file_followers = 'followers_1.json'
    file_following = 'following.json'

    followers = load_users(file_followers, "Followers")
    following = load_users(file_following, "Following")

    if not followers or not following:
        print("\n[CRITICAL] Analysis aborted. One or both lists are empty.")
        print("Please check your JSON files.")
        return

    # Logic: Set Operations
    not_following_back = following - followers
    fans = followers - following

    print("\n--- ANALYSIS RESULTS ---")
    
    # 1. Not Following Back (Deficit)
    save_list('not_following_back.txt', not_following_back, "Not Following Back")
    
    # 2. Fans (Surplus)
    save_list('fans.txt', fans, "Fans (You don't follow back)")

    print("\n[DONE] Process completed.")

if __name__ == "__main__":
    main()