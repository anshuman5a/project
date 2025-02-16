import os
from datetime import datetime
from pathlib import Path
import aiofiles
from ...utils.file_ops import FileOps

class RecentLogsExecutor:
    def __init__(self):
        self.file_ops = FileOps()

    async def execute(self, parameters: dict) -> bool:
        try:
            # Get all .log files from /data/logs directory
            log_dir = "data/logs"
            log_files = []
            
            # Get all .log files with their modification times
            for file in Path(log_dir).glob("*.log"):
                mtime = os.path.getmtime(file)
                log_files.append((file, mtime))
            
            # Sort by modification time (most recent first) and take top 10
            log_files.sort(key=lambda x: x[1], reverse=True)
            recent_logs = log_files[:10]
            
            # Read first line from each file
            result = []
            for file_path, _ in recent_logs:
                async with aiofiles.open(file_path, 'r') as f:
                    first_line = await f.readline()
                    result.append(first_line.strip())
            
            # Write results to output file
            output_path = "data/logs-recent.txt"
            await self.file_ops.write_file(output_path, "\n".join(result))
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to process recent logs: {str(e)}")