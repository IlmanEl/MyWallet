from openai import OpenAI
from utils.config import Config
import base64
import json
import logging

logger = logging.getLogger(__name__)

client = OpenAI(api_key=Config.OPENAI_API_KEY)


class VisionService:
    """Service for processing receipt images using GPT-4 Vision"""

    @staticmethod
    def process_receipt(image_path: str, available_categories: list) -> dict:
        """Extract information from receipt image"""
        try:
            # Encode image to base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            categories_str = ", ".join(available_categories)

            prompt = f"""Проанализируй чек и извлеки следующую информацию:

1. Общая сумма покупки
2. Дата покупки (если видна)
3. Название магазина/заведения (если видно)
4. Список основных купленных товаров/услуг
5. Наиболее подходящая категория расхода

Доступные категории: {categories_str}

Верни ответ строго в формате JSON:
{{
  "amount": <число>,
  "date": "<дата в формате DD.MM.YYYY или null>",
  "store": "<название магазина или null>",
  "items": ["товар1", "товар2", ...],
  "category": "<категория из списка>"
}}"""

            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )

            content = response.choices[0].message.content

            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
                logger.info(f"Receipt processed: {result}")
                return result
            else:
                logger.error("No JSON found in vision response")
                return {}

        except Exception as e:
            logger.error(f"Error processing receipt: {e}")
            return {}


vision_service = VisionService()
