import logging
import os
import requests

from multiprocessing import Process

from flask import current_app, request
from flask_restx import Namespace, fields

from web_interface.rest.helper import error_message, success_message
from web_interface.rest.rest_resource_base import RestResourceBase
from web_interface.security.decorator import roles_accepted
from web_interface.security.privileges import PRIVILEGES

api = Namespace('rest/cve_update', description='Update vulnerability library')

update_model = api.model('Update CVE', {
    'remote': fields.String(description='结果通知api', cls_or_instance=fields.String, required=True),
    'retry': fields.Integer(description='结果通知失败尝试次数', required=False, default=5)
})


@api.route('', doc={'description': 'Update vulnerability library'})
class RestCVEUpdate(RestResourceBase):
    URL = '/rest/cve_update'

    @roles_accepted(*PRIVILEGES['view_analysis'])
    @api.expect(update_model)
    def put(self):
        '''
        Update vulnerability library
        '''
        try:
            remote_url = request.json.get("remote")
            retry = request.json.get("retry", 5)
            script_path = os.path.join(current_app.BASE_DIR, "plugins/analysis/cve_lookup/install.sh")
            if not os.path.exists(script_path):
                return error_message("更新操作失败", self.URL)
            process = Process(target=self.post_update, args=(script_path, remote_url, retry))
            process.start()
        except Exception:
            return error_message("更新操作失败", self.URL)

        return success_message(dict(message="操作成功,正在下载漏洞库文件"), self.URL)

    def post_update(self, script_path, remote_url, retry):
        """
        执行下载在脚本以及通知业务后端
        :param script_path:string 脚本所在的目录
        :param remote_url:string 业务后端的通知url
        :param retry: int 通知失败尝试的次数
        :return:
        """
        is_successful = 2
        try:
            os.system("bash %s" % script_path)
        except Exception as e:
            logging.error(e)
            is_successful = 2
        else:
            is_successful = 0
        finally:
            for _ in range(retry):
                try:
                    requests.post(remote_url, json={"status": is_successful})
                    logging.info("通知成功")
                    return
                except Exception as e:
                    logging.error(e)
                    continue
            logging.info("通知失败")
