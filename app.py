import base64 
import streamlit as st
import yaml
import pandas as pd
import numpy as np
import os
from typing import Dict, List
import playwaze_reports as pw

import importlib
importlib.reload(pw)
CONFIG_PATH = "config"
DEFAULT_APP_CONFIG_PATH = os.path.join(CONFIG_PATH, "app_config.yaml")
DEFAULT_PW_CONFIG_PATH = os.path.join(CONFIG_PATH, "playwaze_config.yaml")

APP_VIEWS = ("Entries", "Crews", "Events", "Clubs", "Rowers", "CofD")

class App():


    def __init__(self, app_config_path: str = DEFAULT_APP_CONFIG_PATH, pw_config_path: str = DEFAULT_PW_CONFIG_PATH):
        
        self.app_config, self.pw_config = self.load_config(
            app_config_path, 
            pw_config_path)

        st.set_page_config(layout=self.app_config["layout"]) #set to wide mode

        self.header()
        self.sidebar()
        self.report_preprocessing()
        self.body()


    def load_config(self, app_config_path, pw_config_path) -> List[Dict]:
        """Loads the app and playwaze configurations."""

        app_config = load_from_yaml(app_config_path)
        pw_config = load_from_yaml(pw_config_path)

        return app_config, pw_config


    def header(self):

        st.image(self.app_config["logo path"], width=300)
        st.title(self.app_config["site title"])


    def sidebar(self):

        st.sidebar.header("Select View:")
        self.view = st.sidebar.selectbox(
            "",
            APP_VIEWS)


        st.sidebar.header("Upload Playwaze Reports:")
        self.teams_report = report_uploader("teams")
        self.team_members_report = report_uploader("team members")
        self.members_report = report_uploader("community members", required=False)


    def body(self):
        st.write(self.df_teams)
        st.write(self.df_team_members)
        st.write(self.df_community_members)
        pass


    def report_preprocessing(self) -> None:

        df_teams = self.load_and_clean_teams_report()
        df_team_members = self.load_and_clean_team_members_report()
        if self.members_report is not None:
            df_community_members = self.load_and_clean_community_members_report()
            df_team_members = pw.get_coxes(df_teams, df_team_members, df_community_members)
        else:
            df_team_members = pw.get_coxes(df_teams, df_team_members)

        self.df_teams = df_teams
        self.df_team_members = df_team_members
        if self.members_report is not None:
            self.df_community_members = df_community_members


    def load_and_clean_teams_report(self) -> pd.DataFrame:

        df = pd.read_excel(self.teams_report) # load teams report
        df = pw.cleanup_report_columns(df, list(self.pw_config["teams report columns"].values()), list(self.pw_config["teams report columns"].keys()))
        df = df[pw.TEAM_COLUMNS] # make sure they are in order

        df[[pw.COL_COX, pw.COL_VERIFIED, pw.COL_CAPTAIN]] = pw.clean_booleans(df[[pw.COL_COX, pw.COL_VERIFIED, pw.COL_CAPTAIN]])
        df[pw.COL_CREW_ID] = df[pw.COL_CREW_ID].str.replace("teams/", "", regex=True) # change the entry ids so the column name and values match the crew id from the members report
    
        return df


    def load_and_clean_team_members_report(self) -> pd.DataFrame:
        
        df = pd.read_excel(self.team_members_report) # load team members report
        df = pw.cleanup_report_columns(df, list(self.pw_config["team members report columns"].values()), list(self.pw_config["team members report columns"].keys()))
        df = df[pw.TEAM_MEMBER_COLUMNS] # make sure they are in order

        df[[pw.COL_ROW_NOVICE, pw.COL_SCULL_NOVICE]] = pw.clean_booleans(df[[pw.COL_ROW_NOVICE, pw.COL_SCULL_NOVICE]])
        df[pw.COL_POSITION] = pw.assign_rower_position(df)

        return df

    def load_and_clean_community_members_report(self) -> pd.DataFrame:

        df = pd.read_excel(self.members_report)
        df = pw.cleanup_report_columns(df, list(self.pw_config["community members report columns"].values()), list(self.pw_config["community members report columns"].keys()))

        return df


def load_from_yaml(config_path: str) -> Dict:
    """Parses a yaml file and returns a dictionary."""

    with open (config_path, "r") as f:
        return yaml.safe_load(f)


def report_uploader(report_type: str, required: bool = True) -> st.uploaded_file_manager.UploadedFile:
    """Create a file uploader in streamlit for playwaze reports."""

    uploaded_file = st.sidebar.file_uploader(f"Upload a {report_type} report", type=[pw.REPORT_FILE_TYPE])

    if uploaded_file is None:
        if required:
            # If no file has been uploaded, display a cue to upload the file in the sidebar
            st.warning(f"← Please upload a {report_type} report to continue.")
            st.stop()
        else:
            st.warning(f"Upload a {report_type} to get all cox details.")

    return uploaded_file


def csv_downloader(df: pd.DataFrame, filename: str) -> None:
    """Creates a clickable link in streamlit to download the given dataframe as an Excel xlsx file."""

    csvfile = df.to_csv()
    b64 = base64.b64encode(csvfile.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download as CSV</a>'
    st.markdown(href,unsafe_allow_html=True)


if __name__ == "__main__":

    app = App()


