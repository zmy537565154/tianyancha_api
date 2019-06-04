import json
from datetime import datetime, date
import requests
from core.db import redis_client
from core.logger import logger
import time
from requests.exceptions import ProxyError, ConnectTimeout, ReadTimeout, ConnectionError
from setting import headers
from core import request
from lxml import etree
import re
import jsonpath
from core.storge import save_invest_partner
from core.module import Session,Partner, Investment, InvestmentPartner
from flask import Response


class JsonFont(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


def make_response(module_object):
    response = Response(json.dumps(module_object, cls=JsonFont), mimetype='application/json')
    return response


def object_to_dict(MoudleObject):
    data = dict()
    data['isSuccess'] = True
    data['msg'] = "查询成功"
    data['company_name'] = MoudleObject.f_company_name
    data['company_code'] = MoudleObject.f_company_code
    data['tel'] = MoudleObject.f_tel
    data['mail'] = MoudleObject.f_mail
    data['contact'] = MoudleObject.f_contact
    # 注册资本
    data['registered_capital'] = MoudleObject.f_registered_capital
    # 注册日期
    data['found_date'] = MoudleObject.f_found_date
    # 统一信用号
    data['credit_code'] = MoudleObject.f_credit_code
    # 公司类型
    data['company_type'] = MoudleObject.f_company_type
    # 工商注册号
    data['register_num'] = MoudleObject.f_register_num
    # 组织机构代码
    data['org_code'] = MoudleObject.f_org_code
    # 地址
    data['address'] = MoudleObject.f_address
    # 经营范围
    data['business_scope'] = MoudleObject.f_business_scope
    # 企业状态
    data['business_status'] = MoudleObject.f_business_status
    # 行业
    data['industry'] = MoudleObject.f_industry
    # 更新时间
    data['update_time'] = MoudleObject.f_update_time
    return data


def partner_object_to_dict(partner):
    data = dict()
    data['amount'] = partner.f_amount
    data['name'] = partner.f_partner_name
    data['percent'] = partner.f_proportion
    data['type'] = partner.f_type
    data['id'] = str(partner.f_partner_code)
    data['start_node'] = str(partner.f_company_code)
    data['level'] = 1
    data['category'] = 1
    return data


def invest_object_to_dict(invest):
    data = dict()
    data['amount'] = invest.f_amount
    data['name'] = invest.f_target_company_name
    data['percent'] = invest.f_proportion
    data['type'] = 2
    data['id'] = str(invest.f_target_company_code)
    data['start_node'] = str(invest.f_company_code)
    data['level'] = 1
    data['category'] = 2
    return data


def get_proxy():
    for item in range(5):
        logger.info("第 {} 次获取代理地址.".format(item + 1))
        if not redis_client.scard("proxyPool:proxyPool"):
            try:
                info = requests.get("http://192.168.10.212:10008/update_pool")
            except ProxyError:
                continue
            except ConnectTimeout:
                continue
            except ReadTimeout:
                continue
            except ConnectionError:
                continue
            if info.json().get('isSuccess') == 'true':
                logger.info('更新代理 {}'.format(info.json().get('msg')[0]))
            else:
                continue
        ip = redis_client.srandmember("proxyPool:proxyPool")
        logger.info("当前代理 {}".format(ip))
        proxies = {
            'http': "http://{}".format(ip),
            'https': "http://{}".format(ip),
        }
        try:
            requests.get("http://www.baidu.com", proxies=proxies, timeout=2)
        except ProxyError:
            redis_client.srem('proxyPool:proxyPool', ip)
            logger.info('{} 代理无效'.format(ip))
        except ReadTimeout:
            redis_client.srem('proxyPool:proxyPool', ip)
            logger.info('{} 连接超时'.format(ip))
        except ConnectTimeout:
            redis_client.srem('proxyPool:proxyPool', ip)
            logger.info('{} 代理超时'.format(ip))
        except ConnectionError:
            redis_client.srem('proxyPool:proxyPool', ip)
            logger.info('{} 代理超时'.format(ip))
        else:
            logger.info("{} 代理有效".format(ip))
            return {'isSuccess': True, 'data': proxies}
    else:
        return {"isSuccess": False, 'msg': "代理获取失败"}


def get_normal_cookies():
    for item in range(5):
        try:
            logger.info('第 {} 次获取 normal cookies...'.format(item + 1))
            response = requests.get("http://192.168.10.212:10000/get_cookie/")
        except ProxyError:
            continue
        except ConnectTimeout:
            continue
        except ReadTimeout:
            continue
        except ConnectionError:
            continue
        else:
            cookies_pool_response = json.loads(response.text)
            if cookies_pool_response.get('code') == 1:
                cookies = {'isSuccess': True, 'data': cookies_pool_response.get('value')}
                break
        time.sleep(5)
    else:
        cookies = {"isSuccess": False, 'msg': "Normal Cookies 获取失败"}
    return cookies


def get_vip_cookies():
    for item in range(5):
        try:
            logger.info('第 {} 次获取 VIP cookies...'.format(item + 1))
            response = requests.get("http://192.168.10.212:10001/get_cookie/")
        except ProxyError:
            continue
        except ConnectTimeout:
            continue
        except ReadTimeout:
            continue
        except ConnectionError:
            continue
        else:
            cookies_pool_response = json.loads(response.text)
            if cookies_pool_response.get('code') == 1:
                cookies = {'isSuccess': True, 'data': cookies_pool_response.get('value')}
                break
        time.sleep(5)
    else:
        cookies = {"isSuccess": False, 'msg': "VIP Cookies 获取失败"}
    return cookies


def get_company_url(company_name):
    logger.info('GET https://m.tianyancha.com/search?key={}'.format(company_name))
    logger.info('正在尝试获取代理...')
    proxy = get_proxy()
    if proxy.get('isSuccess'):
        logger.info('当前代理地址 {}'.format(proxy.get("data").get('http')))
        logger.info('正在使用代理搜索公司.')
        try:
            print(proxy.get('data'))
            response = requests.get('https://m.tianyancha.com/search?key={}'.format(company_name),
                                    proxies=proxy.get("data"),
                                    headers=headers)
        except Exception as e:
            logger.warning(e)
            logger.info('天眼查异常，本次搜索无效.')
            return {'isSuccess': False, 'msg': '第三方服务异常，请稍后重试'}
        logger.info('移动站搜索已完成.')
        if '立即登录' in response.text or '登录/注册即表示同意' in response.text:
            logger.info('移动站需要登录，正在使用PC站搜索.')
            response = request.spider.get_normal_response(
                'https://www.tianyancha.com/search?key={}'.format(company_name))
            if response.get('isSuccess'):
                text_html = response.get('data')
                HTML = etree.HTML(text_html)
                url = HTML.xpath(
                    "/html[1]/body[1]/div[2]/div[1]/div[1]/div[1]/div[3]/div[1]/div[1]/div[3]/div[1]/a[1]/@href")
                url2 = HTML.xpath(
                    "/html[1]/body[1]/div[2]/div[1]/div[1]/div[2]/div[3]/div[1]/div[1]/div[3]/div[1]/a[1]/@href")
                if url:
                    logger.info('当前公司 URL {}'.format(url[0]))
                    return {'isSuccess': True, 'msg': '获取企业URL成功', "URL": url[0]}
                elif url2:
                    logger.info('当前公司 URL {}'.format(url2[0]))
                    return {'isSuccess': True, 'msg': '获取企业URL成功', "URL": url2[0]}
                else:
                    return {'isSuccess': False, 'msg': '未查到企业信息'}
            else:
                return {'isSuccess': False, 'msg': '内部错误，PC站搜索失败'}

        else:
            # print(response.text)
            html = etree.HTML(response.text)
            a_list = html.xpath("//div[@class='col-10 search-name']/a/@href")
            if a_list:
                return {'isSuccess': True, 'msg': '获取企业URL成功', "URL": mobile_url_2_computer_url(a_list[0])}
            else:
                return {'isSuccess': False, 'msg': '内部错误，企业URL获取失败'}
    else:
        return {"isSuccess": False, 'msg': "代理获取失败"}


def mobile_url_2_computer_url(mobile_url):
    company_code = re.search('(?<=/company/)\d*', mobile_url).group()
    url = 'https://www.tianyancha.com/company/{}'.format(company_code)
    logger.info('当前公司 URL {}'.format(url))
    return url


def get_company_code(company_url):
    company_code = re.search('(?<=/company/)[0-9]*', company_url).group()
    return company_code


def get_id():
    return int(datetime.now().timestamp() * 1000)



def get_invert_partner(company_code):
    if company_code == "0":
        data = dict()
        data['holderList'] = []
        data['investorList'] = []
        return {'isSuccess': True, 'msg': "查询成功", 'data': data}

    res = get_invert_partner_from_db(company_code)
    if res.get('isSuccess'):
        return {'isSuccess': True, 'msg': '查询成功', 'data': res.get('data')}

    res = get_invert_partner_from_api(company_code)
    if res.get('isSuccess'):
        return {'isSuccess': True, 'msg': '查询成功', 'data': res.get('data')}


def add_start_node_for_partner(company_code):
    def inner(item):
        item.update({'start_node': str(company_code), 'id': str(item.get('id')), 'level': 1})
        return item

    return inner


def add_start_node_for_invest(company_code):
    def inner(item):
        item.update({'start_node': str(company_code), 'id': str(item.get('id')), 'level': 1, 'type': 2})
        return item

    return inner


def get_invert_partner_from_db(company_code):
    session = Session()
    flag = session.query(InvestmentPartner).filter(InvestmentPartner.f_company_code == company_code).first()
    if flag:
        partner_list_objects = session.query(Partner).filter(Partner.f_company_code == company_code).all()
        invest_list_objects = session.query(Investment).filter(Investment.f_company_code == company_code).all()
        partner_list = []
        invest_list = []
        data = dict()
        for partner in partner_list_objects:
            partner_list.append(partner_object_to_dict(partner))
        data['holderList'] = partner_list
        for invest in invest_list_objects:
            invest_list.append(invest_object_to_dict(invest))
        data['investorList'] = invest_list
        session.close()
        return {'isSuccess': True, 'msg': '查询成功', 'data': data}
    else:
        return {"isSuccess": False, 'msg': '数据库未查到数据'}


def get_invert_partner_from_api(company_code):
    data = dict()
    for item in range(5):
        url = "https://capi.tianyancha.com/cloud-equity-provider/v4/qq/name.json?id={}?random={}".format(
            company_code,
            int(
                time.time() * 1000))
        node = "https://capi.tianyancha.com/cloud-equity-provider/v4/equity/indexnode.json?id={}".format(
            company_code)
        # 使用代理
        proxies = None
        # response_proxy = get_proxy()
        # if response_proxy.get('isSuccess'):
        #     proxies = response_proxy.get('data')

        session = requests.session()

        try:
            response = session.get(url, proxies=proxies, headers=headers)
        except ProxyError:
            continue
        except ConnectTimeout:
            continue
        except ReadTimeout:
            continue
        except ConnectionError:
            continue
        v = list(map(lambda x: int(x), response.json().get('data').get('v').split(',')))
        text = ''
        for _ in v:
            text = text + chr(_)
        token = re.search('(?<=cloud_token=)[0-9a-z]*', text).group()

        # 使用代理
        proxies = None
        # response_proxy = get_proxy()
        # if response_proxy.get('isSuccess'):
        #     proxies = response_proxy.get('data')
        try:
            response = session.get(node, cookies={"cloud_token": token}, headers=headers, proxies=proxies)
        except ProxyError:
            continue
        except ConnectTimeout:
            continue
        except ReadTimeout:
            continue
        except ConnectionError:
            continue
        company_data = response.json().get('data')
        if company_data:
            break
    else:
        return {"isSuccess": False, "msg": "第三方接口调用失败，请重试"}

    if not isinstance(jsonpath.jsonpath(company_data, "$..holderList"), bool):
        data['holderList'] = list(
            map(add_start_node_for_partner(company_code),
                jsonpath.jsonpath(company_data, "$..holderList")[0]))
    else:
        data['holderList'] = []

    if not isinstance(jsonpath.jsonpath(company_data, "$..investorList"), bool):
        data['investorList'] = list(
            map(add_start_node_for_invest(company_code),
                jsonpath.jsonpath(company_data, "$..investorList")[0]))
    else:
        data['investorList'] = []

    data['company_code'] = company_code
    save_invest_partner(data)
    return {'isSuccess': True, 'msg': '查询成功', 'data': data}
