import os
import sys
import json
import time
import random
import requests
from threading import Thread
from termcolor import colored
from colorama import init

init(autoreset=True)

custom_art = """
██████╗  ██████╗ ██████╗ ███████╗ █████╗ ███╗   ███╗ ██████╗ ███╗   ██╗
██╔══██╗██╔═══██╗██╔══██╗██╔════╝██╔══██╗████╗ ████║██╔═══██╗████╗  ██║
██║  ██║██║   ██║██████╔╝█████╗  ███████║██╔████╔██║██║   ██║██╔██╗ ██║
██║  ██║██║   ██║██╔══██╗██╔══╝  ██╔══██║██║╚██╔╝██║██║   ██║██║╚██╗██║
██████╔╝╚██████╔╝██║  ██║███████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██║ ╚████║
╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
"""
made_by_text = "              MADE BY :- Đôrêmon"

agents = {
    "1": {"id": "deployment_p5J9lz1Zxe7CYEoo0TZpRVay", "name": "Professor 🧠"},
    "2": {"id": "deployment_7sZJSiCqCNDy9bBHTEh7dwd9", "name": "Crypto Buddy 💰"},
    "3": {"id": "deployment_SoFftlsf9z4fyA3QCHYkaANq", "name": "Sherlock 🔎"}
}

def display_app_title():
    """Display the ASCII title and app information."""
    print(colored(custom_art, 'cyan'))
    print(colored('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'white'))
    print(colored(made_by_text, 'yellow'))
    print(colored('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'white'))
    print(colored('🔗 Telegram: https://t.me/DoraBots', 'yellow'))
    print(colored('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n', 'white'))

def get_wallets():
    if not os.path.exists('wallet.txt'):
        print(colored('⚠️ wallet.txt not found! Add wallets inside the file.', 'red'))
        sys.exit(1)
    with open('wallet.txt', 'r') as f:
        wallets = [line.strip() for line in f if line.strip()]
    return wallets

def get_random_questions():
    default_questions = [
        "What is AI?", 
        "Explain blockchain.", 
        "How does machine learning work?"
    ]
    if not os.path.exists('random_questions.json'):
        print(colored('⚠️ random_questions.json not found! Using default questions.', 'red'))
        return default_questions
    try:
        with open('random_questions.json', 'r') as f:
            questions = json.load(f)
        return questions if questions else default_questions
    except Exception as e:
        print(colored(f'⚠️ Error reading questions file: {e}', 'red'))
        return default_questions

def send_random_question(agent_id):
    questions = get_random_questions()
    random_question = random.choice(questions)
    payload = {"message": random_question, "stream": False}
    transformed = agent_id.lower().replace('_', '-')
    url = f"https://{transformed}.stag-vxzy.zettablock.com/main"

    attempts = 3
    while attempts > 0:
        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                data = response.json()
                if ("choices" in data and len(data["choices"]) > 0 and 
                    "message" in data["choices"][0]):
                    return {"question": random_question, "response": data["choices"][0]["message"]}
        except Exception as e:
            print(colored(f'⚠️ API request failed (Retries left: {attempts - 1}): {e}', 'red'))
        attempts -= 1
        time.sleep(2)
    return None

def report_usage(wallet, options):
    payload = {
        "wallet_address": wallet.lower(),
        "agent_id": options["agent_id"],
        "request_text": options["question"],
        "response_text": options["response"],
        "request_metadata": {}
    }
    try:
        resp = requests.post(
            "https://quests-usage-dev.prod.zettablock.com/api/report_usage",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        if resp.status_code == 200:
            print(colored('✅ Usage data successfully reported!\n', 'green'))
            return True
        else:
            print(colored(f'⚠️ Failed to report usage: {resp.status_code}', 'red'))
            return False
    except Exception as e:
        print(colored(f'⚠️ Failed to report usage: {e}', 'red'))
        return False

def run_sequential(wallet, agent_ids, iterations):
    for agent_choice in agent_ids:
        agent = agents.get(agent_choice)
        if not agent:
            continue
        print(colored(f"\n🤖 Using Agent: {agent['name']} for Wallet: {wallet}", 'magenta'))
        print(colored('----------------------------------------', 'white'))
        success_count = 0
        while success_count < iterations:
            print(colored(f"🔄 Attempt {success_count + 1}", 'yellow'))
            result = send_random_question(agent["id"])
            if not result or "question" not in result:
                print(colored("⚠️ Failed to retrieve a valid question. Retrying...", 'red'))
                continue

            question_text = result["question"]
            response_content = result.get("response")
            if isinstance(response_content, dict):
                response_text = response_content.get("content", "No response received.")
            else:
                response_text = response_content if response_content else "No response received."
            print(colored("❓ Question: ", 'cyan') + colored(question_text, attrs=["bold"]))
            print(colored("💡 Answer: ", 'green') + colored(response_text, attrs=["underline"]))

            reported = report_usage(wallet, {
                "agent_id": agent["id"],
                "question": question_text,
                "response": response_text if response_text else "No response"
            })
            if reported:
                success_count += 1
        print(colored('----------------------------------------', 'white'))

def run_worker(wallet, agent_ids, iterations):
    """
    Start a new thread to handle processing for a single wallet.
    """
    thread = Thread(target=run_sequential, args=(wallet, agent_ids, iterations))
    thread.start()
    return thread

def main():
    display_app_title()
    wallets = get_wallets()

    # Limit the number of wallets to 100
    wallets = wallets[:100]  # Adjust as needed
    agent_choice = input(colored('🤖 Select Agent (1: Professor 🧠, 2: Crypto Buddy 💰, 3: Sherlock 🔎, 4: All): ', 'yellow'))
    input_iterations = input(colored('🔢 Enter the number of iterations per agent: ', 'yellow'))
    multi_thread = input(colored('⚡ Enable Multi-threading? (yes/no): ', 'yellow'))

    try:
        iterations = int(input_iterations)
    except Exception:
        iterations = 1

    agent_ids = []
    if agent_choice == "4":
        agent_ids = list(agents.keys())
    elif agent_choice in agents:
        agent_ids.append(agent_choice)
    else:
        print(colored("⚠️ Invalid selection! Exiting...", 'red'))
        sys.exit(1)

    print(colored(f"\n📊 Iterations per agent: {iterations}", 'blue'))
    mt_enabled = multi_thread.strip().lower() == "yes"
    print(colored(f"⚡ Multi-threading: {'Enabled' if mt_enabled else 'Disabled'}\n", 'blue'))

    if mt_enabled:
        threads = []
        for wallet in wallets:
            t = run_worker(wallet, agent_ids, iterations)
            threads.append(t)
        for t in threads:
            t.join()
    else:
        for wallet in wallets:
            run_sequential(wallet, agent_ids, iterations)

if __name__ == "__main__":
    main()
