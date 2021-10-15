from remi import App, start
from gui import GUI

class EmployeePortal(App):

    def __init__(self, *args):
        super(EmployeePortal, self).__init__(*args, static_file_path={'my_res': './resx/'})

    def idle(self):
        pass

    def main(self):
        G = GUI(self)
        return G.construct_ui()


configuration = {'config_project_name': 'MainScreen',
                 'config_address': '127.0.0.1',
                 'config_port': 8085, 'config_multiple_instance': True,
                 'config_enable_file_cache': True,
                 'config_start_browser': True,
                 'config_resourcepath': './resx/'}


start(EmployeePortal, address=configuration['config_address'], port=configuration['config_port'],
      multiple_instance=configuration['config_multiple_instance'],
      enable_file_cache=configuration['config_enable_file_cache'],
      start_browser=configuration['config_start_browser'])

