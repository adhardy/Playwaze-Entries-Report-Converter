from typing import List, Dict
import pandas as pd
import streamlit as st
import playwaze_reports as pw
import base64 

ENTRIES_VIEW = "Entries"
CREWS_VIEW = "Crew List"
EVENTS_VIEW = "Events"
CLUBS_VIEW = "Clubs"
ROWERS_VIEW = "Rowers"
COFD_VIEW = "CoFD"

APP_VIEWS = (ENTRIES_VIEW, CREWS_VIEW, EVENTS_VIEW, CLUBS_VIEW, ROWERS_VIEW, COFD_VIEW)

class View():

    def __init__(
        self, 
        view_name: str, 
        df: pd.DataFrame,
        web_hidden_columns: List[str] = [],
        sort_columns: List[str] = [],
        index=None):

        self.view_name = view_name
        self.df = df
        self.index = index
        
        self.web_hidden_columns = web_hidden_columns
        self.sort_columns = sort_columns
        
        self.get_df()
        self.display()


    def get_df(self):

        if self.sort_columns:
            self.df = self.df.sort_values(by=self.sort_columns)
            if self.index is None:
                # if manual index not set, reset the auto-index to match the sorting
                self.df = self.df.reset_index(drop=True)

        if self.index:
            self.df = self.df.set_index(self.index)

        self.df_download = self.df.copy() # copy the dataframe, we don't want to make the below transformations on the downloadable version
        
        if self.web_hidden_columns:
            self.df = self.df.drop(self.web_hidden_columns, axis=1)

        if isinstance(self.df, pd.DataFrame):
            # this only works on Dataframes, not series
            string_columns = self.df.select_dtypes(include=["object"]).columns
            self.df[string_columns] = self.df[string_columns].fillna("") # replace "NA" with a blank string, looks nicer
        

    def display(self):
        self.display_header()
        self.display_header_text()
        self.display_df()
        self.display_downloader()
        self.display_footer()


    def display_header(self):
        st.header(self.view_name.title())


    def display_df(self):
        st.write(self.df)
        

    def display_downloader(self):
        csv_downloader(self.df_download, f"{self.view_name.lower()}.csv")


    def display_header_text(self):
        pass


    def display_footer(self):
        pass

class CrewsListView(View):

    def __init__(
        self, 
        df: pd.DataFrame):

        index=pw.COL_CREW_ID
        sort_columns=[pw.COL_BOAT_TYPE, pw.COL_CREW_NAME]
        web_hidden_columns = None

        super().__init__(
            view_name=CREWS_VIEW, 
            df=df,
            web_hidden_columns=web_hidden_columns,
            sort_columns=sort_columns,
            index=index)


    def display_header_text(self):
        pass

class EntriesView(View):

    def __init__(
        self,
        df: pd.DataFrame,
        stats: Dict = None):

        self.stats = stats
        index = pw.COL_CREW_ID
        web_hidden_columns = [pw.COL_CAPTAIN, pw.COL_CAPTAIN_NAME, pw.COL_COX, pw.COL_CREW_NAME]
        sort_columns=[pw.COL_BOAT_TYPE, pw.COL_CLUB, pw.COL_CREW_LETTER]

        super().__init__(ENTRIES_VIEW, df, web_hidden_columns, sort_columns, index=index)
        

    def display_header_text(self):
        for stat, val in self.stats.items():
            st.write(f"{stat}: {val}")


def csv_downloader(df: pd.DataFrame, filename: str) -> None:
    """Creates a clickable link in streamlit to download the given dataframe as an Excel xlsx file."""

    csvfile = df.to_csv()
    b64 = base64.b64encode(csvfile.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download as CSV</a>'
    st.markdown(href,unsafe_allow_html=True)


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