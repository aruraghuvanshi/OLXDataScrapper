from creators import C
import pandas as pd
import datetime
from time import time
import remi.gui as rm



class GUI:

    def __init__(self, A):
        super(GUI, self).__init__()
        self.A = A
        self.registry_info = {}
        self.login_info = {}

    def construct_ui(self):
        self.window = rm.Container()

        self.window.css_width = "100%"
        self.window.css_left = "0.0px"
        self.window.css_top = "0.0px"
        self.window.css_position = "absolute"
        self.window.css_height = "100%"

        self.window.css_background_color = "lightgrey"
        self.frame_login_register_color = 'beige'


        self.frame_login_register = C.create_container(self.window, 30, 10, 90, 0)
        self.frame_login_register.css_background_color = self.frame_login_register_color


        self.login_btn = C.create_button(self.window, 3, 7, 92, 1, text='Login',
                                         command=lambda x: self.login_clicked())
        self.register_btn = C.create_button(self.window, 3, 7, 92, 6, text='Register',
                                            command=lambda x: self.register_clicked())

        return self.window


    def login_clicked(self):

        print(f'Login Button pressed')
        self.frame_login_register.empty()
        self.lbl_username = C.create_label(self.frame_login_register, 7, 40, 5, 40, text='Username:', bg='white', fg='black')
        self.lbl_pw = C.create_label(self.frame_login_register,  7, 40, 5, 50, text='Password:', bg='white', fg='black')
        self.username = C.create_entry(self.frame_login_register, 7, 52, 40, 40, fg='black', bg='white',
                                       command=self.log_on_enter_username)
        self.pw = C.create_entry(self.frame_login_register, 7, 52, 40, 50, fg='black',
                                 command=self.log_on_enter_pw)
        self.login_ok = C.create_button(self.frame_login_register, 10, 15, 75, 65, text='OK',
                                        command=lambda x: self.login_ok_clicked())


    def login_ok_clicked(self):
        print(f'Ok clicked on Login Button')
        self.frame_login_register.empty()

        # Do the username/password match here
        df = pd.read_csv('user_registration_info.csv')
        df.drop('Unnamed: 0', inplace=True, axis=1)

        print(f"Login username: {self.login_info['username']}")  # Aru
        print(f"Login pw: {self.login_info['pw1']}")             # 22

        x = df.loc[df.username == self.login_info['username']]
        y = df.loc[df.pw1 == self.login_info['pw1']]
        print(f'X\n{x}')
        print(f'Y\n{y}')
        if x.empty or y.empty:
            C.create_label(self.frame_login_register, 10, 75, 20, 35,
                           text='No Match.', bg='azure')
        else:
            C.create_label(self.frame_login_register, 10, 75, 20, 35,
                           text=f"Logged In.", bg='azure')
            user = self.login_info['username']
            U = User(user)
            C.create_label(self.frame_login_register, 10, 75, 20, 35,
                           text=f"Session: {U.get_name()}", bg='azure')
            self.login_btn = C.create_button(self.window, 3, 7, 92, 1, text='Logout',
                                             command=lambda x: self.login_clicked(),
                                             bg='lightgreen')
