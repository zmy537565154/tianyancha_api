import logging
import sys

# 日志管理
logger = logging.getLogger('AppName')
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

file_handler = logging.FileHandler('spider.log', encoding='utf8')
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter

logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)
