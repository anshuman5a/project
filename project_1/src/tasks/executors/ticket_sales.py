import sqlite3
from pathlib import Path
from ...utils.file_ops import FileOps

class TicketSalesExecutor:
    def __init__(self):
        self.file_ops = FileOps()

    async def execute(self, parameters: dict) -> bool:
        try:
            # Define the project root directory
            project_root = Path(__file__).parent.parent.parent.parent

            # Define paths relative to the project root
            db_path = project_root / 'data/ticket-sales.db'
            output_path = project_root / 'data/ticket-sales-gold.txt'

            # Connect to SQLite database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Execute query to sum sales for Gold ticket type
            cursor.execute("""
                SELECT SUM(units * price) 
                FROM tickets 
                WHERE type = 'Gold'
            """)
            
            # Fetch the total sales
            total_sales = cursor.fetchone()[0] or 0

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write result to file
            await self.file_ops.write_file(output_path, str(total_sales))

            conn.close()
            return True
        
        except Exception as e:
            print(f"Error in ticket sales executor: {e}")
            return False
