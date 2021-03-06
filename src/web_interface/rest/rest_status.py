from flask_restx import Namespace

from helperFunctions import uid
from helperFunctions.database import ConnectTo
from intercom.front_end_binding import InterComFrontEndBinding
from objects.firmware import Firmware
from storage.db_interface_frontend import FrontEndDbInterface
from storage.db_interface_statistic import StatisticDbViewer
from web_interface.rest.helper import error_message, success_message
from web_interface.rest.rest_resource_base import RestResourceBase
from web_interface.security.decorator import roles_accepted
from web_interface.security.privileges import PRIVILEGES

api = Namespace('rest/status', description='Request FACT\'s system status')


@api.route('')
class RestStatus(RestResourceBase):
    URL = '/rest/status'

    @roles_accepted(*PRIVILEGES['status'])
    @api.doc(responses={200: 'Success', 400: 'Error'})
    def get(self):
        '''
        Request system status
        Request a json document showing the system state of FACT, similar to the system health page of the GUI
        '''
        components = ['frontend', 'database', 'backend']
        status = {}
        with ConnectTo(StatisticDbViewer, self.config) as stats_db:
            for component in components:
                status[component] = stats_db.get_statistic(component)

        with ConnectTo(InterComFrontEndBinding, self.config) as sc:
            plugins = sc.get_available_analysis_plugins()

        if not any(bool(status[component]) for component in components):
            return error_message('Cannot get FACT component status: Database may be down', self.URL, return_code=404)

        response = {
            'system_status': status,
            'plugins': self._condense_plugin_information(plugins),
        }
        return success_message(response, self.URL)

    @staticmethod
    def _condense_plugin_information(plugins):
        plugins.pop('unpacker', None)

        for name, information in plugins.items():
            description, _, _, version, _, _, _, _ = information
            plugins[name] = dict(description=description, version=version)

        return plugins


@api.route('/<string:uid>', doc={'description': '', 'params': {'uid': 'Firmware UID'}})
class RestStatusGetWithUid(RestResourceBase):
    URL = '/rest/status'

    @roles_accepted(*PRIVILEGES['status'])
    @api.doc(responses={200: 'Success', 400: 'Unknown UID'})
    def get(self, uid):
        with ConnectTo(FrontEndDbInterface, self.config) as connection:
            firmware = connection.firmwares.find_one(uid)
        if not firmware:
            return error_message(f'No firmware with UID {uid} found', self.URL, dict(uid=uid))
        filter_firware = {}
        filter_firware["uid"] = firmware['_id']
        filter_firware["size"] = firmware['size']
        filter_firware["file_name"] = firmware['file_name']
        filter_firware["device_name"] = firmware['device_name']
        filter_firware["device_class"] = firmware['device_class']
        filter_firware["analyses_stats"] = firmware['analyses_stats']
        return success_message(dict(firmware=filter_firware), self.URL, request_data=dict(uid=uid))
