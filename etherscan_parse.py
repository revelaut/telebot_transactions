import json
import requests
from bs4 import BeautifulSoup
import re

API_KEY = 'FKSNQAZV26BXS6U7322ABEHQ3USE8R9MM3'

def parse_holders_page(contract_address):
    url = f"https://etherscan.io/token/tokenholderchart/{contract_address}/?range=10"
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

            # Витягуємо посилання
            link = cols[1].find('a', href=True)
            if not link:
                continue

            href = link['href']
            match = re.search(r'\?a=(0x[a-fA-F0-9]{40})', href)  # Виділяємо адресу з параметра ?a=
            if not match:
                print(f"Invalid address format: {href}")
                continue

            address = match.group(1)

            # Парсинг балансу
            balance_text = cols[2].text.strip().replace(",", "")
            try:
                balance = float(balance_text)
                holders.append({"address": address, "balance": balance})
            except ValueError:
                print(f"Invalid balance format: {balance_text}")


        return holders


    else:
        print('Error fetch data!')
        return []


#w = parse_holders_page("0xB0fFa8000886e57F86dd5264b9582b2Ad87b2b91")
#print(w)

# Перший варіант більш точний, через витягування повної адреси з тегу <a> - посилання


#for row in holders_table.find_all("tr")[1:]:
            #cols = row.find_all("td")
            #address = re.sub(r'\s+', '', cols[1].text.strip())

            #if address.startswith("0x"):
                #balance = cols[2].text.strip().replace(",", "")  # Видаляємо коми
                #try:
                    #balance = float(balance)  # Перетворюємо на число
                    #holders.append({"address": address, "balance": balance})
                #except ValueError:
                    #print(f"Невірний формат балансу для адреси {address}: {cols[2].text.strip()}")
            #else:
                #print(f"Невірний формат адреси: {address}")
            #balance = cols[2].text.strip()
            #holders.append({"address": address, "balance": balance})

        #unique_count = set(holder["address"] for holder in holders)
        #unique_address = len(unique_count)
        #print(unique_address)


        #with open("holders.txt", "w", newline="") as f:
            #for holder in holders:
                #formatted_text = "\n".join([f'{key}: {value}' for key, value in holder.items()])
                #f.write(formatted_text + "\n\n")