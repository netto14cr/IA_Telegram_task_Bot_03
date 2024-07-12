import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
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
        keyboard = [
            [InlineKeyboardButton("New Task", callback_data='start_tasks')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Welcome to the Task Bot!\n"
            "I can help you remember and complete tasks.\n"
            "Click the button below to begin.",
            reply_markup=reply_markup
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
                self.tasks.append({'task': text, 'status': 'neutral'})
                task_id = len(self.tasks) - 1
                await self.send_task_message(update, task_id)
            except sr.UnknownValueError:
                await update.message.reply_text("Sorry, I could not understand the audio.")
            except sr.RequestError as e:
                await update.message.reply_text(f"Could not request results from Google Speech Recognition service; {e}")

        os.remove(file_path)
        os.remove(wav_path)

    async def send_task_message(self, update: Update, task_id: int):
        task = self.tasks[task_id]
        status_emoji = "📝" if task['status'] == 'neutral' else ("❌" if task['status'] == 'pending' else "✔️")
        keyboard = [
            [InlineKeyboardButton("Mark as Completed", callback_data=f'complete_{task_id}')],
            [InlineKeyboardButton("Mark as Pending", callback_data=f'pending_{task_id}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"Task: {task['task']} {status_emoji}", reply_markup=reply_markup)

    async def handle_callback(self, update: Update, context):
        query = update.callback_query
        data = query.data

        if data == 'start_tasks':
            await query.message.reply_text("Send me a voice message with a task and I will convert it to text.")
            await query.answer()
            return

        try:
            action, task_id_str = data.split('_')
            task_id = int(task_id_str)
        except ValueError:
            await query.answer("Invalid callback data.")
            return
        
        if task_id >= len(self.tasks):
            await query.answer("Task not found.")
            return

        task = self.tasks[task_id]

        if action == 'complete':
            task['status'] = 'completed'
            await query.answer("Task marked as completed.")
        elif action == 'pending':
            task['status'] = 'pending'
            await query.answer("Task marked as pending.")

        await self.edit_task_message(query, task_id)

    async def edit_task_message(self, query, task_id: int):
        task = self.tasks[task_id]
        status_emoji = "📝" if task['status'] == 'neutral' else ("❌" if task['status'] == 'pending' else "✔️")
        keyboard = [
            [InlineKeyboardButton("Mark as Completed", callback_data=f'complete_{task_id}')],
            [InlineKeyboardButton("Mark as Pending", callback_data=f'pending_{task_id}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"Task: {task['task']} {status_emoji}", reply_markup=reply_markup)

    def run(self):
        self.application.run_polling()

if __name__ == '__main__':
    load_dotenv()  # Load environment variables from .env file
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    bot = TelegramAudioTaskBot(TELEGRAM_TOKEN, OPENAI_API_KEY)
    bot.run()
