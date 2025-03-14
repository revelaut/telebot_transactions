import json
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time

API_KEY = 'FKSNQAZV26BXS6U7322ABEHQ3USE8R9MM3'


def parse_holders_page(contract_address):
    url = f"https://etherscan.io/token/tokenholderchart/{contract_address}/?range=50"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        holders_table = soup.find("table", {"class": "table"})
        holders = []

        for row in holders_table.find_all("tr")[1:]:
            cols = row.find_all("td")
            address = re.sub(r'\s+', '', cols[1].text.strip())

            if re.match(r'^0x[a-fA-F0-9]{40}$', address):
                balance = cols[2].text.strip().replace(",", "")
                try:
                    balance = float(balance)
                    holders.append({"address": address, "balance": balance})
                except ValueError:
                    print(f"Невірний формат балансу для адреси {address}: {cols[2].text.strip()}")
            else:
                print(f"Невірний формат адреси: {address}")

        return holders
    else:
        print('Error fetch data!')
        return []


def get_transactions(address, api_key, contract_address):
    url = "https://api.etherscan.io/api"
    params = {
        "module": "account",
        "action": "tokentx",
        "address": address,
        "contractaddress": contract_address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc",
        "apikey": api_key
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        print(json.dumps(data, indent=4))

        if data['status'] == "1":
            if data['result']:
                return data['result']
            else:
                print("Немає транзакцій для цієї адреси.")
                return []
        else:
            print(f"Помилка від API: {data['message']}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Помилка HTTP: {e}")
        return []
    except ValueError as e:
        print(f"Помилка при обробці JSON: {e}")
        return []


def convert_timestamp(timeStamp):
    return datetime.fromtimestamp(int(timeStamp))


def calculate_balance_changes(transactions, address, days):
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    balance_changes = 0.0

    for tx in transactions:
        tx_time = convert_timestamp(tx['timeStamp'])
        if start_time <= tx_time <= end_time:
            value = int(tx['value']) / 10 ** 18
            if tx["to"].lower() == address.lower():
                balance_changes += value
            elif tx["from"].lower() == address.lower():
                balance_changes -= value

    return balance_changes


def track_holders_changes(contract_address, api_key, days=None):
    if days is None:
        days = [1, 7, 30]
    holders = parse_holders_page(contract_address)
    result = []

    for holder in holders:
        address = holder['address']
        transactions = get_transactions(address, api_key, contract_address)

        if transactions:
            balance_changes = {f"{d}d": calculate_balance_changes(transactions, address, d) for d in days}
            result.append({"address": address, "balance_changes": balance_changes})
            print(f"Адреса: {address}")
            for d, change in balance_changes.items():
                print(f"Зміна за {d}d: {change}")
            print("-" * 50)
        else:
            print(f"Адреса {address}: немає транзакцій.")

        time.sleep(1)  # Зменшено затримку до 1 секунди

    return result


# Виклик функції
contract_address = "0xB0fFa8000886e57F86dd5264b9582b2Ad87b2b91"
holders_balance_changes = track_holders_changes(contract_address, API_KEY)