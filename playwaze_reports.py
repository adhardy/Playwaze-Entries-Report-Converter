import pandas as pd
import numpy as np
from typing import List, Union

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
COL_MEMBER_ID =  "member id"
COL_NAME = "name"
COL_GENDER = "gender"
COL_DOB = "dob"
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

TEAM_COLUMNS = [COL_CREW_ID, COL_BOAT_TYPE, COL_CLUB, COL_CREW_NAME, 
    COL_CREW_LETTER, COL_SEATS, COL_VERIFIED, COL_CAPTAIN,COL_CAPTAIN_NAME, COL_COX, COL_COX_NAME]

TEAM_MEMBER_COLUMNS = [COL_BOAT_TYPE, COL_CLUB, COL_CREW_ID, COL_CREW_LETTER, COL_CREW_NAME, COL_MEMBER_ID, 
    COL_NAME, COL_GENDER, COL_DOB, COL_SR_NUMBER, COL_MEMBERSHIP_TYPE,COL_EXPIRY,COL_ROW_POINTS,
    COL_ROW_NOVICE, COL_SCULL_POINTS, COL_SCULL_NOVICE, COL_PRIMARY_CLUB,COL_ADDITIONAL_CLUBS, COL_FIRST_LICENCE,COL_COMPOSITE_CLUBS]

COMMUNITY_MEMBER_COLUMNS = [COL_MEMBER_ID, COL_NAME, COL_DOB, COL_GENDER, COL_SR_NUMBER, 
    COL_MEMBERSHIP_TYPE, COL_EXPIRY, COL_ROW_POINTS, COL_ROW_NOVICE, COL_SCULL_POINTS, COL_SCULL_NOVICE, 
    COL_PRIMARY_CLUB, COL_ADDITIONAL_CLUBS, COL_FIRST_LICENCE, COL_COMPOSITE_CLUBS]

# additional columns we create
COL_POSITION = "position"

# file type of uploaded reports
REPORT_FILE_TYPE = "xlsx"


def cleanup_report_columns(df: pd.DataFrame, column_numbers: List[int], column_names: List[str]) -> pd.DataFrame:

    df = df.iloc[:,column_numbers] # keep only the columns we need
    df.columns = column_names # and rename them to match names in config

    return df


def clean_booleans(df: pd.DataFrame) -> pd.DataFrame:
    """Replaces Y, N and nan with True/False"""

    df = df.replace({"Y":True, np.nan:False, "N":False})
    return df.astype(bool)


def assign_rower_position(df):
    """Assign a unique position (number) to rowers in each crew"""

    df["position"] = df.groupby(COL_CREW_ID).cumcount()
    df["position"] = df["position"] + 1 # index from 1

    return df["position"].astype(str)


def get_coxes(df_teams: pd.DataFrame, df_team_members: pd.DataFrame, df_members: Union[None, pd.DataFrame] = None):
    """Get coxes from a Playwaze teams report, match their details from either a community members or team members report, and insert them into the team members dataframe"""

    # extract all coxes from the teams report
    df_coxes = df_teams.loc[df_teams[COL_COX]==True, [COL_COX_NAME, COL_CREW_ID, COL_CREW_NAME, COL_CREW_LETTER, COL_CLUB, COL_BOAT_TYPE]]
    df_coxes[COL_POSITION] = "C"
    df_coxes = df_coxes.rename(columns={COL_COX_NAME:COL_NAME}) # rename the name column to match the members df
    
    # try and find their membership number if they are entered as a rower in another crew
    # if a community members report is not included, get a list of rowers from the team members report
    if df_members is None:
        df_members = get_unique_rowers(df_team_members)

    # look up cox details from the members report
    df_coxes = pd.merge(
        df_coxes, 
        df_members[[COL_NAME, COL_SR_NUMBER, COL_GENDER, COL_DOB, COL_MEMBERSHIP_TYPE, COL_EXPIRY, COL_PRIMARY_CLUB, COL_ADDITIONAL_CLUBS, COL_FIRST_LICENCE, COL_COMPOSITE_CLUBS, COL_ROW_NOVICE, COL_SCULL_NOVICE, COL_ROW_POINTS, COL_SCULL_POINTS]], 
        left_on=[COL_NAME], 
        right_on=[COL_NAME], 
        how="left")

    # add coxes to the rowers dataframe
    df_team_members = df_team_members.append(df_coxes)

    # somewhere above, membership number gets turned to an interger, convert back to string
    df_team_members[COL_SR_NUMBER] = df_team_members[COL_SR_NUMBER].fillna(0) # remove NANs so can convert to string
    df_team_members[COL_SR_NUMBER] = df_team_members[COL_SR_NUMBER].astype(int).astype(str)
    df_team_members.loc[df_team_members[COL_SR_NUMBER] == "0", COL_SR_NUMBER] = np.nan # convet back to nan

    return df_team_members


def get_unique_rowers(df_team_members: pd.DataFrame):
    """Get a unique list of rowers from a Playwaze team members report"""

    df_unique_members = df_team_members[df_team_members.duplicated(subset=[COL_NAME, COL_SR_NUMBER]) == False]
    return df_unique_members


def count_num_entries(df_teams: pd.DataFrame) -> int:
    """Count the number of entries from a Playwaze teams report."""
    return df_teams[COL_CREW_ID].count()


def count_num_seats(df_teams: pd.DataFrame) -> int:
    """Count the number of seats (excluding coxes, total and filled) from a Playwaze teams report."""
    filled_seats = df_teams[COL_SEATS].sum()
    re_boat = r"([1248])[x\-\+][\+]?"
    total_seats = (df_teams[COL_BOAT_TYPE].str.extract(re_boat).astype(int)).sum()[0]
    return total_seats, filled_seats


def count_unique_rowers(df_team_members: pd.DataFrame) -> int:
    """Count the number of unique rowers and coxes in the event."""

    return df_team_members.loc[df_team_members.duplicated(subset=COL_MEMBER_ID)==False, COL_MEMBER_ID].count()


def get_pivoted_team_members_report(df_team_members: pd.DataFrame) -> pd.DataFrame:
    """Pivot the dataframe so that each row is a crew, and crew members are listed by their position across the row"""

    return df_team_members.pivot(index=[COL_CREW_ID, COL_BOAT_TYPE, COL_CLUB, COL_CREW_LETTER], columns=COL_POSITION, values=COL_NAME).reset_index()


def get_events_report(df_teams: pd.DataFrame) -> pd.DataFrame:
    return (df_teams.groupby(COL_BOAT_TYPE).count())[COL_CREW_ID].rename("Entries")


def get_clubs_report(df_teams: pd.DataFrame, df_team_members: pd.DataFrame) -> pd.DataFrame:

    # count entries by club
    df_entries_by_club_count = (df_teams.groupby(by=COL_CLUB))[COL_CREW_ID].count()

    # count rowers by club. squeeze: force into a series
    df_rowers_by_club_count = (df_team_members[df_team_members.duplicated(subset=COL_SR_NUMBER)==False].sort_values(by=COL_CLUB))[[COL_CLUB, COL_SR_NUMBER]].groupby(COL_CLUB).count().squeeze().rename("rowers") 
    
    #count seats by club
    df_seats_by_club_count = (df_teams.groupby(by=COL_CLUB).sum())[COL_SEATS].rename("seats")


    # merge all the dataframes together
    df = pd.merge(df_entries_by_club_count, df_rowers_by_club_count, left_index=True, right_index=True, how="left")
    df = pd.merge(df, df_seats_by_club_count, left_index=True, right_index=True, how="left")

    return df