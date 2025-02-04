import telebot
from telebot import types
import address_transactions_parse
import os
import json

API_KEY = 'FKSNQAZV26BXS6U7322ABEHQ3USE8R9MM3'
TOKEN = '7332833376:AAGC4NTZ5_SmsuGR8NxUOttebQZgCBuEyuA'

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = types.KeyboardButton('-> Введіть адресу вашого токену ERC-20')
    markup.add(button_1)

    bot.send_message(message.chat.id, "Радий вас бачити. Оберіть тип чейну та слідуйте інструкції нижче:",
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '-> Введіть адресу вашого токену ERC-20')
def ask_for_input(message):
    bot.send_message(message.chat.id, "Будь ласка, введіть адресу контракту:")
    bot.register_next_step_handler(message, get_text)  # Очікуємо наступне повідомлення


def get_text(message):
    user_text = message.text
    bot.send_message(message.chat.id, f'Ви ввели наступну адресу токена: {user_text}.\nТрішки зачекайте...')

    try:
        # Викликаємо функцію з модуля address_transactions_parse
        result = address_transactions_parse.track_holders_changes(user_text, API_KEY, [1, 7, 30])

        print(result)  # Дивимося, що приходить у змінну

        if isinstance(result, dict):
            holders = result.get("holders", [])
            contract_address = result.get("contract_address", "N/A")
            total_changes = result.get("total_changes", {})

            if isinstance(holders, list):
                file = f'{user_text}.txt'
                with open(file, "w", encoding="utf-8") as f:
                    # Записуємо дані в файл
                    for holder in holders:
                        f.write(f"Адреса: {holder['address']}\n")
                        f.write(f"Зміна за 1 день: {holder['balance_changes'].get('1d', 'N/A')}\n")
                        f.write(f"Зміна за 7 днів: {holder['balance_changes'].get('7d', 'N/A')}\n")
                        f.write(f"Зміна за 30 днів: {holder['balance_changes'].get('30d', 'N/A')}\n")
                        f.write("-" * 50 + "\n")

                    # Додаємо загальну інформацію
                    f.write(f"\nАдреса контракту: {contract_address}\n")
                    f.write(f"Загальна зміна балансу за 7 днів: {total_changes.get('7d', 'N/A')}\n")
                    f.write(f"Загальна зміна балансу за 30 днів: {total_changes.get('30d', 'N/A')}\n")

                with open(file, "rb") as f:
                    bot.send_document(message.chat.id, f)

                os.remove(file)

    except Exception as e:
        bot.reply_to(message, f"Помилка: {str(e)}")

bot.infinity_polling()
