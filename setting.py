sqlalchemy_mysql = "mysql+pymysql://spider:pelerin@192.168.10.211:3306/d_spider?charset=utf8mb4"

redis_config = {
    'host': '192.168.10.212',
    'db': 15,
    'decode_responses': True,  # 这个参数的作用是，返回的字符串，默认是字节
    'port': 6379
}

headers = {
    "Content-Type": "text/html; charset=utf-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
    "Referer": "https://www.tianyancha.com/"
}

change_person = ['投资人变更（包括出资额、出资方式、出资日期、投资人名称等）','投资人','高级管理人员备案（董事、监事、经理等）','负责人变更（法定代表人、负责人、首席代表、合伙事务执行人等变更）','董事长或执行董事成员','总经理','指定联系人','法定代表人（负责人）','股东（投资人）','董事成员','高管人员','监事信息','其他董事信息','董事（理事）、经理、监事']
change_address = ['地址变更','住所']
change_name = ['企业名称','名称变更（字号名称、集团名称等）','名称']