import os
import json
import zipfile
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Папка для збереження файлів
UPLOAD_DIR = "uploads"

# Створюємо папку, якщо її не існує
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Надішли мені ZIP-архів, і я розархівую його та знайду інформацію з user_data_tiktok.json.")


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document

    if not file.file_name.endswith('.zip'):
        await update.message.reply_text("Будь ласка, надішли ZIP-архів.")
        return

    # Зберігаємо файл локально
    file_path = os.path.join(UPLOAD_DIR, file.file_name)
    tg_file = await file.get_file()  # Очікуємо результат асинхронно
    await tg_file.download_to_drive(file_path)  # Завантажуємо файл за допомогою нового методу

    try:
        # Розархівовуємо файл
        with zipfile.ZipFile(file_path, 'r') as archive:
            archive.extractall(UPLOAD_DIR)

        # Шукаємо user_data_tiktok.json
        json_path = os.path.join(UPLOAD_DIR, 'user_data_tiktok.json')
        if not os.path.exists(json_path):
            await update.message.reply_text("Файл user_data_tiktok.json не знайдено в архіві.")
            return

        # Читаємо та аналізуємо JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Дістаємо потрібну інформацію (наприклад, поле 'username')
        username = data.get('username', 'Інформація відсутня')
        await update.message.reply_text(f"Знайдено інформацію: \\nUsername: {username}")

    except zipfile.BadZipFile:
        await update.message.reply_text("Помилка: Неможливо розархівувати файл. Перевірте, чи це ZIP-архів.")
    except Exception as e:
        await update.message.reply_text(f"Виникла помилка: {e}")
    finally:
        # Видаляємо архів після обробки
        if os.path.exists(file_path):
            os.remove(file_path)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Невідома команда. Використовуй /start для початку.")


if __name__ == "__main__":
    application = ApplicationBuilder().token("7801818597:AAE8UFrT6p6DbCdWKXQ7KsOOzuRRg87-9UY").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    print("Бот запущено")
    application.run_polling()

