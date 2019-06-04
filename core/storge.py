from core import module
from .module import CompanyStore, Investment, Partner, InvestmentPartner
from sqlalchemy import and_
from core.logger import logger
from core import utils
from datetime import datetime
from sqlalchemy.exc import InternalError


def save_item(item):
    company = dict()
    session = module.Session()
    company['f_company_name'] = item.get('company_name')
    company['f_company_code'] = item.get('company_code')
    company['f_tel'] = item.get('tel')
    company['f_mail'] = item.get('mail')
    company['f_contact'] = item.get('contact')
    company['f_registered_capital'] = item.get('registered_capital')
    company['f_found_date'] = item.get('found_date')
    company['f_credit_code'] = item.get('credit_code')
    company['f_company_type'] = item.get('company_type')
    company['f_register_num'] = item.get('register_num')
    company['f_org_code'] = item.get('org_code')
    company['f_address'] = item.get('address')
    company['f_business_scope'] = item.get('business_scope')
    company['f_area'] = item.get('area')
    company['f_business_status'] = item.get('business_status')
    company['f_industry'] = item.get('industry')
    company['f_staff_num'] = item.get('staff_num')
    results = session.query(CompanyStore).filter(CompanyStore.f_company_code == company.get('f_company_code')).first()

    # 更新
    if results:
        company['f_update_time'] = item.get('update_time')
        try:
            session.query(CompanyStore).filter(CompanyStore.f_company_code == company.get('f_company_code')).update(
                company)
            session.commit()
            logger.info("数据已经更新")
        except Exception:
            session.rollback()
    # 添加
    else:
        company['f_update_time'] = item.get('update_time')
        company['f_create_time'] = item.get('create_time')
        company['f_company_id'] = utils.get_id()
        company_store = CompanyStore(**company)
        try:
            session.add(company_store)
            session.commit()
            logger.info("新数据已经保存")
        except Exception:
            session.rollback()
    session.close()


# 储存股东信息和对外投资
def save_invest_partner(item):
    session = module.Session()
    invest_list = item.get('investorList')
    for invest in invest_list:
        data = dict()
        data['f_company_code'] = item.get('company_code')
        data['f_target_company_code'] = invest.get('id')
        data['f_target_company_name'] = invest.get('name')
        data['f_amount'] = invest.get('amount')
        data['f_proportion'] = invest.get('percent')
        data['f_type'] = invest.get('type')
        results = session.query(Investment).filter(and_(Investment.f_company_code == data.get('f_company_code'),
                                                        Investment.f_target_company_code == data.get(
                                                            'f_target_company_code'))).first()
        if results:
            data['f_update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                session.query(Investment).filter(and_(Investment.f_company_code == data.get('f_company_code'),
                                                      Investment.f_target_company_code == data.get(
                                                          'f_target_company_code'))).update(data)
                session.commit()
            except InternalError:
                session.rollback()

        else:
            data['f_create_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data['f_update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            invest_object = Investment(**data)
            session.add(invest_object)
            try:
                session.commit()
            except Exception:
                session.rollback()

    partner_list = item.get('holderList')
    for partner in partner_list:
        data = dict()

        data['f_company_code'] = item.get('company_code')
        data['f_partner_code'] = partner.get('id')
        data['f_partner_name'] = partner.get('name')
        data['f_amount'] = partner.get('amount')
        data['f_proportion'] = partner.get('percent')
        data['f_type'] = partner.get('type')

        results = session.query(Partner).filter(and_(Partner.f_company_code == data.get('f_company_code'),
                                                     Partner.f_partner_code == data.get('f_partner_code'))).first()
        if results:
            data['f_update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                session.query(Partner).filter(and_(Partner.f_company_code == data.get('f_company_code'),
                                                   Partner.f_partner_code == data.get('f_partner_code'))).update(data)
                session.commit()
            except Exception:
                session.rollback()

        else:
            data['f_create_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data['f_update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            partner_object = Partner(**data)
            session.add(partner_object)
            try:
                session.commit()
            except Exception:
                session.rollback()

    company = session.query(CompanyStore).filter(CompanyStore.f_company_code == item.get('company_code')).first()
    company_name = None
    if company:
        company_name = company.f_company_name

    investment_partner_flag = InvestmentPartner(f_company_code=item.get('company_code'), f_company_name=company_name,
                                                f_create_time=datetime.now(),
                                                f_update_time=datetime.now())
    try:
        session.add(investment_partner_flag)
        session.commit()
    except Exception:
        session.rollback()
    session.close()
