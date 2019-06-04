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
