from groq import Groq
from langdetect import detect
from config import GROQ_API_KEY, PREFERRED_LANGUAGE


class TranslatorAgent:
    """Multilingual Translator Agent - Handles language detection and translation."""

    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"
        self.preferred_language = PREFERRED_LANGUAGE
        self.language_names = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ar": "Arabic",
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "hi": "Hindi",
            "ru": "Russian",
        }

    def detect_language(self, text: str) -> str:
        """Detect the language of incoming text."""
        try:
            return detect(text)
        except:
            return "unknown"

    def translate(self, message: str, target_language: str = None) -> dict:
        """Translate message to target language."""
        if target_language is None:
            target_language = self.preferred_language

        source_lang = self.detect_language(message)

        if source_lang == target_language:
            return {
                "original": message,
                "translated": message,
                "source_language": source_lang,
                "target_language": target_language,
                "was_translated": False,
            }

        target_name = self.language_names.get(target_language, target_language)

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"""Translate the following message to {target_name}.
Keep the tone natural and conversational. Only output the translation, nothing else.

Message: {message}""",
                }
            ],
        )

        translated = response.choices[0].message.content

        return {
            "original": message,
            "translated": translated,
            "source_language": source_lang,
            "target_language": target_language,
            "was_translated": True,
        }

    def adjust_tone(self, message: str, tone: str = "professional") -> str:
        """Adjust message tone: friendly, professional, or persuasive."""
        tone_instructions = {
            "friendly": "Make it warm, casual, and approachable. Use a conversational style.",
            "professional": "Make it formal, polite, and business-appropriate.",
            "persuasive": "Make it compelling and sales-oriented while remaining respectful.",
        }

        instruction = tone_instructions.get(tone, tone_instructions["professional"])

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"""Rewrite the following message with this tone adjustment: {instruction}

Keep the same meaning and language. Only output the rewritten message.

Message: {message}""",
                }
            ],
        )

        return response.choices[0].message.content

    def translate_for_client(self, message: str, client_language: str) -> str:
        """Translate your response back to the client's language."""
        result = self.translate(message, target_language=client_language)
        return result["translated"]
