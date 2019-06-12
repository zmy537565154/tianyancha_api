from core.module import Session, CompanyStore
from core.request import spider
from core.utils import get_company_url, object_to_dict, get_company_code, get_invert_partner
from parse import base_info
from flask import request, Blueprint, Response
from core.logger import logger
from werkzeug.exceptions import BadRequest
import json
import re
from core.utils import make_response
from .utils import EnterpriseGenealogy, remove_company_code
from sqlalchemy import and_
from flask_csv import send_csv

home = Blueprint('home', __name__)

#
# @home.errorhandler(Exception)
# def handler_exception(e):
#     logger.warning(e)
#     response = Response(json.dumps({"isSuccess": False, "msg": "查询失败,稍后再试."}), mimetype='application/json')
#     return response


@home.route('/get_company_map/', methods=["POST"])
def get_company_map():
    try:
        data = request.get_json()
        if not data:
            '''
            content-type:
            '''
            logger.warning({"isSuccess": False, "msg": "请使用 application/json 传递参数"})
            response = Response(json.dumps({"isSuccess": False, "msg": "请使用 application/json 传递参数"}),
                                mimetype='application/json')
            return response
    except BadRequest:
        logger.warning({"isSuccess": False, "msg": "JSON 格式错误"})
        response = Response(json.dumps({"isSuccess": False, "msg": "JSON 格式错误"}), mimetype='application/json')
        return response

    if not data.get('company_name'):
        logger.warning({"isSuccess": False, "msg": "缺少必要参数"})
        response = Response(json.dumps({"isSuccess": False, "msg": "缺少必要参数"}), mimetype='application/json')
        return response

    company_name = data.get('company_name')

    data = get_company_base_info(company_name)
    if data.get('isSuccess'):
        company_map = EnterpriseGenealogy()
        logger.info('正在构建 {} 企业族谱.'.format(company_name))
        genealogy = company_map.make_company_map(data)
        remove_company_code(genealogy)
        response = make_response(genealogy)
    else:
        response = make_response(data)

    logger.info(data)
    return response


@home.route('/get_company_map/table', methods=["POST", "GET"])
def get_company_map2():
    resp_type = 0
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                logger.warning({"isSuccess": False, "msg": "请使用 application/json 传递参数"})
                response = Response(json.dumps({"isSuccess": False, "msg": "请使用 application/json 传递参数"}),
                                    mimetype='application/json')
                return response
        except BadRequest:
            logger.warning({"isSuccess": False, "msg": "JSON 格式错误"})
            response = Response(json.dumps({"isSuccess": False, "msg": "JSON 格式错误"}), mimetype='application/json')
            return response

        if not data.get('company_name'):
            logger.warning({"isSuccess": False, "msg": "缺少必要参数"})
            response = Response(json.dumps({"isSuccess": False, "msg": "缺少必要参数"}), mimetype='application/json')
            return response
        company_name = data.get('company_name')
        p2p_name = data.get('name')
    else:
        company_name = request.args.get('company_name')
        p2p_name = request.args.get('name')
        resp_type = request.args.get('type')
    data = get_company_base_info2(company_name)
    if data.get('isSuccess'):
        company_map = EnterpriseGenealogy()
        logger.info('正在构建 {} 企业族谱.'.format(company_name))
        genealogy = company_map.make_company_map2(data)
        logger.info(data)
    else:
        response = make_response(data)
        return response
    logger.info('企业族谱响应成功')
    # 请求携带参数，为1时响应最新的简化的csv
    if resp_type == '1':
        genealogy_new = []
        # 添加股东和对外投资
        for row in genealogy:
            c0 = '被查主体'
            c1 = '项目'
            c2 = '内容'
            genealogy_new.append({c0: company_name, c1: row['0'], c2: row['1']})
        # 添加主要人员
        for i in data['main_person']:
            genealogy_new.append({c0: company_name, c1: i['2']+'（当前）', c2: i['1']})
        # 添加变更记录
        from setting import change_address,change_person,change_name
        names = []  # 存放所有变更中出现过的名字
        for i in data['change_record']:
            # 如果变更前变更后信息一致，直接continue掉
            if i['3'] == i['4']:
                continue
            if i['2'] in change_address:
                genealogy_new.append({c0: company_name, c1: '地址', c2: i['4'].replace(' ','')})
                genealogy_new.append({c0: company_name, c1: '地址变更', c2: i['3'].replace(' ','')})
            if i['2'] in change_name:
                genealogy_new.append({c0: company_name, c1: '名称变更', c2: i['3'].replace(' ','')})
            if i['2'] in change_person:
                result1 = clean(i['3'])
                if result1:
                    names = names+result1
                result2 = clean(i['4'])
                if result2:
                    names = names+result2
        print(names)
        names = set(names)
        if names:
            for name in names:
                if name != '':
                    genealogy_new.append({c0: company_name, c1: '历史角色', c2: name})
        return send_csv(genealogy_new, "{}.csv".format(company_name),
                        [c0, c1, c2]
                        )
    genealogy.append({'0': '', '1': '', '2': '', '3': ''})
    genealogy.insert(0, {'0': '层级', '1': '名称', '2': '股东类型', '3': '投资金额', '4': '投资占比', '5': '关联公司'})
    genealogy.insert(0, {'0': '平台名称：' + str(p2p_name), '1': "企业名称：" + data['company_name'],
                         '2': '法人：' + data['contact'], '3': '电话：' + data['tel'], '4': '员工人数：' + data['staff_num'],
                         '5': '注册时间：' + data['found_date']})
    genealogy.insert(1, {'0': '邮箱：' + data['mail'], '1': "企业类型：" + data['company_type'],
                         '2': '统一信用代码：' + data['credit_code'], '3': '组织机构码：' + data['org_code'],
                         '4': '地址：' + data['address'], '5': '状态：' + data['business_status']})
    genealogy.append({'0': '', '1': '', '2': '', '3': ''})
    genealogy.append({'0': '主要人员'})
    genealogy.append({'0': '序号', '1': '姓名', '2': '职位'})
    genealogy = genealogy + data['main_person']
    if data['change_record']:
        genealogy.append({'0': '', '1': '', '2': '', '3': ''})
        genealogy.append({'0': '变更记录'})
        genealogy.append({'0': '序号', '1': '变更日期', '2': '变更项目', '3': '变更前', '4': '变更后'})
        genealogy = genealogy + data['change_record']
    genealogy.append({'0': '分支机构'})
    for branch in data.get('branch'):
        genealogy.append({'0': branch})
    return send_csv(genealogy, "{}.csv".format(company_name),
                    ['0', '1', '2', '3', '4', '5']
                    )


def get_company_base_info2(company_name):
    logger.info('正在使用在线搜索查询 {} 企业基本信息.'.format(company_name))
    # 搜索企业主页
    search_response = get_company_url(company_name)
    if search_response.get("isSuccess"):
        company_url = search_response.get('URL')
        company_code = get_company_code(company_url)
        html_text = spider.get_normal_response(company_url)
        if html_text.get('isSuccess'):
            results = base_info(html_text.get('data'), meta={'company_code': company_code}, table=True)
            response_invert_partner = get_invert_partner(company_code)
            if response_invert_partner.get('isSuccess'):
                results.update(get_invert_partner(company_code).get('data'))
            response = results
        else:
            response = {"isSuccess": False, 'msg': "查询失败，请重试"}
    else:
        response = {"isSuccess": False, 'msg': "查询失败，请重试"}
    return response


def get_company_base_info(company_name):
    session = Session()
    results = session.query(CompanyStore).filter(
        and_(CompanyStore.f_company_name == company_name, CompanyStore.f_tel.isnot(None))).first()
    if results:
        logger.info('本地数据库已搜索到 {} 企业基本信息.'.format(company_name))
        company_code = results.f_company_code
        results = object_to_dict(results)
        response_invert_partner = get_invert_partner(company_code)
        if response_invert_partner.get('isSuccess'):
            results.update(response_invert_partner.get('data'))
            session.close()
            return results
        else:
            session.close()
            return {"isSuccess": False, 'msg': "查询失败，请重试"}

    logger.info('正在使用在线搜索查询 {} 企业基本信息.'.format(company_name))
    search_response = get_company_url(company_name)
    if search_response.get("isSuccess"):
        company_url = search_response.get('URL')
        company_code = get_company_code(company_url)
        html_text = spider.get_normal_response(company_url)
        if html_text.get('isSuccess'):
            results = base_info(html_text.get('data'), meta={'company_code': company_code})
            response_invert_partner = get_invert_partner(company_code)
            if response_invert_partner.get('isSuccess'):
                results.update(get_invert_partner(company_code).get('data'))
            response = results
        else:
            response = {"isSuccess": False, 'msg': "查询失败，请重试"}
    else:
        response = {"isSuccess": False, 'msg': "查询失败，请重试"}
    session.close()
    return response


def get_company_invert_partner(company_code):
    if not company_code:
        logger.warning({"isSuccess": False, "msg": "缺少必要参数"})
        response = {"isSuccess": False, "msg": "缺少必要参数"}
        return response
    data = get_invert_partner(company_code)
    if data.get('isSuccess'):
        response = data.get('data')
        return response

# 判断是否为纯中文
def is_all_chinese(strs):
    for _char in strs:
        if not '\u4e00' <= _char <= '\u9fa5':
            return False
    return True

# 清洗变更记录，找到名字
def clean(change_str):
    name_list = []
    # @.判断是否为联想控股股份有限公司这种的变更，数字索引的
    if change_str.startswith(' 1'):
        results = re.findall('\d  (.*?) [\u4e00-\u9fa5]',change_str)
        for result in results:
            name_list.append(result.replace('*','').replace(' ',''))
        # 有索引的情况不会出现以下其他情况，直接return
        return name_list

    change_str = change_str.replace(' ', '')

    # @.只有一个'-'占位的,直接return
    if change_str == '-':
        return

    # @.满足只有一个名字的情况
    if is_all_chinese(change_str):
        return [change_str]

    # @.将带新增/退出和不带的两种情况统一成一种
    change_str = change_str.replace('[新增]','')
    change_str = change_str.replace('[退出]','')

    # @.带有冒号的情况
    if ':' in change_str or '：' in change_str:
        results = re.findall('[:|：](.*?)[^\u4e00-\u9fa5]',change_str)
        for result in results:
            if is_all_chinese(result):
                name_list.append(result)
        # 有冒号的情况下就不会再出现其他情况了，直接return
        return name_list

    # @.名字（董事）这种情况
    elif '（' in change_str:
        words = re.findall('（(.*?)）',change_str)
        for word in words:
            change_str = change_str.replace(word,'')
            words = re.findall('（(.*?)）', change_str)
        for word in words:
            change_str = change_str.replace(word, '')
        names = change_str.split('（）')
        for name in names:
            if is_all_chinese(name):
                name_list.append(name)
        return name_list

    return [change_str]