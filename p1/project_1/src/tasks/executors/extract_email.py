import os
from ...llm.client import LLMClient
from ...utils.file_ops import FileOps

class EmailExtractorExecutor:
    def __init__(self):
        self.llm_client = LLMClient()
        self.file_ops = FileOps()

    async def execute(self, parameters: dict) -> bool:
        try:
            # Read the email content from /data/email.txt
            email_content = await self.file_ops.read_file('/data/email.txt')

            # Prompt for email extraction
            prompt = f"""
            Extract the sender's email address from the following email content.
            Return ONLY the email address. If no email is found, return an empty string.
            
            Email Content:
            {email_content}
            """

            # Use LLM to extract email
            extracted_email = await self.llm_client.generate(prompt)

            # Clean and validate email
            extracted_email = extracted_email.strip()

            # Write to output file in project root/data folder
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
            output_file_path = os.path.join(project_root, 'data', 'email-sender.txt')
            await self.file_ops.write_file(output_file_path, extracted_email)

            return True
        except Exception as e:
            print(f"Error in email extraction: {e}")
            return False
