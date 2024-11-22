from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update
from dotenv import load_dotenv
import os
import openai
import aiohttp
import json

# подгружаем переменные окружения
load_dotenv()

# передаем секретные данные в переменные
TOKEN = os.getenv('TG_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# передаем секретный токен chatgpt
openai.api_key = OPENAI_API_KEY


# функция для асинхронного общения с сhatgpt
async def get_answer_async(text, history):
    payload = {"text":text,
               "history": history,
               }
    async with aiohttp.ClientSession() as session:
        async with session.post('http://127.0.0.1:5000/api/get_answer_async', json=payload) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                # Если произошла ошибка, возвращаем информацию об ошибке
                return {'detail': 'Ошибка API', 'status_code': resp.status}
            

# функция-обработчик команды /start
async def start(update, context):
    user_id = update.message.from_user.id
    # при первом запуске бота добавляем этого пользователя в словарь
    if user_id not in context.bot_data.keys():
        context.bot_data[user_id] = {"requests": 3, "history": []}
    
    # возвращаем текстовое сообщение пользователю
    await update.message.reply_text('Добро пожаловать, мой дорогой друг!')


# функция-обработчик команды /help
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    red_exclamation_mark = '\U00002757'
    await update.message.reply_text(f'Этот бот предназначен для обучения{red_exclamation_mark}')


# функция-обработчик команды /data 
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data = context.bot_data[user_id]

    # создаем json и сохраняем в него словарь context.bot_data
    with open('status.json', 'w') as fp:
        json.dump(context.bot_data, fp)

    # возвращаем текстовое сообщение пользователю
    await update.message.reply_text(f'Осталось запросов: {user_data["requests"]}')


# функция-обработчик текстовых сообщений
async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id
    user_data = context.bot_data[user_id]

    # Инициализация истории, если она еще не существует
    if "history" not in user_data:
        user_data["history"] = []

    # проверка доступных запросов пользователя
    if user_data ['requests']> 0:

        # выполнение запроса в chatgpt
        first_message = await update.message.reply_text('Ваш запрос обрабатывается, пожалуйста подождите...')

        # Сохраняем текущее сообщение в историю
        user_data["history"].append(update.message.text)
        
        # Ограничиваем историю до 5 последних сообщений
        if len(user_data["history"]) > 5:
            user_data["history"].pop(0)

        # Печатаем текущую историю для отладки
        print('history', user_data["history"])

        # Объединяем историю с текущим запросом
        history_context = "\n".join(user_data["history"])

        # res = await get_answer_async(update.message.text, user_data["history"])

        # Выполняем запрос в chatgpt с передачей истории
        res = await get_answer_async(history_context, user_data["history"])

        await context.bot.edit_message_text(text=res['message'], chat_id=update.message.chat_id, message_id=first_message.message_id)

        # уменьшаем количество доступных запросов на 1
        user_data["requests"] -= 1
    
    else:
        # сообщение если запросы исчерпаны
        await update.message.reply_text('Ваши запросы на сегодня исчерпаны')


# функция, которая будет запускаться раз в сутки для обновления доступных запросов
async def callback_daily(context: ContextTypes.DEFAULT_TYPE):

    # проверка базы пользователей
    if context.bot_data != {}:
        # проходим по всем пользователям в базе и обновляем их доступные запросы
        for key in context.bot_data:
            context.bot_data[key]["requests"] = 5
        print('Запросы пользователей обновлены')
    else:
        print('Не найдено ни одного пользователя')


def main():

    application = Application.builder().token(TOKEN).build()
    print('Бот запущен...')

    job_queue = application.job_queue
    job_queue.run_repeating(callback_daily, interval=60, first=10)  

    application.add_handler(CommandHandler("start", start, block=True))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("status", status, block=True))
    application.add_handler(MessageHandler(filters.TEXT, text, block=False))

    application.run_polling()
    print('Бот остановлен')


if __name__ == '__main__':
    main()