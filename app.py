import base64 
import streamlit as st
import yaml
import pandas as pd
import os
from typing import Dict, List

CONFIG_PATH = "config"
DEFAULT_APP_CONFIG_PATH = os.path.join(CONFIG_PATH, "app_config.yaml")
DEFAULT_PW_CONFIG_PATH = os.path.join(CONFIG_PATH, "playwaze_config.yaml")


class App():


    def __init__(self, app_config_path: str = DEFAULT_APP_CONFIG_PATH, pw_config_path: str = DEFAULT_PW_CONFIG_PATH):
        
        self.app_config, self.pw_config = self.load_config(
            app_config_path, 
            pw_config_path)

        st.set_page_config(layout=self.app_config["layout"]) #set to wide mode


    def load_config(self, app_config_path, pw_config_path) -> List[Dict]:
        """Loads the app and playwaze configurations."""

        app_config = load_from_yaml(app_config_path)
        pw_config = load_from_yaml(pw_config_path)


        return app_config, pw_config


    def header(self):
        st.image(self.app_config["logo path"], width=300)
        st.title(self.app_config["site title"])


    def sidebar(self):
        st.sidebar.header("Upload Playwaze Reports:")

        teams_report = self.report_uploader("teams")
        team_members_report = self.report_uploader("team members")

        return teams_report, team_members_report


    def report_uploader(self, report_type) -> None:
        """Create a file uploader in streamlit for playwaze reports."""

        uploaded_file = st.sidebar.file_uploader(f"Upload a {report_type} report", type=[self.pw_config['report file type']])

        if uploaded_file is None:
            # If no file has been uploaded, display a cue to upload the file in the sidebar
            st.warning(f"← Please upload a {report_type} report to continue.")
            st.stop()
               
        return uploaded_file


def load_from_yaml(config_path: str) -> Dict:
    """Parses a yaml file and returns a dictionary."""

    with open (config_path, "r") as f:
        return yaml.safe_load(f)


def csv_downloader(df: pd.DataFrame, filename: str) -> None:
    """Creates a clickable link in streamlit to download the given dataframe as an Excel xlsx file."""

    csvfile = df.to_csv()
    b64 = base64.b64encode(csvfile.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download as CSV</a>'
    st.markdown(href,unsafe_allow_html=True)


if __name__ == "__main__":

    app = App()
    app.header()
    teams_report, team_members_report = app.sidebar()

