import base64
import os
from pathlib import Path
from src.llm.client import LLMClient
from src.utils.file_ops import FileOps

class CreditCardExecutor:
    def __init__(self):
        self.llm_client = LLMClient()
        self.file_ops = FileOps()

    async def execute(self, parameters: dict) -> bool:
        # Ensure correct paths
        project_root = Path(__file__).parent.parent.parent.parent 
        image_path = project_root / "data/credit_card.png"
        output_path = project_root / "data/credit-card.txt"

        # Validate image file exists
        if not image_path.exists():
            print(f"Error: Image file not found at {image_path}")
            return False

        try:
            # Read the image and convert to base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            # Prompt for credit card number extraction
            prompt = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": "Extract the credit card number from this image. Return ONLY the number without any spaces or formatting. If no credit card number is visible, return 'NO_NUMBER_FOUND'."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]

            # Use LLM to extract credit card number
            response = await self.llm_client.generate_vision(prompt)
            
            # Remove any spaces or formatting, keep only digits
            card_number = ''.join(filter(str.isdigit, response))

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the extracted number to file
            await self.file_ops.write_file(output_path, card_number)

            return True
        except Exception as e:
            print(f"Error extracting credit card number: {e}")
            return False
