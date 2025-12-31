from openai import OpenAI
from utils.config import Config
import logging
import os

logger = logging.getLogger(__name__)

client = OpenAI(api_key=Config.OPENAI_API_KEY)


class VoiceService:
    """Service for processing voice messages using Whisper API"""

    @staticmethod
    def transcribe_voice(voice_file_path: str) -> str:
        """Transcribe voice message to text using Whisper"""
        try:
            with open(voice_file_path, 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ru"  # Russian, but Whisper handles Ukrainian too
                )

            text = transcript.text
            logger.info(f"Voice transcribed: {text[:50]}...")
            return text

        except Exception as e:
            logger.error(f"Error transcribing voice: {e}")
            return ""

    @staticmethod
    def cleanup_voice_file(file_path: str):
        """Delete temporary voice file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Voice file cleaned up: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up voice file: {e}")


voice_service = VoiceService()
