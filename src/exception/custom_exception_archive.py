import sys
import traceback
import os.path
from logger.custom_logging import CustomLogger
class Document_Portal_Exception(Exception):
    """Custom excution for Document Portal"""
    def __init__(self, error_message, error_detail:sys):
        _,_,exc_tb = error_detail.exc_info()
        self.file_name = exc_tb.tb_frame.f_code.co_filename
        self.lineno = exc_tb.tb_lineno
        self.error_message = str(error_message)
        self.traceback_str = ''.join(traceback.format_exception(*error_detail.exc_info()))

    def __str__(self):
        return f"""
Error in [{self.file_name}] at line [{self.lineno}]
Message: [{self.error_message}]
{self.traceback_str}
"""

if __name__ == "__main__":
    try:
        a = 1/0
        print(a)
    except Exception as e:
        app_exc =  Document_Portal_Exception(e, sys)
        logger.error(app_exc)
        raise app_exc
        