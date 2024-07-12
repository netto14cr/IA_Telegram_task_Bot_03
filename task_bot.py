import os
from dotenv import load_dotenv
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import time
import speech_recognition as sr
from pydub import AudioSegment

class TelegramAudioTaskBot:
    def __init__(self, telegram_token, openai_api_key):
        self.telegram_token = telegram_token
        self.openai_api_key = openai_api_key
        self.application = Application.builder().token(telegram_token).build()
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(MessageHandler(filters.VOICE, self.handle_voice_message))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        self.tasks = []

    async def start(self, update: Update, context):
        await update.message.reply_text(
            "Welcome to the Task Bot!\n"
            "Send me a voice message with a task and I will convert it to text."
        )

    async def handle_voice_message(self, update: Update, context):
        file_id = update.message.voice.file_id
        new_file = await context.bot.get_file(file_id)
        file_path = f"voice_{file_id}.ogg"
        await new_file.download_to_drive(file_path)

        # Convert OGG to WAV
        audio = AudioSegment.from_ogg(file_path)
        wav_path = f"voice_{file_id}.wav"
        audio.export(wav_path, format="wav")

        # Use speech recognition to convert audio to text
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
                self.tasks.append({'task': text, 'status': 'pending'})
                keyboard = [
                    [InlineKeyboardButton("Mark as Completed", callback_data=f'complete_{len(self.tasks)-1}')],
                    [InlineKeyboardButton("Mark as Pending", callback_data=f'pending_{len(self.tasks)-1}')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(f"Task: {text}", reply_markup=reply_markup)
            except sr.UnknownValueError:
                await update.message.reply_text("Sorry, I could not understand the audio.")
            except sr.RequestError as e:
                await update.message.reply_text(f"Could not request results from Google Speech Recognition service; {e}")

        os.remove(file_path)
        os.remove(wav_path)

    async def handle_callback(self, update: Update, context):
        query = update.callback_query
        data = query.data.split('_')
        action, task_id = data[0], int(data[1])
        if action == 'complete':
            self.tasks[task_id]['status'] = 'completed'
            await query.answer("Task marked as completed.")
        elif action == 'pending':
            self.tasks[task_id]['status'] = 'pending'
            await query.answer("Task marked as pending.")
        await query.edit_message_reply_markup(None)

    def run(self):
        self.application.run_polling()

if __name__ == '__main__':
    load_dotenv()  # Load environment variables from .env file
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    bot = TelegramAudioTaskBot(TELEGRAM_TOKEN, OPENAI_API_KEY)
    bot.run()


# https://t.me/AI_voice_task24_bot