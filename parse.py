from lxml import etree
import re
from datetime import datetime
import time
import requests
import json

from core.storge import save_item
from core.request import spider


def base_info(html_text, meta,table=False):
    html = etree.HTML(html_text)
    company = dict()
    company['isSuccess'] = True
    company['msg'] = "查询成功"
    company['company_name'] = '###'.join(
        html.xpath("//h1[@class='name']/text()"))
    company['company_code'] = meta.get('company_code')
    company['tel'] = '###'.join(html.xpath('//span[text()="电话："]/following-sibling::span[1]/text()'))
    company['mail'] = '###'.join(html.xpath('//span[text()="邮箱："]/following-sibling::span[1]/text()'))
    company['contact'] = '###'.join(html.xpath(
        '//*[@id="_container_baseInfo"]/table[1]/tbody/tr[1]/td[1]/div/div[1]/div[2]/div[1]/a/text()'))
    # 注册资本
    company['registered_capital'] = '###'.join(html.xpath('//td[text()="实缴资本"]/following-sibling::td[1]/text()'))

    # 人员规模
    company['staff_num'] = '###'.join(html.xpath('//td[contains(text(),"人员规模")]/following-sibling::td/text()'))

    found_data = re.search(
        '.*(?=至)',
        '###'.join(
            html.xpath('//td[text()="营业期限"]/following-sibling::td/span/text()')))
    if found_data:
        company['found_date'] = found_data.group()
    else:
        company['found_date'] = ''
    # 统一社会信用代码
    company['credit_code'] = '###'.join(
        html.xpath('//td[text()="统一社会信用代码"]/following-sibling::td[1]/text()'))
    # 公司类型
    company['company_type'] = '###'.join(
        html.xpath('//td[text()="公司类型"]/following-sibling::td[1]/text()'))
    # 工商注册号
    company['register_num'] = '###'.join(
        html.xpath('//td[contains(text(),"工商注册号")]/following-sibling::td/text()'))
    # 组织机构代码
    company['org_code'] = '###'.join(
        html.xpath('//td[contains(text(),"组织机构代码")]/following-sibling::td/text()'))
    # 地址
    company['address'] = '###'.join(
        html.xpath('//td[contains(text(),"注册地址")]/following-sibling::td/text()'))
    # 经营范围
    company['business_scope'] = '###'.join(html.xpath(
        '//td[contains(text(),"经营范围")]/following-sibling::td//span/text()'))
    # 行业
    industry = '###'.join(html.xpath('//td[text()="行业"]/following-sibling::td[1]/text()'))
    company['industry'] = industry
    # 数据更新时间
    company['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 创建时间
    company['create_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 公司状态
    company['business_status'] = '###'.join(html.xpath('//td[text()="经营状态"]/following-sibling::td[1]/text()'))
    # 地区
    company['area'] = '###'.join(
        html.xpath("//div[@id='_container_baseInfo']//tbody//tr[8]//td[2]/text()"))
    save_item(company)
    # 主要人员
    if not table:
        return company
    company['main_person'] = []
    main_person = '###'.join(html.xpath('//div[text()="主要人员"]/span/text()'))
    main_person = int(main_person) if main_person != '' else 0
    if main_person > 0:
        main_person_list = html.xpath('//*[@id="_container_staff"]/div/table/tbody/tr')
        for p in main_person_list:
            num = p.xpath('./td[1]/text()')[0]
            try:
                name = p.xpath('./td[2]/div/div[2]/a/text()')[0]
            except:
                name = p.xpath('./td[2]/table/tr/td[2]/span/text()')[0]
            position = ''.join(p.xpath('./td[3]/span/text()'))
            company['main_person'].append({'0': num, '1': name, '2': position})

    # 变更记录 需要额外请求
    company['change_record'] = []
    change_record = '###'.join(html.xpath('//div[text()="变更记录"]/span/text()'))
    if change_record == '99+':
        change_record = '###'.join(html.xpath('//*[@id="nav-main-changeCount"]/span[2]/text()'))
        change_record = int(change_record)
    else:
        change_record = int(change_record) if change_record != '' else 0
    # 第一页
    if change_record > 0:
        change_record_list = html.xpath('//*[@id="_container_changeinfo"]/table/tbody/tr')
        for c in change_record_list:
            num = c.xpath('./td[1]/text()')[0]
            change_date = c.xpath('./td[2]/text()')[0]
            change_content = c.xpath('./td[3]/text()')[0]
            change_before = c.xpath('./td[4]')[0]
            change_before = etree.tostring(change_before, encoding="utf-8", pretty_print=True, method="html").decode(
                encoding='utf-8')
            change_before = ' '.join(re.findall('>(.*?)<', change_before))
            change_after = c.xpath('./td[5]')[0]
            change_after = etree.tostring(change_after, encoding="utf-8", pretty_print=True, method="html").decode(
                encoding='utf-8')
            change_after = ' '.join(re.findall('>(.*?)<', change_after))
            company['change_record'].append({'0':num,'1':change_date,'2':change_content,'3':change_before,'4':change_after})

    change_record_page = 1
    if change_record > 10:
        change_record_page = change_record // 10 if change_record % 10 == 0 else change_record // 10 + 1
    for i in range(2, change_record_page + 1):
        url = 'https://www.tianyancha.com/pagination/changeinfo.xhtml?ps=10&pn={}&id={}&_={}'.format(i, meta.get(
            'company_code'), str(int(time.time() * 1000)))
        html = spider.get_normal_response(url).get('data')
        html = etree.HTML(html)
        change_record_list = html.xpath('//table/tbody/tr')
        for c in change_record_list:
            num = c.xpath('./td[1]/text()')[0]
            change_date = c.xpath('./td[2]/text()')[0]
            change_content = c.xpath('./td[3]/text()')[0]
            change_before = c.xpath('./td[4]')[0]
            change_before = etree.tostring(change_before, encoding="utf-8", pretty_print=True, method="html").decode(
                encoding='utf-8')
            change_before = ' '.join(re.findall('>(.*?)<', change_before))
            change_after = c.xpath('./td[5]')[0]
            change_after = etree.tostring(change_after, encoding="utf-8", pretty_print=True, method="html").decode(
                encoding='utf-8')
            change_after = ' '.join(re.findall('>(.*?)<', change_after))
            company['change_record'].append(
                {'0': num, '1': change_date, '2': change_content, '3': change_before, '4': change_after})
    company['branch'] = get_branch(company['company_code'])
    return company

def get_branch(code):
    def fun(n):
        return chr(n % 256)
    t = int(time.time() * 1000)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15'
    }

    url = 'https://dis.tianyancha.com/qq/{}.json?random={}'.format(code,str(t))
    resp = requests.get(url, headers=headers)
    cookies = resp.cookies.get_dict()
    resp = json.loads(resp.text)
    s = ''
    for i in resp['data']['v'].split(','):
        s += fun(int(i))

    rtoken = re.findall('rtoken=(.*?);', s)[0]

    cookies['rtoken'] = rtoken
    url = 'https://dis.tianyancha.com/dis/enterpriseMap.json?id={}'.format(code)
    resp = requests.get(url, cookies=cookies, headers=headers).text
    resp = json.loads(resp)
    branch = resp['data']['branch']
    branch_list = []
    for b in branch:
        branch_list.append(b['name'])
    return branch_list