from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import os

# подгружаем переменные окружения
load_dotenv()

# токен бота
TOKEN = os.getenv('TG_TOKEN')


# функция-обработчик команды /start
async def start(update, context):
    await update.message.reply_text('Добро пожаловать, мой дорогой друг!')

# функция-обработчик команды /help
async def help(update, context):
    red_exclamation_mark = '\U00002757'
    await update.message.reply_text(f'Этот бот предназначен для обучения{red_exclamation_mark}')

# функция-обработчик текстовых сообщений
async def text(update, context):
    await update.message.reply_text('Текст, текст, текст…')


def main():

    # создаем приложение и передаем в него токен
    application = Application.builder().token(TOKEN).build()
    print('Бот запущен...')

    # добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # добавляем обработчик команды /help
    application.add_handler(CommandHandler("help", help))

    # добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT, text))

    # запускаем бота (нажать Ctrl-C для остановки бота)
    application.run_polling()
    print('Бот остановлен')


if __name__ == "__main__":
    main()
