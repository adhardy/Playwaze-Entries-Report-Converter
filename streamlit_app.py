import streamlit as st
import yaml
import pandas as pd
import os
from typing import Dict, List
import playwaze_reports as pw
import views

import importlib

importlib.reload(pw)
importlib.reload(views)

CONFIG_PATH = "config"
DEFAULT_APP_CONFIG_PATH = os.path.join(CONFIG_PATH, "app_config.yaml")
DEFAULT_PW_CONFIG_PATH = os.path.join(CONFIG_PATH, "playwaze_config.yaml")


class App:
    def __init__(
        self,
        app_config_path: str = DEFAULT_APP_CONFIG_PATH,
        pw_config_path: str = DEFAULT_PW_CONFIG_PATH,
    ):

        self.app_config, self.pw_config = self.load_config(
            app_config_path, pw_config_path
        )

        st.set_page_config(
            layout=self.app_config["layout"],
            page_title=self.app_config["site title"],
            page_icon=self.app_config["logo path"],
            initial_sidebar_state="expanded",
        )

    def load_config(self, app_config_path, pw_config_path) -> List[Dict]:
        """Loads the app and playwaze configurations."""

        app_config = load_from_yaml(app_config_path)
        pw_config = load_from_yaml(pw_config_path)

        return app_config, pw_config

    def display(self):

        self.header()
        self.sidebar()
        self.report_preprocessing()
        self.body()

    def header(self):

        st.image(self.app_config["logo path"], width=300)
        st.title(self.app_config["site title"])

    def sidebar(self):

        st.sidebar.header("Select View:")
        self.view = st.sidebar.selectbox("", views.APP_VIEWS)

        st.sidebar.header("Upload Playwaze Reports:")
        self.teams_report = views.report_uploader("teams")
        self.team_members_report = views.report_uploader("team members")
        self.community_members_report = views.report_uploader(
            "community members", required=False
        )

    def body(self):

        if self.view == views.ENTRIES_VIEW:

            stats = {
                "Entries": self.num_entries,
                "Total Seats (excludes coxes)": self.total_seats,
                "Filled Seats (excludes coxes)": self.filled_seats,
                "Unique Rowers (includes coxes)": self.unique_rowers,
            }
            views.EntriesView(df=self.df_teams, stats=stats)

        if self.view == views.CREWS_VIEW:

            df_crew_list = pw.get_pivoted_team_members_report(
                self.df_team_members, self.df_teams
            )
            views.CrewsListView(df_crew_list)

        if self.view == views.EVENTS_VIEW:

            df_events = pw.get_events_report(self.df_teams)
            views.View(self.view, df_events)

        if self.view == views.CLUBS_VIEW:
            df_clubs = pw.get_clubs_report(self.df_teams, self.df_team_members)
            views.View(self.view, df_clubs)

        if self.view == views.ROWERS_VIEW:
            st.warning(
                "Rowers who are entered into composites may be associated with  \
                the wrong club."
            )
            df_rowers = pw.get_rowers_report(self.df_team_members)
            views.View(self.view, df_rowers)

        if self.view == views.COFD_VIEW:
            df_CoFD = pw.get_COFD_report(self.df_team_members)
            views.CofDView(df_CoFD)

    def report_preprocessing(self) -> None:

        df_teams = self.load_and_clean_teams_report()
        df_team_members = self.load_and_clean_team_members_report()
        if self.community_members_report is not None:
            df_community_members = (
                self.load_and_clean_community_members_report()
            )
            df_team_members = pw.get_coxes(
                df_teams, df_team_members, df_community_members
            )
        else:
            df_team_members = pw.get_coxes(df_teams, df_team_members)
        df_teams = df_teams.drop(pw.COL_COX_NAME, axis=1)
        # remove coxes from the teams report now that they are in team_members

        # assign dfs to self for access in rest of app
        self.df_teams = df_teams
        self.df_team_members = df_team_members
        if self.community_members_report is not None:
            self.df_community_members = df_community_members

        # gather some stats
        self.num_entries = pw.count_num_entries(df_teams)
        self.total_seats, self.filled_seats = pw.count_num_seats(df_teams)
        self.unique_rowers = pw.count_unique_rowers(df_team_members)

    def load_and_clean_teams_report(self) -> pd.DataFrame:

        df = pd.read_excel(self.teams_report)  # load teams report
        df = pw.cleanup_report_columns(
            df,
            list(self.pw_config["teams report columns"].values()),
            list(self.pw_config["teams report columns"].keys()),
        )
        df = df[pw.TEAM_COLUMNS]  # make sure they are in order

        # check that all of the columns in each row are not empty
        required_columns = [
            pw.COL_CREW_ID,
            pw.COL_BOAT_TYPE,
            pw.COL_CLUB,
            pw.COL_CREW_NAME,
            pw.COL_CREW_LETTER,
            pw.COL_SEATS,
            pw.COL_VERIFIED,
            pw.COL_CAPTAIN,
            pw.COL_COX,
        ]
        # check that there are no nans in the required columns
        for col in required_columns:
            if df[col].isnull().sum() > 0:
                st.error(
                    f"{col.title()} is missing values. Please check the teams \
                        report."
                )
                st.stop()

        df[[pw.COL_COX, pw.COL_VERIFIED, pw.COL_CAPTAIN]] = pw.clean_booleans(
            df[[pw.COL_COX, pw.COL_VERIFIED, pw.COL_CAPTAIN]]
        )
        df = pw.clean_composites(df)
        df[pw.COL_CREW_ID] = df[pw.COL_CREW_ID].str.replace(
            "teams/", "", regex=True
        )
        # change the entry ids so the column name and values match the crew id
        # from the members report

        return df

    def load_and_clean_team_members_report(self) -> pd.DataFrame:

        df = pd.read_excel(
            self.team_members_report
        )  # load team members report
        df = pw.cleanup_report_columns(
            df,
            list(self.pw_config["team members report columns"].values()),
            list(self.pw_config["team members report columns"].keys()),
        )
        df = pw.clean_composites(df, set_composite_flag=False)
        df = df[pw.TEAM_MEMBER_COLUMNS]  # make sure they are in order

        df[[pw.COL_ROW_NOVICE, pw.COL_SCULL_NOVICE]] = pw.clean_booleans(
            df[[pw.COL_ROW_NOVICE, pw.COL_SCULL_NOVICE]]
        )
        df[pw.COL_POSITION] = pw.assign_rower_position(df)

        return df

    def load_and_clean_community_members_report(self) -> pd.DataFrame:

        df = pd.read_excel(self.community_members_report)
        df = pw.cleanup_report_columns(
            df,
            list(self.pw_config["community members report columns"].values()),
            list(self.pw_config["community members report columns"].keys()),
        )

        return df


def load_from_yaml(config_path: str) -> Dict:
    """Parses a yaml file and returns a dictionary."""

    with open(config_path, "r") as f:
        return yaml.safe_load(f)


if __name__ == "__main__":

    app = App()
    app.display()
