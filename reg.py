import os
import time
import datetime
import json
import sys
import random
from colorama import init, Fore, Style
from eth_account import Account
from eth_account.messages import encode_defunct
from multiprocessing import Pool, cpu_count

init(autoreset=True)

USE_PROXY = False
proxies_list = []

def get_proxies():
    if USE_PROXY and proxies_list:
        proxy = random.choice(proxies_list)
        return {"http": proxy, "https": proxy}
    return None

def banner():
    print(Fore.GREEN + r"""
██████╗  ██████╗ ██████╗ ███████╗ █████╗ ███╗   ███╗ ██████╗ ███╗   ██╗
██╔══██╗██╔═══██╗██╔══██╗██╔════╝██╔══██╗████╗ ████║██╔═══██╗████╗  ██║
██║  ██║██║   ██║██████╔╝█████╗  ███████║██╔████╔██║██║   ██║██╔██╗ ██║
██║  ██║██║   ██║██╔══██╗██╔══╝  ██╔══██║██║╚██╔╝██║██║   ██║██║╚██╗██║
██████╔╝╚██████╔╝██║  ██║███████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██║ ╚████║
╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝                                                                      
              MADE BY :- Đôrêmon                               
    """ + Style.RESET_ALL)

def timestamp():
    return "[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]"

def log_info(msg):
    print(f"{timestamp()} {Fore.BLUE}[*] {msg}{Style.RESET_ALL}")

def log_success(msg):
    print(f"{timestamp()} {Fore.GREEN}[+] {msg}{Style.RESET_ALL}")

def log_error(msg):
    print(f"{timestamp()} {Fore.RED}[-] {msg}{Style.RESET_ALL}")

def get_auth_ticket(nonce):
    url = "https://api-kiteai.bonusblock.io/api/auth/get-auth-ticket"
    body = {"nonce": nonce}
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "Referer": "https://testnet.gokite.ai/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    log_info(f"Sending POST request to {url} with nonce: {nonce}")
    try:
        response = requests.post(url, headers=headers, json=body, proxies=get_proxies())
        log_info(f"Response status code: {response.status_code}")
        log_success("Raw response:")
        print(response.text)
        data = response.json()
        log_success("Parsed JSON response:")
        print(json.dumps(data, indent=2))
        return data
    except Exception as e:
        log_error(f"Error in get-auth-ticket request: {e}")
        return None

def sign_payload(payload, private_key):
    try:
        message = encode_defunct(text=payload)
        signed = Account.sign_message(message, private_key=private_key)
        signature = signed.signature.hex()
        if not signature.startswith("0x"):
            signature = "0x" + signature
        log_success(f"Message signed successfully: {signature}")
        return signature
    except Exception as e:
        log_error(f"Error signing payload: {e}")
        return None

def eth_auth(signed_message, nonce, referral_code):
    url = "https://api-kiteai.bonusblock.io/api/auth/eth"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site"
    }
    body = {
        "blockchainName": "ethereum",
        "signedMessage": signed_message,
        "nonce": nonce,
        "referralId": referral_code  # Using referral code provided by the user
    }
    log_info("Sending eth auth request...")
    try:
        response = requests.post(url, headers=headers, json=body, proxies=get_proxies())
        log_info(f"Response status code: {response.status_code}")
        log_success("Raw response:")
        print(response.text)
        data = response.json()
        log_success("Parsed JSON response:")
        print(json.dumps(data, indent=2))
        if data.get("success") and data.get("payload"):
            token = data["payload"]["session"]["token"]
            user_id = data["payload"]["account"]["userId"]
            return token, user_id
        else:
            log_error("eth auth API did not succeed or payload missing.")
            return None, None
    except Exception as e:
        log_error(f"Error in eth auth request: {e}")
        return None, None

def forward_api(url, token):
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "x-auth-token": token
    }
    log_info(f"Sending POST request to {url} with x-auth-token.")
    try:
        response = requests.post(url, headers=headers, json=None, proxies=get_proxies())
        log_info(f"Response status code: {response.status_code}")
        log_success("Raw response:")
        print(response.text)
        try:
            data = response.json()
            log_success("Parsed JSON response:")
            print(json.dumps(data, indent=2))
        except Exception:
            log_error("Response is not valid JSON.")
        return True
    except Exception as e:
        log_error(f"Error calling {url}: {e}")
        return False

def process_wallet(private_key, wallet_index, total_wallets, referral_code):
    log_info(f"Processing wallet {wallet_index}/{total_wallets}...")
    nonce = f"timestamp_{int(time.time() * 1000)}"
    log_info(f"Using nonce: {nonce}")
    auth_resp = get_auth_ticket(nonce)
    if auth_resp is None:
        log_error("Failed to get auth ticket. Skipping wallet.")
        return False
    payload = auth_resp.get("payload")
    if not payload:
        log_error("Auth ticket payload missing. Skipping wallet.")
        return False
    log_info(f"Message to sign: {payload}")
    signed_message = sign_payload(payload, private_key)
    if not signed_message:
        log_error("Failed to sign message. Skipping wallet.")
        return False
    token, user_id = eth_auth(signed_message, nonce, referral_code)
    if token is None or user_id is None:
        log_error("eth auth failed. Skipping wallet.")
        return False
    log_success("Account reg ✅")
    try:
        with open("userids.txt", "a", encoding="utf-8") as f:
            f.write(f"{user_id}\n")
        with open("key.txt", "a", encoding="utf-8") as f:
            f.write(f"{private_key}\n")
        with open("wallet.txt", "a", encoding="utf-8") as f:
            f.write(f"{Account.privateKeyToAccount(private_key).address}\n")
    except Exception as e:
        log_error(f"Error saving user data: {e}")
        return False
    social_url = "https://api-kiteai.bonusblock.io/api/forward-link/go/kiteai-mission-social-3"
    if forward_api(social_url, token):
        log_success("Join Tg ✅")
    else:
        log_error("Social API call failed.")
    tutorial_url = "https://api-kiteai.bonusblock.io/api/forward-link/go/kiteai-mission-tutorial-1"
    if forward_api(tutorial_url, token):
        log_success("Complete tutorial ✅")
    else:
        log_error("Tutorial API call failed.")
    return True

def generate_keys(num_keys):
    private_keys = []
    addresses = []
    for _ in range(num_keys):
        acct = Account.create()
        private_key = acct._private_key.hex()
        address = acct.address
        private_keys.append(private_key)
        addresses.append(address)
    return private_keys, addresses

def main():
    banner()
    referral_code = input("Enter your referral code: ").strip()
    num_refer = int(input("How many wallets would you like to refer?: ").strip())

    use_proxy_input = input("Do you want to use a proxy? (yes/no): ").strip().lower()
    global USE_PROXY, proxies_list
    if use_proxy_input in ["yes", "y"]:
        USE_PROXY = True
        try:
            with open("proxy.txt", "r", encoding="utf-8") as f:
                proxies_list = [line.strip() for line in f if line.strip()]
            if not proxies_list:
                log_error("No proxies found in proxy.txt, proceeding without proxy.")
                USE_PROXY = False
        except Exception as e:
            log_error(f"Error reading proxy.txt: {e}. Proceeding without proxy.")
            USE_PROXY = False
    else:
        USE_PROXY = False

    private_keys, _ = generate_keys(num_refer)
    total_wallets = len(private_keys)
    log_info(f"Total wallets to process: {total_wallets}")
    processed_count = 0

    for index, private_key in enumerate(private_keys, start=1):
        success = process_wallet(private_key, index, total_wallets, referral_code)
        if success:
            processed_count += 1
        log_info(f"Processed wallets so far: {processed_count}/{total_wallets}")
        if index < total_wallets:
            log_info("Waiting 20 seconds before processing the next wallet...")
            time.sleep(10)
    log_success(f"All processing completed. Total wallets processed: {processed_count}/{total_wallets}")

if __name__ == "__main__":
    main()
