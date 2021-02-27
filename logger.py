import logging


logging.basicConfig(level=logging.DEBUG)
logger_expenses = logging.getLogger("expenses")
my_handler = logging.FileHandler("log_table.log")
my_format = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
my_handler.setFormatter(my_format)
logger_expenses.addHandler(my_handler)
logger_expenses.setLevel(logging.DEBUG)
