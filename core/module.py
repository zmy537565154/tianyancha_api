from sqlalchemy import Column, DateTime, Text, Integer, create_engine, VARCHAR, Date, Boolean, SmallInteger
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from setting import sqlalchemy_mysql

engine = create_engine(sqlalchemy_mysql,
                       max_overflow=3000, pool_size=5000, pool_recycle=1800)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class CompanyStore(Base):
    __tablename__ = 't_company_store'
    f_id = Column(Integer, primary_key=True, autoincrement=True)
    f_company_id = Column(VARCHAR(20), unique=True)
    # 企业名称
    f_company_name = Column(VARCHAR(255))
    f_company_code = Column(Integer)
    # 电话 邮箱
    f_tel = Column(VARCHAR(100))
    f_mail = Column(VARCHAR(255))
    # 法人
    f_contact = Column(VARCHAR(100))
    # 注册资本
    f_registered_capital = Column(VARCHAR(100))
    # 注册日期
    f_found_date = Column(Date)
    # 社会统一信用号
    f_credit_code = Column(VARCHAR(100))
    # 企业类型
    f_company_type = Column(VARCHAR(255))
    # 工商注册号
    f_register_num = Column(VARCHAR(100))
    # 组织机构代码
    f_org_code = Column(VARCHAR(100))
    # 注册地
    f_address = Column(VARCHAR(255))
    # 经营范围
    f_business_scope = Column(Text)
    # 地址
    f_area = Column(VARCHAR(100))
    # 企业状态
    f_business_status = Column(VARCHAR(100))
    # 行业
    f_industry = Column(VARCHAR(100))
    f_update_time = Column(DateTime)
    f_create_time = Column(DateTime)
    # 员工人数
    f_staff_num = Column(VARCHAR(255))


class Investment(Base):
    __tablename__ = "t_investment"
    f_id = Column(Integer, primary_key=True, autoincrement=True)
    f_company_code = Column(VARCHAR(255))
    f_target_company_name = Column(VARCHAR(255))
    f_target_company_code = Column(VARCHAR(255))
    f_amount = Column(VARCHAR(255))
    f_proportion = Column(VARCHAR(255))
    f_time = Column(VARCHAR(255))
    f_type = Column(SmallInteger)
    f_status = Column(VARCHAR(255))
    f_update_time = Column(DateTime)
    f_create_time = Column(DateTime)


class Partner(Base):
    __tablename__ = "t_partner"
    f_id = Column(Integer, primary_key=True, autoincrement=True)
    f_partner_name = Column(VARCHAR(255))
    f_partner_code = Column(VARCHAR(255))
    f_company_code = Column(DateTime)
    f_amount = Column(VARCHAR(255))
    f_proportion = Column(VARCHAR(255))
    f_time = Column(VARCHAR(255))
    f_type = Column(SmallInteger)
    f_update_time = Column(DateTime)
    f_create_time = Column(DateTime)


class InvestmentPartner(Base):
    __tablename__ = "t_investment_partner"
    f_id = Column(Integer, primary_key=True, autoincrement=True)
    f_company_code = Column(VARCHAR(255))
    f_company_name = Column(VARCHAR(255))
    f_create_time = Column(DateTime)
    f_update_time = Column(DateTime)


Base.metadata.create_all(engine)
