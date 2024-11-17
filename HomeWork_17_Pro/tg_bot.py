from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
from telegram import InlineKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
import os

# подгружаем переменные окружения
load_dotenv()

# токен бота
TOKEN = os.getenv('TG_TOKEN')

# Словари для языков
messages = {
    'en': {
        'start': "Please choose your language:",
        'choice': "You have chosen English",
        'text_received': "We've received a message from you!",
        'voice_received': "We've received a voice message from you!",
        'photo_saved': "Photo saved!",
    },
    'ru': {
        'start': "Пожалуйста, выберите язык:",
        'choice': "Вы выбрали русский язык",
        'text_received': "Текстовое сообщение получено!",
        'voice_received': "Голосовое сообщение получено!",
        'photo_saved': "Фотография сохранена!",
    }
}

# Словарь для хранения выбранного языка
user_languages = {}

# INLINE
# форма inline клавиатуры
inline_frame = [[InlineKeyboardButton("Русский", callback_data="ru")],
                [InlineKeyboardButton("English", callback_data="en")],
                ]
# создаем inline клавиатуру
inline_keyboard = InlineKeyboardMarkup(inline_frame)

# функция-обработчик команды /start
async def start(update: Update, _):
    # прикрепляем inline клавиатуру к сообщению
    await update.message.reply_text(messages['ru']['start'], reply_markup=inline_keyboard)

# функция-обработчик нажатий на кнопки
async def button(update: Update, _):
    # получаем callback query из update
    query = update.callback_query
    user_id = query.from_user.id
    # сохраняем выбранный язык
    user_languages[user_id] = query.data
    # редактируем сообщение после нажатия
    await query.edit_message_text(text=messages[query.data]['choice'])

# функция-обработчик текстовых сообщений
async def text(update, context):
    user_id = update.message.from_user.id
    language = user_languages.get(user_id, 'ru')
    # сообщение о получении сообщения
    await update.message.reply_text(messages[language]['text_received'])

# функция-обработчик голосовых сообщений
async def voice(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    language = user_languages.get(user_id)
    # Отправляем изображение с использованием контекстного менеджера
    with open('photos/voice_image.png', 'rb') as photo_file:
        await context.bot.send_photo(update.message.chat.id, photo=photo_file,
                                      caption=messages[language]['voice_received'])

# функция-обработчик сообщений с изображениями
async def image(update: Update, _):
    user_id = update.message.from_user.id
    language = user_languages.get(user_id)
    # получаем изображение из апдейта
    file = await update.message.photo[-1].get_file()
    # сохраняем изображение на диск
    await file.download_to_drive(f'photos/{update.message.photo[-1].file_id}.png')
    # сообщение о сохранении
    await update.message.reply_text(messages[language]['photo_saved'])

def main():

    # создаем приложение и передаем в него токен
    application = Application.builder().token(TOKEN).build()
    print('Бот запущен...')

    # добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # добавляем CallbackQueryHandler (только для inline кнопок)
    application.add_handler(CallbackQueryHandler(button))

    # добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT, text))

    # добавляем обработчик голосовых сообщений
    application.add_handler(MessageHandler(filters.VOICE, voice))

    # добавляем обработчик сообщений с фотографиями
    application.add_handler(MessageHandler(filters.PHOTO, image))

    # запускаем бота (нажать Ctrl-C для остановки бота)
    application.run_polling()
    print('Бот остановлен')


if __name__ == "__main__":
    main()