import os
import json
from dotenv import load_dotenv
from google import genai
from PIL import Image

from ai.prompt import SYSTEM_PROMPT

# Load environment variables
load_dotenv()


class GeminiClient:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise Exception("GEMINI_API_KEY not found in .env file.")

        self.client = genai.Client(api_key=api_key)
        self.model = "models/gemini-3.5-flash-lite"

    def extract_answers(self, image_path):
        """
        Extract MCQ answers from an image using Gemini.

        Returns:
            dict
            Example:
            {
                "1": "A",
                "2": "C",
                "3": "B"
            }
        """

        # Check image exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        try:
            image = Image.open(image_path)

            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    SYSTEM_PROMPT,
                    image
                ]
            )

            text = response.text.strip()

            # Remove markdown if Gemini returns it
            text = (
                text.replace("```json", "")
                .replace("```", "")
                .strip()
            )

            answers = json.loads(text)

            if not isinstance(answers, dict):
                raise Exception("Gemini did not return a valid JSON object.")

            return answers

        except json.JSONDecodeError:
            raise Exception(
                "Gemini returned invalid JSON.\n\nResponse:\n" + text
            )

        except Exception as e:
            raise Exception(f"Gemini Error: {e}")