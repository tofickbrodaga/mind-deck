import os
from uuid import UUID
from gtts import gTTS
from infrastructure.config import settings


class TTSService:
    """Сервис для генерации аудио с помощью Text-to-Speech"""
    
    # Список поддерживаемых языков (gTTS поддерживает 50+ языков)
    SUPPORTED_LANGUAGES = {
        'ru': 'Russian',
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ko': 'Korean',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'tr': 'Turkish',
        'pl': 'Polish',
        'nl': 'Dutch',
        'sv': 'Swedish',
        'no': 'Norwegian',
        'da': 'Danish',
        'fi': 'Finnish',
        'cs': 'Czech',
        'el': 'Greek',
        'he': 'Hebrew',
        'th': 'Thai',
        'vi': 'Vietnamese',
        'id': 'Indonesian',
        'uk': 'Ukrainian',
        'ro': 'Romanian',
        'bg': 'Bulgarian',
        'hr': 'Croatian',
        'sk': 'Slovak',
        'sl': 'Slovenian',
        'et': 'Estonian',
        'lv': 'Latvian',
        'lt': 'Lithuanian',
        'hu': 'Hungarian',
        'ca': 'Catalan',
        'sr': 'Serbian',
        'mk': 'Macedonian',
        'sq': 'Albanian',
        'mt': 'Maltese',
        'is': 'Icelandic',
        'ga': 'Irish',
        'cy': 'Welsh',
        'eu': 'Basque',
        'gl': 'Galician',
        'af': 'Afrikaans',
        'sw': 'Swahili',
        'zu': 'Zulu',
        'xh': 'Xhosa',
        'am': 'Amharic',
        'bn': 'Bengali',
        'gu': 'Gujarati',
        'kn': 'Kannada',
        'ml': 'Malayalam',
        'mr': 'Marathi',
        'ne': 'Nepali',
        'pa': 'Punjabi',
        'si': 'Sinhala',
        'ta': 'Tamil',
        'te': 'Telugu',
        'ur': 'Urdu',
    }
    
    async def generate_audio(self, text: str, language: str, card_id: UUID) -> str:
        """
        Сгенерировать аудио из текста
        
        Args:
            text: Текст для озвучки
            language: Код языка (например, 'ru', 'en')
            card_id: ID карточки для сохранения файла
        
        Returns:
            URL или путь к аудио файлу
        """
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Language {language} is not supported")
        
        # Создаем директорию для аудио, если её нет
        audio_dir = os.path.join(settings.upload_dir, "audio")
        os.makedirs(audio_dir, exist_ok=True)
        
        # Генерируем аудио
        tts = gTTS(text=text, lang=language, slow=False)
        
        # Сохраняем файл
        audio_filename = f"{card_id}_{language}.mp3"
        audio_path = os.path.join(audio_dir, audio_filename)
        tts.save(audio_path)
        
        # Возвращаем относительный путь (в реальном приложении можно использовать S3 или CDN)
        return f"/api/v1/media/audio/{audio_filename}"
    
    def get_supported_languages(self) -> List[dict]:
        """Получить список поддерживаемых языков"""
        return [
            {"code": code, "name": name}
            for code, name in self.SUPPORTED_LANGUAGES.items()
        ]
