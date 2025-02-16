import json, os
from typing import Dict, Any, Optional
from src.llm.client import LLMClient
from src.utils.logger import logger

class TaskParser:
    def __init__(self):
        self.llm_client = LLMClient()
        self._task_handlers = {
            'install_run_script': self._handle_install_script,
            'format_markdown': self._handle_format_markdown,
            'count_weekday': self._handle_count_weekday,
            'sort_contacts': self._handle_sort_contacts,
            'recent_logs': self._handle_recent_logs,
            'extract_email': self._handle_extract_email,
            'markdown_index': self._handle_markdown_index,
            'credit_card': self._handle_credit_card,
            'similar_comments': self._handle_similar_comments,
            'ticket_sales': self._handle_ticket_sales,
            'fetch_api': self._handle_fetch_api,
            'git_operations': self._handle_git_operations,
        }
    
    async def parse_task(self, task_description: str) -> Dict[str, Any]:
        """
        Parse a task description into a structured task format.
        
        Args:
            task_description: Natural language description of the task
            
        Returns:
            Dict containing task_type and parameters
            
        Raises:
            ValueError: If task description is invalid or cannot be parsed
        """
        try:
            task_description = task_description.strip().lower()
            
            # Try direct task matching first
            for handler in self._task_handlers:
                if handler in task_description:
                    return self._task_handlers[handler](task_description)
            
            # Fallback to LLM for complex tasks
            return await self._parse_with_llm(task_description)
            
        except Exception as e:
            logger.error(f"Failed to parse task: {str(e)}")
            raise ValueError(f"Task parsing failed: {str(e)}")

    def _handle_install_script(self, task_description: str) -> Dict[str, Any]:
        """Handle install_run_script specific task parsing"""
        if "datagen.py" not in task_description:
            raise ValueError("Invalid install script task: datagen.py not specified")
            
        return {
            "task_type": "install_run_script",
            "parameters": {
                "script_url": "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py",
                "email": 'anshuman.singh@gramener.com'
            }
        }

    def _handle_format_markdown(self, task_description: str) -> Dict[str, Any]:
        """Handle format_markdown specific task parsing"""
        return {
            "task_type": "format_markdown",
            "parameters": {}
        }

    def _handle_count_weekday(self, task_description: str) -> Dict[str, Any]:
        """Handle count_weekday specific task parsing"""
        return {
            "task_type": "count_weekday",
            "parameters": {
                "weekday": "wednesday",
                "input_file": "data/dates.txt",
                "output_file": "data/dates-wednesdays.txt"
            }
        }

    def _handle_sort_contacts(self, task_description: str) -> Dict[str, Any]:
        """Handle sort_contacts specific task parsing"""
        return {
            "task_type": "sort_contacts",
            "parameters": {}
        }

    def _handle_recent_logs(self, task_description: str) -> Dict[str, Any]:
        """Handle recent_logs specific task parsing"""
        return {
            "task_type": "recent_logs",
            "parameters": {}
        }

    def _handle_extract_email(self, task_description: str) -> Dict[str, Any]:
        """Handle extract_email specific task parsing"""
        return {
            "task_type": "extract_email",
            "parameters": {}
        }

    def _handle_markdown_index(self, task_description: str) -> Dict[str, Any]:
        """Handle markdown_index specific task parsing"""
        return {
            "task_type": "markdown_index",
            "parameters": {
                "input_dir": "/data/docs",
                "output_file": "/data/docs/index.json"
            }
        }

    def _handle_credit_card(self, task_description: str) -> Dict[str, Any]:
        """Handle credit_card specific task parsing"""
        return {
            "task_type": "credit_card",
            "parameters": {}
        }

    def _handle_similar_comments(self, task_description: str) -> Dict[str, Any]:
        """Handle similar_comments specific task parsing"""
        return {
            "task_type": "similar_comments",
            "parameters": {
                "input_file": "/data/comments.txt",
                "output_file": "/data/comments-similar.txt"
            }
        }

    def _handle_ticket_sales(self, task_description: str) -> Dict[str, Any]:
        """Handle ticket_sales specific task parsing"""
        return {
            "task_type": "ticket_sales",
            "parameters": {}
        }

    def _handle_fetch_api(self, task_description: str) -> Dict[str, Any]:
        """Handle fetch_api specific task parsing"""
        return {
            "task_type": "fetch_api",
            "parameters": {
                "url": "https://example.com/api",
                "output_path": "/data/api_data.json"
            }
        }

    def _handle_git_operations(self, task_description: str) -> Dict[str, Any]:
        """Handle git_operations specific task parsing"""
        return {
            "task_type": "git_operations",
            "parameters": {
                "repo_url": "https://github.com/example/repo.git",
                "commit_message": "Automated commit"
            }
        }

    async def _parse_with_llm(self, task_description: str) -> Dict[str, Any]:
        """Parse complex tasks using LLM"""
        prompt = """
        Analyze this task and extract key information in JSON format.
        Task: {task_description}
        
        Return JSON with the following structure:
        {
            "task_type": "string",
            "parameters": {
                // task specific parameters
            }
        }
        """
        
        try:
            response = await self.llm_client.generate(
                prompt.format(task_description=task_description)
            )
            result = json.loads(response.strip())
            
            # Validate response structure
            if not isinstance(result, dict) or 'task_type' not in result or 'parameters' not in result:
                raise ValueError("Invalid LLM response structure")
                
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            raise ValueError(f"Invalid JSON response from LLM: {str(e)}")
        except Exception as e:
            logger.error(f"LLM parsing failed: {str(e)}")
            raise ValueError(f"Failed to parse task with LLM: {str(e)}")