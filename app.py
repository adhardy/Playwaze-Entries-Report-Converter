import base64 
import streamlit as st
import yaml
import pandas as pd
import numpy as np
import os
from typing import Dict, List

CONFIG_PATH = "config"
DEFAULT_APP_CONFIG_PATH = os.path.join(CONFIG_PATH, "app_config.yaml")
DEFAULT_PW_CONFIG_PATH = os.path.join(CONFIG_PATH, "playwaze_config.yaml")

APP_VIEWS = ("Entries", "Crews", "Events", "Clubs", "Rowers", "CofD")

# column names for reports for convenience in code. The strings should match that in the playwaze config file.
COL_CREW_ID = "crew id"
COL_BOAT_TYPE = "boat type"
COL_CLUB = "club"
COL_CREW_NAME = "crew name"
COL_CREW_LETTER = "crew letter"
COL_SEATS = "seats"
COL_VERIFIED = "verified"
COL_CAPTAIN = "captain"
COL_CAPTAIN_NAME = "captain name"
COL_COX = "cox"
COL_COX_NAME = "cox name"

TEAM_COLUMNS = [COL_CREW_ID, COL_BOAT_TYPE, COL_CLUB, COL_CREW_NAME, 
    COL_CREW_LETTER, COL_SEATS, COL_VERIFIED, COL_CAPTAIN,COL_CAPTAIN_NAME, COL_COX, COL_COX_NAME]

COL_MEMBER_ID =  "member id"
COL_NAME = "name"
COL_GENDER = "gender"
COL_DOB = "dob"
COL_SR_ID = "sr member id"
COL_SR_NUMBER = "sr member number"
COL_MEMBERSHIP_TYPE = "membership type"
COL_EXPIRY = "membership expiry"
COL_ROW_POINTS = "rowing points"
COL_ROW_NOVICE = "rowing novice"
COL_SCULL_POINTS = "sculling points"
COL_SCULL_NOVICE = "sculling novice"
COL_PRIMARY_CLUB = "primary club"
COL_ADDITIONAL_CLUBS = "additional clubs"
COL_FIRST_LICENCE = "first licence start date"
COL_COMPOSITE_CLUBS = "composite clubs"

MEMBER_COLUMNS = [COL_BOAT_TYPE, COL_CLUB, COL_CREW_ID, COL_CREW_LETTER, COL_CREW_NAME, COL_MEMBER_ID, 
    COL_NAME, COL_GENDER, COL_DOB, COL_SR_ID, COL_SR_NUMBER, COL_MEMBERSHIP_TYPE,COL_EXPIRY,COL_ROW_POINTS,
    COL_ROW_NOVICE, COL_SCULL_POINTS, COL_SCULL_NOVICE, COL_PRIMARY_CLUB,COL_ADDITIONAL_CLUBS, COL_FIRST_LICENCE,COL_COMPOSITE_CLUBS]

REPORT_FILE_TYPE = "xlsx"

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
        self.teams_report = self.report_uploader("teams")
        self.team_members_report = self.report_uploader("team members")


    def body(self):
        pass


    def report_preprocessing(self) -> None:

        df_teams = self.load_and_clean_teams_report()
        df_team_members = self.load_and_clean_team_members_report()

        st.write(df_teams)
        st.write(df_team_members)


    def load_and_clean_teams_report(self) -> pd.DataFrame:

        df = pd.read_excel(self.teams_report) # load teams report
        df = cleanup_report_columns(df, list(self.pw_config["teams report columns"].values()), list(self.pw_config["teams report columns"].keys()))
        df = df[TEAM_COLUMNS] # make sure they are in order

        df[[COL_COX, COL_VERIFIED, COL_CAPTAIN]] = clean_booleans(df[[COL_COX, COL_VERIFIED, COL_CAPTAIN]])
        df[COL_CREW_ID] = df[COL_CREW_ID].str.replace("teams/", "", regex=True) # change the entry ids so the column name and values match the crew id from the members report

        return df


    def load_and_clean_team_members_report(self) -> pd.DataFrame:
        
        df = pd.read_excel(self.team_members_report) # load team members report
        df = cleanup_report_columns(df, list(self.pw_config["team members report columns"].values()), list(self.pw_config["team members report columns"].keys()))
        df = df[MEMBER_COLUMNS] # make sure they are in order

        df[[COL_ROW_NOVICE, COL_SCULL_NOVICE]] = clean_booleans(df[[COL_ROW_NOVICE, COL_SCULL_NOVICE]])

        return df


    def report_uploader(self, report_type) -> st.uploaded_file_manager.UploadedFile:
        """Create a file uploader in streamlit for playwaze reports."""

        uploaded_file = st.sidebar.file_uploader(f"Upload a {report_type} report", type=[REPORT_FILE_TYPE])

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

def cleanup_report_columns(df: pd.DataFrame, column_numbers: List[int], column_names: List[str]) -> pd.DataFrame:

    df = df.iloc[:,column_numbers] # keep only the columns we need
    df.columns = column_names # and rename them to match names in config

    return df


def clean_booleans(df: pd.DataFrame) -> pd.DataFrame:
    """Replaces Y, N and nan with True/False"""

    df = df.replace({"Y":True, np.nan:False, "N":False})
    return df.astype(bool)


if __name__ == "__main__":

    app = App()


