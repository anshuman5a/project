import shutil
import subprocess
import os
from ...utils.logger import logger

class FormatMarkdownExecutor:
    async def execute(self, params: dict) -> bool:
        try:
            # Get the current working directory and construct absolute path
            current_dir = os.getcwd()
            input_file = os.path.join(current_dir, 'data', 'format.md')
            
            # Verify file exists
            if not os.path.exists(input_file):
                raise FileNotFoundError(f"Input file not found: {input_file}")
                
            logger.info(f"Found input file at: {input_file}")
            logger.info(f"Current working directory: {current_dir}")

            # Check if npm and npx are accessible
            npm_path = shutil.which('npm')
            npx_path = shutil.which('npx')
            logger.info(f"npm path: {npm_path}")
            logger.info(f"npx path: {npx_path}")

            if not npm_path or not npx_path:
                raise EnvironmentError("npm or npx not found in PATH")

            # Create a package.json if it doesn't exist
            if not os.path.exists('package.json'):
                with open('package.json', 'w') as f:
                    f.write('{"name": "format-markdown","version": "1.0.0"}')
                logger.info('Created package.json file')

            # Install prettier locally
            logger.info("Installing prettier@3.4.2...")
            install_command = [npm_path, 'install', 'prettier@3.4.2', '--save-dev']
            logger.info(f"Running command: {' '.join(install_command)}")
            install_result = subprocess.run(
                install_command,
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"Install output: {install_result.stdout}")
            logger.info(f"Install errors: {install_result.stderr}")
            logger.info("Prettier installation completed")

            # Format the file using prettier
            logger.info(f"Formatting file: {input_file}")
            format_command = [npx_path, 'prettier', '--write', input_file]
            logger.info(f"Running command: {' '.join(format_command)}")
            result = subprocess.run(
                format_command,
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"Prettier output: {result.stdout}")
            logger.info(f"Prettier errors: {result.stderr}")
            logger.info("File formatted successfully")
            return True

        except FileNotFoundError as e:
            logger.error(f"File-related error: {str(e)}")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e.cmd}")
            logger.error(f"Output: {e.output}")
            raise
        except EnvironmentError as e:
            logger.error(f"Environment error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in FormatMarkdownExecutor: {str(e)}")
            raise
