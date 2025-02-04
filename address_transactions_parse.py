import requests
from datetime import datetime, timedelta
from etherscan_parse import parse_holders_page
import time
import json
import re


def get_transactions(address, api_key, contract_address):

    url = "https://api.etherscan.io/api"

    params = {
        "module": "account",
        "action": "tokentx",  # Тип запиту: отримання транзакцій токена
        "contractaddress": contract_address,
        "address": address,  # Адреса гаманця
        "page": 1,
        "offset": 100,
        "startblock": 0,  # Початковий блок (0 - з початку історії)
        "endblock": 27025780,  # Кінцевий блок (до останнього блоку)
        "sort": "desc",  # Сортування: "asc" (за зростанням), "desc" (за спаданням)
        "apikey": api_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        #print(json.dumps(data, indent=4))


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
            value = int(tx['value']) / 10**18

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
    total_changes_7d = 0.0
    total_changes_30d = 0.0

    for holder in holders:
        address = holder['address']
        balance = holder['balance']
        transactions = get_transactions(address, api_key, contract_address)

        if transactions:
            balance_changes = {f"{d}d": calculate_balance_changes(transactions, address, d) for d in days}
            result.append({"address": address, "balance_changes": balance_changes})
            print(f"Адреса: {address}")
            print(f"Баланс: {balance}")
            for d, change in balance_changes.items():
                print(f"Зміна за {d}d: {change}")
            print("-" * 50)

            total_changes_7d += balance_changes.get("7d", 0)
            total_changes_30d += balance_changes.get("30d", 0)

        else:
            print(f"Адреса {address}: немає транзакцій.")


        time.sleep(1)

    print(f'Адреса контракту: {contract_address}')
    print(f'Загальна зміна балансу на усіх гаманцях за 7 днів: {total_changes_7d}')
    print(f'Загальна зміна балансу на усіх гаманцях за 30 днів: {total_changes_30d}')

    return {
        "contract_address": contract_address,
        "total_changes": {
            "7d": total_changes_7d,
            "30d": total_changes_30d
        },
        "holders": result
    }

API_KEY = "FKSNQAZV26BXS6U7322ABEHQ3USE8R9MM3"
wallet_address = "0x4D5fA1839aed8Dce51c5Fe3bC23f4FC08E02702e"
contract_address = "0xADE00C28244d5CE17D72E40330B1c318cD12B7c3"

holders_balance_changes = track_holders_changes(contract_address, API_KEY)



#Тут вказуються апі, адреса гаманця і адреса контракту токена

#API_KEY = "FKSNQAZV26BXS6U7322ABEHQ3USE8R9MM3"
#wallet_address = "0x4D5fA1839aed8Dce51c5Fe3bC23f4FC08E02702e"
#contract_address = "0xB0fFa8000886e57F86dd5264b9582b2Ad87b2b91"

#Створюємо обʼєкт функції, та передаємо дані, розміщені в змінних

#new_transactions = get_transactions(wallet_address, API_KEY, contract_address)

#Якщо список з транзакціями є - перебираємо їх та виводимо потрібні нам дані (конвертуємо велью та дату)

#    for tx in new_transactions[:5]:
#        print(f"From: {tx['from']}")
 #       print(f"To: {tx['to']}")
 #       print(f"Value: {int(tx['value']) / 10**18}")
 #       print(f"Timestamp: {convert_timestamp(tx['timeStamp'])}")
 #       print("-" * 40)
#else:
  #  print("Transactions not defined!")

#balance_change_1d = calculate_balance_changes(new_transactions, wallet_address, 1)
#balance_change_7d = calculate_balance_changes(new_transactions, wallet_address, 7)
#balance_change_30d = calculate_balance_changes(new_transactions, wallet_address, 30)

#print(f"Зміна балансу за 1 день: {balance_change_1d}")
#print(f"Зміна балансу за 7 днів: {balance_change_7d}")
#print(f"Зміна балансу за 30 днів: {balance_change_30d}")



