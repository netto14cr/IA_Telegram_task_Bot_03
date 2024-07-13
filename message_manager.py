class MessageManager:
  def __init__(self):
      self.language_code = "en-US"  # Default language for recognition
      self.language = "en"  # Default language for bot messages

  def get_text(self, key):
      texts = {
          "en": {
              "welcome": "Welcome to the Task Bot!\nI can help you remember and complete tasks.\nClick the button below to begin.",
              "new_task": "New Task",
              "change_language": "Change Language",
              "send_voice_message": "Send me a voice message with a task and I will convert it to text.",
              "audio_not_understood": "Sorry, I could not understand the audio.",
              "recognition_error": "Could not request results from Google Speech Recognition service; {}",
              "task_message": "Task: {} {}",
              "mark_completed": "Mark as Completed",
              "mark_pending": "Mark as Pending",
              "select_language": "Select the language for voice recognition:",
              "invalid_callback": "Invalid callback data.",
              "task_not_found": "Task not found.",
              "task_completed": "Task marked as completed.",
              "task_pending": "Task marked as pending."
          },
          "es": {
              "welcome": "¡Bienvenido al Bot de Tareas!\nPuedo ayudarte a recordar y completar tareas.\nHaz clic en el botón de abajo para comenzar.",
              "new_task": "Nueva Tarea",
              "change_language": "Cambiar Idioma",
              "send_voice_message": "Envíame un mensaje de voz con una tarea y la convertiré en texto.",
              "audio_not_understood": "Lo siento, no pude entender el audio.",
              "recognition_error": "No se pudieron solicitar los resultados del servicio de reconocimiento de voz de Google; {}",
              "task_message": "Tarea: {} {}",
              "mark_completed": "Marcar como Completada",
              "mark_pending": "Marcar como Pendiente",
              "select_language": "Selecciona el idioma para el reconocimiento de voz:",
              "invalid_callback": "Datos de callback inválidos.",
              "task_not_found": "Tarea no encontrada.",
              "task_completed": "Tarea marcada como completada.",
              "task_pending": "Tarea marcada como pendiente."
          },
          "de": {
              "welcome": "Willkommen beim Task Bot!\nIch kann Ihnen helfen, Aufgaben zu merken und zu erledigen.\nKlicken Sie auf die Schaltfläche unten, um zu beginnen.",
              "new_task": "Neue Aufgabe",
              "change_language": "Sprache ändern",
              "send_voice_message": "Senden Sie mir eine Sprachnachricht mit einer Aufgabe und ich werde sie in Text umwandeln.",
              "audio_not_understood": "Entschuldigung, ich konnte das Audio nicht verstehen.",
              "recognition_error": "Anforderung von Ergebnissen beim Google-Spracherkennungsdienst konnte nicht durchgeführt werden; {}",
              "task_message": "Aufgabe: {} {}",
              "mark_completed": "Als erledigt markieren",
              "mark_pending": "Als ausstehend markieren",
              "select_language": "Wählen Sie die Sprache für die Spracherkennung:",
              "invalid_callback": "Ungültige Callback-Daten.",
              "task_not_found": "Aufgabe nicht gefunden.",
              "task_completed": "Aufgabe als erledigt markiert.",
              "task_pending": "Aufgabe als ausstehend markiert."
          },
          "ja": {
              "welcome": "タスクボットへようこそ！\nタスクを記憶して完了するのを手伝います。\n以下のボタンをクリックして始めてください。",
              "new_task": "新しいタスク",
              "change_language": "言語を変更する",
              "send_voice_message": "タスクの音声メッセージを送信してください。テキストに変換します。",
              "audio_not_understood": "申し訳ありませんが、音声が理解できませんでした。",
              "recognition_error": "Google音声認識サービスから結果をリクエストできませんでした; {}",
              "task_message": "タスク: {} {}",
              "mark_completed": "完了としてマーク",
              "mark_pending": "保留中としてマーク",
              "select_language": "音声認識の言語を選択してください：",
              "invalid_callback": "無効なコールバックデータ。",
              "task_not_found": "タスクが見つかりません。",
              "task_completed": "タスクを完了としてマークしました。",
              "task_pending": "タスクを保留中としてマークしました。"
          }
      }
      return texts[self.language].get(key, key)

  def set_language(self, language_code, language):
      self.language_code = language_code
      self.language = language