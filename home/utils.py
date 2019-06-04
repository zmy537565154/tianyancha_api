from concurrent.futures import ThreadPoolExecutor, as_completed
import home.views


class EnterpriseGenealogy(object):

    def __init__(self):
        self.partner_level_1 = []
        self.partner_level_2 = []
        self.partner_level_3 = []

        self.invest_level_1 = []
        self.invest_level_2 = []
        self.invest_level_3 = []

    def request(self, company_code):
        res = home.views.get_company_invert_partner(company_code)
        return res

    def get_partner_1(self, node):
        holderList = [x for x in node.get('holderList') if x.get('type') == 2]
        if holderList:
            length = 50 if len(holderList) >= 50 else len(holderList)
            executor = ThreadPoolExecutor(max_workers=length)
            tasks = [executor.submit(self.request, holder.get('id')) for holder in holderList]
            results = as_completed(tasks)
            for feature in results:
                data = feature.result()
                for k, v in data.items():
                    for item in v:
                        if isinstance(item, dict):
                            item.update({"level": 2, "category": 1})
                self.partner_level_1.append(data)

    def get_partner_2(self, node):
        holderList = [company for item in node for company in item.get('holderList') if company.get("type") == 2]
        if holderList:
            length = 50 if len(holderList) >= 50 else len(holderList)
            executor = ThreadPoolExecutor(max_workers=length)
            tasks = [executor.submit(self.request, holder.get('id')) for holder in holderList]
            results = as_completed(tasks)
            for feature in results:
                data = feature.result()
                for k, v in data.items():
                    for item in v:
                        if isinstance(item, dict):
                            item.update({"level": 3, "category": 1})
                self.partner_level_2.append(data)

    def get_partner_3(self, node):
        holderList = [company for item in node for company in item.get('holderList') if company.get("type") == 2]
        if holderList:
            length = 50 if len(holderList) >= 50 else len(holderList)
            executor = ThreadPoolExecutor(max_workers=length)
            tasks = [executor.submit(self.request, holder.get('id')) for holder in holderList]
            results = as_completed(tasks)
            for feature in results:
                data = feature.result()
                for k, v in data.items():
                    for item in v:
                        if isinstance(item, dict):
                            item.update({"level": 4, "category": 1})
                self.partner_level_3.append(data)

    def get_partner_children_node(self, node, company_code):
        for temp in node:
            holder_list = temp.get('holderList')
            for holder in holder_list:
                if holder.get('start_node') == company_code:
                    return temp
        else:
            return dict()

    def get_invest_1(self, node):
        investorList = [x for x in node.get('investorList')]
        if investorList:
            length = 50 if len(investorList) >= 50 else len(investorList)
            executor = ThreadPoolExecutor(max_workers=length)
            tasks = [executor.submit(self.request, invest.get('id')) for invest in investorList]
            results = as_completed(tasks)
            for feature in results:
                data = feature.result()
                for k, v in data.items():
                    for item in v:
                        if isinstance(item, dict):
                            item.update({"level": 2, "category": 2})
                self.invest_level_1.append(data)

    def get_invest_2(self, node):
        investorList = [company for item in node for company in item.get('investorList')]
        if investorList:
            length = 50 if len(investorList) >= 50 else len(investorList)
            executor = ThreadPoolExecutor(max_workers=length)
            tasks = [executor.submit(self.request, invest.get('id')) for invest in investorList]
            results = as_completed(tasks)
            for feature in results:
                data = feature.result()
                for k, v in data.items():
                    for item in v:
                        if isinstance(item, dict):
                            item.update({"level": 3, "category": 2})
                self.invest_level_2.append(data)

    def get_invest_3(self, node):
        investorList = [company for item in node for company in item.get('investorList')]
        if investorList:
            length = 50 if len(investorList) >= 50 else len(investorList)
            executor = ThreadPoolExecutor(max_workers=length)
            tasks = [executor.submit(self.request, invest.get('id')) for invest in investorList]
            results = as_completed(tasks)
            for feature in results:
                data = feature.result()
                for k, v in data.items():
                    for item in v:
                        if isinstance(item, dict):
                            item.update({"level": 4, "category": 2})
                self.invest_level_3.append(data)

    def get_invest_children_node(self, node, company_code):
        for temp in node:
            invest_list = temp.get('investorList')
            for invest in invest_list:
                if invest.get('start_node') == company_code:
                    return temp
        else:
            return dict()

    def build_partner_map(self, root):
        # 第一层
        holder_list_1 = [x for x in root.setdefault('holderList', []) if x.get('type') == 2]

        for holder_1 in holder_list_1:
            company_code_1 = holder_1.get('id')
            children_node_1 = self.get_partner_children_node(self.partner_level_1, company_code_1)
            holder_1.update(children_node_1)

            # 第二层
            holder_list_2 = (x for x in holder_1.setdefault('holderList', []) if x.get('type') == 2)
            for holder_2 in holder_list_2:
                company_code_2 = holder_2.get('id')
                children_node_2 = self.get_partner_children_node(self.partner_level_2, company_code_2)
                holder_2.update(children_node_2)

                # 第三层
                holder_list_3 = (x for x in holder_2.setdefault('holderList', []) if x.get('type') == 2)
                for holder_3 in holder_list_3:
                    company_code_3 = holder_3.get('id')
                    children_node_3 = self.get_partner_children_node(self.partner_level_3, company_code_3)
                    holder_3.update(children_node_3)

    def build_invest_map(self, root):
        # 第一层
        invest_list_1 = [x for x in (root.get('investorList') if root.get('investorList') else [])]
        for invest_1 in invest_list_1:
            company_code_1 = invest_1.get('id')
            children_node_1 = self.get_invest_children_node(self.invest_level_1, company_code_1)
            invest_1.update(children_node_1)

            # 第二层
            invest_list_2 = (x for x in (invest_1.get('investorList') if invest_1.get('investorList') else []))
            for invest_2 in invest_list_2:
                company_code_2 = invest_2.get('id')
                children_node_2 = self.get_invest_children_node(self.invest_level_2, company_code_2)
                invest_2.update(children_node_2)

                # 第三层
                invest_list_3 = (x for x in (invest_2.get('investorList') if invest_2.get('investorList') else []))
                for invest_3 in invest_list_3:
                    company_code_3 = invest_3.get('id')
                    children_node_3 = self.get_invest_children_node(self.invest_level_3, company_code_3)
                    invest_3.update(children_node_3)

    def make_company_map(self, root):
        self.get_partner_1(root)
        self.get_partner_2(self.partner_level_1)
        self.get_partner_3(self.partner_level_2)
        self.build_partner_map(root)

        self.get_invest_1(root)
        self.get_invest_2(self.invest_level_1)
        self.get_invest_3(self.invest_level_2)
        self.build_invest_map(root)

        return root

    # 构造.csv响应
    def make_company_map2(self, root):
        self.get_partner_1(root)
        self.get_partner_2(self.partner_level_1)
        self.get_partner_3(self.partner_level_2)

        self.get_invest_1(root)
        self.get_invest_2(self.invest_level_1)
        self.get_invest_3(self.invest_level_2)

        # 把企业名称和id一一对应，方便显示关联公司
        self.get_company_code_dict(root)
        c0 = '0'
        c1 = '1'
        c2 = '2'
        c3 = '3'
        c4 = '4'
        c5 = '5'

        csv_result = []
        # 1级股东
        for i in root['holderList']:
            holder_type = '机构股东'
            if i['type'] == 1:
                holder_type = '自然人股东'
            d = {c0:str(i['level']) + '级股东',c1:i['name'],c2:holder_type,c3:i['amount'], c4:i['percent'], c5: root['company_name']}
            csv_result.append(d)

        # 2级股东
        for j in self.partner_level_1:
            if j.get('holderList'):
                for i in j['holderList']:
                    holder_type = '机构股东'
                    if i['type'] == 1:
                        holder_type = '自然人股东'
                    d = {c0: str(i['level']) + '级股东', c1: i['name'], c2: holder_type, c3: i['amount'],
                         c4: i['percent'], c5: self.company_code_dict[i['start_node']]}
                    csv_result.append(d)

        # 3级股东
        for j in self.partner_level_2:
            if j.get('holderList'):
                for i in j['holderList']:
                    holder_type = '机构股东'
                    if i['type'] == 1:
                        holder_type = '自然人股东'

                    d = {c0: str(i['level']) + '级股东', c1: i['name'], c2: holder_type, c3: i['amount'],
                         c4: i['percent'], c5: self.company_code_dict[i['start_node']]}
                    csv_result.append(d)

        # 4级股东
        for j in self.partner_level_3:
            if j.get('holderList'):
                for i in j['holderList']:
                    holder_type = '机构股东'
                    if i['type'] == 1:
                        holder_type = '自然人股东'

                    d = {c0: str(i['level']) + '级股东', c1: i['name'], c2: holder_type, c3: i['amount'],
                         c4: i['percent'], c5: self.company_code_dict[i['start_node']]}
                    csv_result.append(d)

        # 1级投资
        if root.get('investorList'):
            for i in root['investorList']:
                d = {c0: str(i['level']) + '级投资', c1: i['name'], c2: '', c3: i['amount'],
                     c4: i['percent'], c5: root['company_name']}
                csv_result.append(d)

        # 2级投资
        for j in self.invest_level_1:
            if j.get('investorList'):
                for i in j['investorList']:
                    d = {c0: str(i['level']) + '级投资', c1: i['name'], c2: '', c3: i['amount'],
                         c4: i['percent'], c5: self.company_code_dict[i['start_node']]}
                    csv_result.append(d)

        # 3级投资
        for j in self.invest_level_2:
            if j.get('investorList'):
                for i in j['investorList']:
                    d = {c0: str(i['level']) + '级投资', c1: i['name'], c2: '', c3: i['amount'],
                         c4: i['percent'], c5: self.company_code_dict[i['start_node']]}
                    csv_result.append(d)

        # 4级投资
        for j in self.invest_level_3:
            if j.get('investorList'):
                for i in j['investorList']:
                    d = {c0: str(i['level']) + '级投资', c1: i['name'], c2: '', c3: i['amount'],
                         c4: i['percent'], c5: self.company_code_dict[i['start_node']]}
                    csv_result.append(d)
        return csv_result

    def get_company_code_dict(self, root):
        self.company_code_dict = {}
        for c in root['holderList']:
            self.company_code_dict[c['id']] = c['name']

        for j in self.partner_level_1:
            if j.get('holderList'):
                for c in j['holderList']:
                    self.company_code_dict[c['id']] = c['name']

        for j in self.partner_level_2:
            if j.get('holderList'):
                for c in j['holderList']:
                    self.company_code_dict[c['id']] = c['name']

        for j in self.partner_level_3:
            if j.get('holderList'):
                for c in j['holderList']:
                    self.company_code_dict[c['id']] = c['name']

        if root.get('investorList'):
            if root.get('investorList'):
                for c in root['investorList']:
                    self.company_code_dict[c['id']] = c['name']
        for j in self.invest_level_1:
            if j.get('investorList'):
                for c in j['investorList']:
                    self.company_code_dict[c['id']] = c['name']
        for j in self.invest_level_2:
            if j.get('investorList'):
                for c in j['investorList']:
                    self.company_code_dict[c['id']] = c['name']
        for j in self.invest_level_3:
            if j.get('investorList'):
                for c in j['investorList']:
                    self.company_code_dict[c['id']] = c['name']


def remove_company_code(dict_list):
    try:
        dict_list.pop('company_code')
    except KeyError:
        pass
    for k, v in dict_list.items():
        if isinstance(v, list):
            for item in v:
                remove_company_code(item)
