import streamlit as st
from streamlit_option_menu import option_menu

import log2_user
import log2_admin

class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({
            "title": title,
            "function": func
        })

    def run(self):
        with st.sidebar:  # Use st.sidebar instead of st
            app = option_menu(
                menu_title='',
                options=['Home', 'User', 'Admin'],
                icons=['house-fill', 'person-circle', 'person-circle'],
                menu_icon='',
                default_index=0,
                styles={
                    "container": {"padding": "5!important", "background-color": 'black'},
                    "icon": {"color": "white", "font-size": "23px"},
                    "nav-link": {"color": "white", "font-size": "20px", "text-align": "left", "margin": "0px",
                                 "--hover-color": "blue"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                }
            )

        if app == "Home":
            
            st.title("Welcome!")
            st.text("Introducing CRIME MAPPING ANALYTIC TOOL")
        elif app == "User":
            log2_user.login()
        elif app == "Admin":
            log2_admin.login()

if __name__ == "__main__":
    st.set_page_config(page_title="Home")
    multi_app = MultiApp()
    multi_app.run()
