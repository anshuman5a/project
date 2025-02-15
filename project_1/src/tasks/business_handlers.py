# src/tasks/business_handlers.py

import os
import httpx
import git
import duckdb
import sqlite3
import requests
from bs4 import BeautifulSoup
from PIL import Image
import markdown2
import csv
import json
import aiofiles

class BusinessTaskHandler:
    async def handle_api_fetch(self, parameters: dict) -> bool:
        """
        Fetch data from an API and save it
        """
        try:
            url = parameters.get('url')
            output_path = parameters.get('output_path', '/data/api_data.json')
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Write response to file
                async with aiofiles.open(output_path, 'w') as f:
                    await f.write(json.dumps(response.json()))
            
            return True
        except Exception as e:
            raise ValueError(f"API fetch failed: {str(e)}")

    async def handle_git_operations(self, parameters: dict) -> bool:
        """
        Clone a git repo and make a commit
        """
        try:
            repo_url = parameters.get('repo_url')
            commit_message = parameters.get('commit_message', 'Automated commit')
            
            # Clone repo
            repo_path = '/data/git_repo'
            os.makedirs(repo_path, exist_ok=True)
            repo = git.Repo.clone_from(repo_url, repo_path)
            
            # Make changes (example: create a file)
            with open(os.path.join(repo_path, 'automated_file.txt'), 'w') as f:
                f.write('Automated changes')
            
            # Commit and push
            repo.git.add('.')
            repo.git.commit('-m', commit_message)
            repo.git.push()
            
            return True
        except Exception as e:
            raise ValueError(f"Git operations failed: {str(e)}")

    async def handle_sql_query(self, parameters: dict) -> bool:
        """
        Run a SQL query on SQLite or DuckDB
        """
        try:
            db_type = parameters.get('db_type', 'sqlite')
            db_path = parameters.get('db_path')
            query = parameters.get('query')
            output_path = parameters.get('output_path', '/data/query_result.json')
            
            if db_type == 'sqlite':
                conn = sqlite3.connect(db_path)
            elif db_type == 'duckdb':
                conn = duckdb.connect(db_path)
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Write results to file
            with open(output_path, 'w') as f:
                json.dump(results, f)
            
            conn.close()
            return True
        except Exception as e:
            raise ValueError(f"SQL query failed: {str(e)}")

    async def handle_web_scraping(self, parameters: dict) -> bool:
        """
        Extract data from a website
        """
        try:
            url = parameters.get('url')
            selector = parameters.get('selector')
            output_path = parameters.get('output_path', '/data/scraped_data.json')
            
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract data based on selector
            elements = soup.select(selector)
            data = [elem.get_text(strip=True) for elem in elements]
            
            # Write to file
            with open(output_path, 'w') as f:
                json.dump(data, f)
            
            return True
        except Exception as e:
            raise ValueError(f"Web scraping failed: {str(e)}")

    async def handle_image_processing(self, parameters: dict) -> bool:
        """
        Compress or resize an image
        """
        try:
            input_path = parameters.get('input_path')
            output_path = parameters.get('output_path')
            action = parameters.get('action', 'resize')
            
            with Image.open(input_path) as img:
                if action == 'resize':
                    width = parameters.get('width')
                    height = parameters.get('height')
                    img = img.resize((width, height))
                elif action == 'compress':
                    quality = parameters.get('quality', 85)
                    img.save(output_path, optimize=True, quality=quality)
                
                img.save(output_path)
            
            return True
        except Exception as e:
            raise ValueError(f"Image processing failed: {str(e)}")

    async def handle_audio_transcription(self, parameters: dict) -> bool:
        """
        Transcribe audio from an MP3 file
        """
        try:
            # This would typically use a speech recognition library
            # For this example, we'll simulate transcription
            input_path = parameters.get('input_path')
            output_path = parameters.get('output_path', '/data/transcription.txt')
            
            # Placeholder transcription
            with open(output_path, 'w') as f:
                f.write("Simulated transcription text")
            
            return True
        except Exception as e:
            raise ValueError(f"Audio transcription failed: {str(e)}")

    async def handle_markdown_conversion(self, parameters: dict) -> bool:
        """
        Convert Markdown to HTML
        """
        try:
            input_path = parameters.get('input_path')
            output_path = parameters.get('output_path', '/data/converted.html')
            
            with open(input_path, 'r') as f:
                markdown_text = f.read()
            
            html = markdown2.markdown(markdown_text)
            
            with open(output_path, 'w') as f:
                f.write(html)
            
            return True
        except Exception as e:
            raise ValueError(f"Markdown conversion failed: {str(e)}")

    async def handle_csv_filter(self, parameters: dict) -> bool:
        """
        Filter CSV and return JSON
        """
        try:
            input_path = parameters.get('input_path')
            output_path = parameters.get('output_path', '/data/filtered_data.json')
            filters = parameters.get('filters', {})
            
            with open(input_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                filtered_data = [
                    row for row in reader 
                    if all(row.get(k) == v for k, v in filters.items())
                ]
            
            with open(output_path, 'w') as f:
                json.dump(filtered_data, f)
            
            return True
        except Exception as e:
            raise ValueError(f"CSV filtering failed: {str(e)}")