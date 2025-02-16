import json
import aiofiles
from ...utils.file_ops import FileOps

class SortContactsExecutor:
    def __init__(self):
        self.file_ops = FileOps()

    async def execute(self, parameters: dict) -> bool:
        try:
            # Read the contacts file
            input_path = "data/contacts.json"
            output_path = "data/contacts-sorted.json"
            
            # Read the JSON file
            async with aiofiles.open(input_path, 'r') as f:
                content = await f.read()
                contacts = json.loads(content)
            
            # Sort contacts by last_name, then first_name
            sorted_contacts = sorted(
                contacts,
                key=lambda x: (x['last_name'], x['first_name'])
            )
            
            # Write sorted contacts to output file
            async with aiofiles.open(output_path, 'w') as f:
                await f.write(json.dumps(sorted_contacts, indent=2))
            
            return True
            
        except Exception as e:
            raise Exception(f"Error sorting contacts: {str(e)}")