import requests
import core.utils
from setting import headers
from requests.exceptions import ProxyError, ConnectTimeout, ConnectionError, ReadTimeout


class Spider(object):

    def get_normal_response(self, url):
        for item in range(5):
            res = core.utils.get_normal_cookies()
            if res.get('isSuccess'):
                try:
                    response = requests.get(url=url, cookies=res.get('data'), headers=headers)
                except ProxyError:
                    continue
                except ConnectTimeout:
                    continue
                except ReadTimeout:
                    continue
                except ConnectionError:
                    continue
                check_results = self.check_response(response, '普通账号')
                if check_results:
                    break
            else:
                continue
        else:
            return {"isSuccess": False, 'msg': "页面检查不通过"}

        return {"isSuccess": True, 'data': response.text}

    def get_vip_response(self, url):
        for item in range(5):
            res = core.utils.get_vip_cookies()
            if res.get('isSuccess'):
                try:
                    response = requests.get(url=url, cookies=res.get('data'), headers=headers)
                except ProxyError:
                    continue
                except ConnectTimeout:
                    continue
                except ReadTimeout:
                    continue
                except ConnectionError:
                    continue
                check_results = self.check_response(response, 'VIP 账号')
                if check_results:
                    break
            else:
                continue
        else:
            return {"isSuccess": False, 'msg': "页面检查不通过"}

        return {"isSuccess": True, 'data': response.text}

    @classmethod
    def check_response(cls, response, flag):
        if '天眼查校验' in response.text:
            core.utils.logger.warning('{} 天眼查校验'.format(flag))
            return False
        elif '503 Service Unavailable' in response.text:
            core.utils.logger.warning('{} 503 error '.format(flag))
            return False
        elif '登录/注册' in response.text:
            core.utils.logger.warning('{} 需要登录...'.format(flag))
            return False
        elif '503 Service Temporarily Unavailable' in response.text:
            core.utils.logger.warning('{} 503 error '.format(flag))
            return False
        elif '非人类行为' in response.text:
            core.utils.logger.warning('{} 账号被封.'.format(flag))
            return False
        return True


spider = Spider()
