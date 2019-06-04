from core.module import Session, CompanyStore
from core.request import spider
from core.utils import get_company_url, object_to_dict, get_company_code, get_invert_partner
from parse import base_info
from flask import request, Blueprint, Response
from core.logger import logger
from werkzeug.exceptions import BadRequest
import json
from core.utils import make_response
from .utils import EnterpriseGenealogy, remove_company_code
from sqlalchemy import and_
from flask_csv import send_csv

home = Blueprint('home', __name__)


@home.errorhandler(Exception)
def handler_exception(e):
    logger.warning(e)
    response = Response(json.dumps({"isSuccess": False, "msg": "查询失败,稍后再试."}), mimetype='application/json')
    return response


@home.route('/get_company_map/', methods=["POST"])
def get_company_map():
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


@home.route('/get_company_map/table', methods=["POST","GET"])
def get_company_map2():
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
            results = base_info(html_text.get('data'), meta={'company_code': company_code},table=True)
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
