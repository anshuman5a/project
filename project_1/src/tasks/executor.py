from venv import logger
from ..utils.file_ops import FileOps
from ..utils.security import SecurityCheck
from .business_handlers import BusinessTaskHandler
from .executors.count_weekdays import CountWeekdaysExecutor
from .executors.credit_card import CreditCardExecutor
from .executors.extract_email import EmailExtractorExecutor
from .executors.format_markdown import FormatMarkdownExecutor
from .executors.install_script import InstallScriptExecutor
from .executors.markdown_index import MarkdownIndexExecutor
from .executors.recent_logs import RecentLogsExecutor
from .executors.similar_comments import SimilarCommentsExecutor
from .executors.sort_contacts import SortContactsExecutor
from .executors.ticket_sales import TicketSalesExecutor

class TaskExecutor:
    def __init__(self):
        self.file_ops = FileOps()  
        self.security = SecurityCheck()
        self.handlers = {
            'install_run_script': InstallScriptExecutor(),
            'format_markdown': FormatMarkdownExecutor(),
            'count_weekday': CountWeekdaysExecutor(),
            'sort_contacts': SortContactsExecutor(),
            'recent_logs': RecentLogsExecutor(),
            'markdown_index': MarkdownIndexExecutor(),
            'extract_email': EmailExtractorExecutor(),
            'credit_card': CreditCardExecutor(),
            'similar_comments': SimilarCommentsExecutor(),
            'ticket_sales': TicketSalesExecutor(),
            'fetch_api': BusinessTaskHandler().handle_api_fetch,
            'git_operations': BusinessTaskHandler().handle_git_operations,
            'sql_query': BusinessTaskHandler().handle_sql_query,
            'web_scraping': BusinessTaskHandler().handle_web_scraping,
            'image_processing': BusinessTaskHandler().handle_image_processing,
            'audio_transcription': BusinessTaskHandler().handle_audio_transcription,
            'markdown_conversion': BusinessTaskHandler().handle_markdown_conversion,
            'csv_filter': BusinessTaskHandler().handle_csv_filter
        }

    async def execute_task(self, task_info: dict) -> bool:
        try:
            # Validate task type
            task_type = task_info.get('task_type')
            if not task_type:
                raise ValueError("Task type not specified")

            # Get appropriate handler
            handler = self.handlers.get(task_type)
            if not handler:
                raise ValueError(f"Unknown task type: {task_type}")

            # Execute task
            return await handler.execute(task_info.get('parameters', {}))

        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")
            raise