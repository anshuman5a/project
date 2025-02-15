import os
import subprocess
import sys
from typing import Dict, Any
import httpx
import asyncio
from ...utils.logger import logger

class InstallScriptExecutor:
    def __init__(self):
        self.timeout = 300  # 5 minutes timeout
        self.max_retries = 3
        
    async def execute(self, params: Dict[str, Any]) -> bool:
        """
        Execute script installation and running process
        
        Args:
            params: Dictionary containing script_url and email
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If required parameters are missing
            RuntimeError: If script execution fails
        """
        try:
            # Validate parameters
            if not isinstance(params, dict):
                raise ValueError("Parameters must be a dictionary")
                
            script_url = params.get('script_url')
            email = params.get('email', 'anshuman.singh@gramener.com')
            
            if not script_url:
                raise ValueError("script_url parameter is required")
            if not email:
                raise ValueError("email parameter is required")
            
            # Setup directories
            root_dir = os.getcwd()
            data_dir = os.path.join(root_dir, 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            # Install dependencies
            await self._ensure_uv_installed()
            
            # Download and run script with retries
            script_path = await self._download_script(script_url, data_dir)
            
            # Make script executable
            os.chmod(script_path, 0o755)
            
            # Setup paths
            input_dir = os.path.join(root_dir, 'data', 'docs')
            output_file = os.path.join(root_dir, 'data', 'docs', 'index.json')
            params['input_dir'] = input_dir
            params['output_file'] = output_file
            
            # Run script
            success = await self._run_script(script_path, email, data_dir)
            
            return success

        except Exception as e:
            logger.error(f"Error in InstallScriptExecutor: {str(e)}")
            raise

    async def _ensure_uv_installed(self) -> None:
        """Ensure uv package manager is installed"""
        try:
            subprocess.run(['uv', '--version'], check=True, capture_output=True)
            logger.info("uv is already installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.info("Installing uv...")
            for attempt in range(self.max_retries):
                try:
                    subprocess.run([
                        sys.executable, 
                        '-m', 
                        'pip', 
                        'install', 
                        'uv'
                    ], check=True)
                    break
                except subprocess.CalledProcessError as e:
                    if attempt == self.max_retries - 1:
                        raise RuntimeError(f"Failed to install uv after {self.max_retries} attempts")
                    logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                    await asyncio.sleep(1)

    async def _download_script(self, script_url: str, data_dir: str) -> str:
        """Download script with retries"""
        script_path = os.path.join(data_dir, 'datagen.py')
        
        async with httpx.AsyncClient() as client:
            for attempt in range(self.max_retries):
                try:
                    response = await client.get(script_url, timeout=30.0)
                    response.raise_for_status()
                    
                    with open(script_path, 'wb') as f:
                        f.write(response.content)
                        
                    logger.info(f"Successfully downloaded script to {script_path}")
                    return script_path
                    
                except (httpx.RequestError, httpx.HTTPStatusError) as e:
                    if attempt == self.max_retries - 1:
                        raise RuntimeError(f"Failed to download script after {self.max_retries} attempts: {str(e)}")
                    logger.warning(f"Download attempt {attempt + 1} failed, retrying...")
                    await asyncio.sleep(1)

    async def _run_script(self, script_path: str, email: str, data_dir: str) -> bool:
        """Run the script with proper error handling"""
        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                script_path,
                email,
                '--root',
                data_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                raise RuntimeError(f"Script execution timed out after {self.timeout} seconds")
            
            if process.returncode != 0:
                logger.error(f"Script failed with return code {process.returncode}")
                logger.error(f"stdout: {stdout.decode()}")
                logger.error(f"stderr: {stderr.decode()}")
                raise RuntimeError(f"Script execution failed with code {process.returncode}")
            
            logger.info(f"Script output: {stdout.decode()}")
            return True
            
        except Exception as e:
            logger.error(f"Error running script: {str(e)}")
            raise RuntimeError(f"Script execution failed: {str(e)}")
