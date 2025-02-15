# src/tasks/executors/count_weekdays.py

from datetime import datetime
import os
from ...utils.logger import logger
from ...utils.file_ops import FileOps

class CountWeekdaysExecutor:
    async def execute(self, params: dict) -> bool:
        try:
            file_ops = FileOps()
            input_file = 'data/dates.txt'
            output_file = 'data/dates-wednesdays.txt'
            
            # Read the input file
            content = await file_ops.read_file(input_file)
            dates = content.strip().split('\n')
            
            wednesday_count = 0
            
            for date_str in dates:
                try:
                    # Handle different date formats
                    date_formats = [
                        '%d-%b-%Y',
                        '%Y/%m/%d %H:%M:%S',
                        '%Y-%m-%d',
                        '%b %d, %Y'
                    ]
                    
                    parsed_date = None
                    for fmt in date_formats:
                        try:
                            # Strip any time component if present
                            date_part = date_str.split()[0]
                            parsed_date = datetime.strptime(date_str, fmt)
                            break
                        except ValueError:
                            continue
                    
                    if parsed_date and parsed_date.weekday() == 2:  # Wednesday is 2
                        wednesday_count += 1
                        
                except Exception as e:
                    logger.warning(f"Could not parse date: {date_str}, Error: {str(e)}")
                    continue
            
            # Write result to output file
            await file_ops.write_file(output_file, str(wednesday_count))
            return True
            
        except Exception as e:
            logger.error(f"Error in CountWeekdaysExecutor: {str(e)}")
            raise