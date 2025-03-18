import json
import requests
from bs4 import BeautifulSoup
import re

API_KEY = 'C5694QYVPN1AG47W9XMEUW7FQD5GD9N73R'

def parse_holders_page(contract_address):
    url = f"https://etherscan.io/token/tokenholderchart/{contract_address}/?range=100"
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'referer': 'https://etherscan.io/token/generic-tokenholders2?m=light&a=0x514910771af9ca656af840dff83e8264ecf986ca&s=1000000000000000000000000000&sid=6d98e7148d144f6813996e95925a5fec&p=1',
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-bitness': '"64"',
        'sec-ch-ua-full-version': '"134.0.6998.89"',
        'sec-ch-ua-full-version-list': '"Chromium";v="134.0.6998.89", "Not:A-Brand";v="24.0.0.0", "Google Chrome";v="134.0.6998.89"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"macOS"',
        'sec-ch-ua-platform-version': '"12.7.6"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'Cookie': 'etherscan_switch_token_amount_value=value; ASP.NET_SessionId=0xgor5z4uufyy2233bkvnnbt; etherscan_offset_datetime=+2; __stripe_mid=87452759-ba55-44c2-9c30-0daa7686ae2481c5d9; etherscan_cookieconsent=True; etherscan_userid=lattebudlaska; etherscan_autologin=True; _ga_T1JC9RNQXV=deleted; etherscan_pwd=4792:Qdxb:U5zNwBOkQtLV9WHSBDSIKaEyoBcy+gRn44kYYEF/fao=; __cflb=0H28vPcoRrcznZcNZSuFrvaNdHwh858K6dRCL7NsNJQ; _gid=GA1.2.727001669.1742211053; __stripe_sid=b5c370ab-5d87-4388-aacc-f1b9e052af6dcdbb06; _gat_gtag_UA_46998878_6=1; cf_clearance=3MyjXmyz3sQNm.x_x0mZ_3z4JxxAYuwcA_XUbCwqv5s-1742285791-1.2.1.1-EMqtzkI3I1TZ2c8xoNdnsOjn4La5NZf7Kcn07BaAEgaZoFI6rHQ93yGSpGOjD3.DttEgqLJBwPKgsD8nqs1AxIpiGDNiQ3qt40TRKXg4HDgIDYd1nEOzAX59nWcPvrL9.rMfX68zHeCdw0vLzD7NNpaPLOhLF1wOyG_Rcsvwhy6E8lP_86462SnybgaW_0nNZMPkHN.rQOEu9ubqay4w5urawaOXpEn0yGo9QcbRZr8XmlKKCUXOgaU3fsmE4mbVmUQ0PRiz2pIjETjycHc59vkC0M_13XA9FF9M1aaTkyOPnNnXZrP32aiEUmrk9V9udYLwv9F.R_mnWtIDqy_EjOTpa7bgU950kyNB2PbbVlGGWGXlfnX6rQcy5A.SocQ2K9Ti_3bwKOrOEGqzclylYXK5.LY93jAsu0Qwi9mJpLA; _ga_T1JC9RNQXV=GS1.1.1742284926.38.1.1742285803.47.0.0; _ga=GA1.2.1184989000.1724148862'
    }
    response = requests.get(url, headers=headers)
    print(f"Статус відповіді: {response.status_code}")

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


#w = parse_holders_page("0xB8c77482e45F1F44dE1745F52C74426C631bDD52")
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