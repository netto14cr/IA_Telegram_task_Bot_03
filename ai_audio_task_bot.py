import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import speech_recognition as sr
from pydub import AudioSegment
from message_manager import MessageManager  # Asegúrate de importar la clase MessageManager correctamente

class TelegramAudioTaskBot:
    def __init__(self, telegram_token, openai_api_key):
        self.telegram_token = telegram_token
        self.openai_api_key = openai_api_key
        self.message_manager = MessageManager()
        self.application = Application.builder().token(telegram_token).build()
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(MessageHandler(filters.VOICE, self.handle_voice_message))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        self.tasks = []

    async def start(self, update: Update, context):
        keyboard = [
            [InlineKeyboardButton(self.message_manager.get_text("new_task"), callback_data='start_tasks')],
            [InlineKeyboardButton(self.message_manager.get_text("change_language"), callback_data='change_language')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            self.message_manager.get_text("welcome"),
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
                text = recognizer.recognize_google(audio_data, language=self.message_manager.language_code)
                self.tasks.append({'task': text, 'status': 'neutral'})
                task_id = len(self.tasks) - 1
                await self.send_task_message(update, task_id)
            except sr.UnknownValueError:
                await update.message.reply_text(self.message_manager.get_text("audio_not_understood"))
            except sr.RequestError as e:
                await update.message.reply_text(self.message_manager.get_text("recognition_error").format(e))

        os.remove(file_path)
        os.remove(wav_path)

    async def send_task_message(self, update: Update, task_id: int):
        task = self.tasks[task_id]
        status_emoji = "📝" if task['status'] == 'neutral' else ("❌" if task['status'] == 'pending' else "✔️")
        keyboard = [
            [InlineKeyboardButton(self.message_manager.get_text("mark_completed"), callback_data=f'complete_{task_id}')],
            [InlineKeyboardButton(self.message_manager.get_text("mark_pending"), callback_data=f'pending_{task_id}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            self.message_manager.get_text("task_message").format(task['task'], status_emoji),
            reply_markup=reply_markup
        )

    async def handle_callback(self, update: Update, context):
        query = update.callback_query
        data = query.data

        if data == 'start_tasks':
            await query.message.reply_text(self.message_manager.get_text("send_voice_message"))
            await query.answer()
            return

        if data == 'change_language':
            keyboard = [
                [InlineKeyboardButton("English", callback_data='set_language_en')],
                [InlineKeyboardButton("Español", callback_data='set_language_es')],
                [InlineKeyboardButton("Deutsch", callback_data='set_language_de')],
                [InlineKeyboardButton("日本語", callback_data='set_language_ja')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(self.message_manager.get_text("select_language"), reply_markup=reply_markup)
            await query.answer()
            return

        if data.startswith('set_language'):
            if data == 'set_language_en':
                self.message_manager.set_language("en-US", "en")
                await query.message.reply_text("Language set to English.")
            elif data == 'set_language_es':
                self.message_manager.set_language("es-ES", "es")
                await query.message.reply_text("Idioma establecido a Español.")
            elif data == 'set_language_de':
                self.message_manager.set_language("de-DE", "de")
                await query.message.reply_text("Sprache auf Deutsch eingestellt.")
            elif data == 'set_language_ja':
                self.message_manager.set_language("ja-JP", "ja")
                await query.message.reply_text("言語が日本語に設定されました。")
            await query.answer()
            return

        if data.startswith('complete_'):
            task_id = int(data.split('_')[1])
            if 0 <= task_id < len(self.tasks):
                self.tasks[task_id]['status'] = 'completed'
                await query.message.edit_text(
                    self.message_manager.get_text("task_message").format(self.tasks[task_id]['task'], "✔️"),
                    reply_markup=query.message.reply_markup
                )
                await query.message.reply_text(self.message_manager.get_text("task_completed"))
            else:
                await query.message.reply_text(self.message_manager.get_text("task_not_found"))
            await query.answer()
            return

        if data.startswith('pending_'):
            task_id = int(data.split('_')[1])
            if 0 <= task_id < len(self.tasks):
                self.tasks[task_id]['status'] = 'pending'
                await query.message.edit_text(
                    self.message_manager.get_text("task_message").format(self.tasks[task_id]['task'], "❌"),
                    reply_markup=query.message.reply_markup
                )
                await query.message.reply_text(self.message_manager.get_text("task_pending"))
            else:
                await query.message.reply_text(self.message_manager.get_text("task_not_found"))
            await query.answer()
            return

        await query.message.reply_text(self.message_manager.get_text("invalid_callback"))
        await query.answer()

    def run(self):
        self.application.run_polling()

if __name__ == '__main__':
    load_dotenv()
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    openai_api_key = os.getenv('OPENAI_API_KEY')

    bot = TelegramAudioTaskBot(telegram_token, openai_api_key)
    bot.run()