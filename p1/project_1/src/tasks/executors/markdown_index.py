import os
import json
import aiofiles
from pathlib import Path

class MarkdownIndexExecutor:
    async def execute(self, parameters: dict) -> bool:
        try:
            # Get the project root directory
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

            
            # Define paths relative to project root
            docs_dir = os.path.join(project_root, 'data', 'docs')
            output_file = os.path.join(project_root, 'data', 'docs', 'index.json')
            
            # Create directories if they don't exist
            os.makedirs(docs_dir, exist_ok=True)
            
            # Dictionary to store filename -> title mapping
            index = {}
            
            # Find all .md files
            md_files = Path(docs_dir).glob('**/*.md')
            
            for file_path in md_files:
                # Get path relative to docs directory
                relative_path = str(file_path.relative_to(docs_dir))
                
                # Read file content
                async with aiofiles.open(file_path, 'r') as f:
                    content = await f.read()
                
                # Find first H1 header
                for line in content.split('\n'):
                    if line.strip().startswith('# '):
                        title = line.strip('# ').strip()
                        index[relative_path] = title
                        break
            
            # Write index to file
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            async with aiofiles.open(output_file, 'w') as f:
                await f.write(json.dumps(index, indent=2))
            
            print(f"Index file created at: {output_file}")
            return True
            
        except Exception as e:
            raise ValueError(f"Failed to create markdown index: {str(e)}")