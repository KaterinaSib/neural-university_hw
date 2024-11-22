from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update
from dotenv import load_dotenv
import os
import openai
import requests
import aiohttp
import asyncio
import json

# подгружаем переменные окружения
load_dotenv()

# передаем секретные данные в переменные
TOKEN = os.getenv('TG_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# передаем секретный токен chatgpt
openai.api_key = OPENAI_API_KEY


# функция для асинхронного общения с сhatgpt
async def get_answer_async(text):
    payload = {"text":text}
    async with aiohttp.ClientSession() as session:
        async with session.post('http://127.0.0.1:5000/api/get_answer_async', json=payload) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                # Если произошла ошибка, возвращаем информацию об ошибке
                return {'detail': 'Ошибка API', 'status_code': resp.status}
            

# функция-обработчик команды /start
async def start(update, context):
    # при первом запуске бота добавляем этого пользователя в словарь
    if update.message.from_user.id not in context.bot_data.keys():
        context.bot_data[update.message.from_user.id] = 3
    
    # возвращаем текстовое сообщение пользователю
    await update.message.reply_text('Добро пожаловать, мой дорогой друг!')


# функция-обработчик команды /help
async def help(update):
    red_exclamation_mark = '\U00002757'
    await update.message.reply_text(f'Этот бот предназначен для обучения{red_exclamation_mark}')


# функция-обработчик команды /data 
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # создаем json и сохраняем в него словарь context.bot_data
    with open('status.json', 'w') as fp:
        json.dump(context.bot_data, fp)

    # возвращаем текстовое сообщение пользователю
    await update.message.reply_text(f'Осталось запросов: {context.bot_data[update.message.from_user.id]}')


# функция-обработчик текстовых сообщений
async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # проверка доступных запросов пользователя
    if context.bot_data[update.message.from_user.id] > 0:

        # выполнение запроса в chatgpt
        first_message = await update.message.reply_text('Ваш запрос обрабатывается, пожалуйста подождите...')
        res = await get_answer_async(update.message.text)
        await context.bot.edit_message_text(text=res['message'], chat_id=update.message.chat_id, message_id=first_message.message_id)

        # уменьшаем количество доступных запросов на 1
        context.bot_data[update.message.from_user.id]-=1
    
    else:
        # сообщение если запросы исчерпаны
        await update.message.reply_text('Ваши запросы на сегодня исчерпаны')


# функция, которая будет запускаться раз в сутки для обновления доступных запросов
async def callback_daily(context: ContextTypes.DEFAULT_TYPE):

    # проверка базы пользователей
    if context.bot_data != {}:
        # проходим по всем пользователям в базе и обновляем их доступные запросы
        for key in context.bot_data:
            context.bot_data[key] = 5
        print('Запросы пользователей обновлены')
    else:
        print('Не найдено ни одного пользователя')


def main():

    # создаем приложение и передаем в него токен
    application = Application.builder().token(TOKEN).build()
    print('Бот запущен...')

    # создаем job_queue 
    job_queue = application.job_queue
    job_queue.run_repeating(callback_daily, # функция обновления базы запросов пользователей
                            interval=60,    # интервал запуска функции (в секундах)
                            first=10)  

    
    # добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start, block=True))

    # добавляем обработчик команды /help
    application.add_handler(CommandHandler("help", help, block=True))

    # добавляем обработчик команды /status
    application.add_handler(CommandHandler("status", status, block=True))

    # добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT, text, block=False))

    # запускаем бота (нажать Ctrl-C для остановки бота)
    application.run_polling()
    print('Бот остановлен')


if __name__ == '__main__':
    main()
