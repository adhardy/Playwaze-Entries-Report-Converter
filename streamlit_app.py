import pandas as pd
import numpy as np
import streamlit as st


#================================ Configuration ================================

# st.set_page_config(layout="wide") #set to wide mode
# # st.image("images/2.1.png", width=300)
# # st.title("Playwaze Entry System Report Converter")

# str_team = "Boat"

# # Create variable names for all the report columns - allows flexibility as columns names can be changed in playwaze. TODO: break this out into a config file
# col_event = "Event"
# col_crew_name = "Crew Name"
# col_crew_members = "Rowers"
# col_verified = "Verified"
# col_has_cox = "has cox"
# col_club = "Club"
# col_primary_club = "PrimaryClub"
# col_crew_id = "Team Id"
# col_entry_id = f"{str_team} Id"

# # variables for internal columns
# col_composite = "Composite"
# col_entering_club = "EnteringClub"



#================================ Sidebar ================================

# st.sidebar.header("Select View:")
# view_entries = st.sidebar.selectbox(
#     "",
#     ("Entries", "Crews", "Events", "Clubs", "Rowers", "CofD")
)

#================================ File Upload ================================





#================================ Pre Processing ================================

# load teams report
# df_teams = pd.read_excel(playwaze_teams_uploaded_file)
# df_playwaze_teams = df_teams.rename(columns={
#     f"{str_team} type":col_event,
#     f"{str_team} name":col_crew_name,
#     "Number of players": col_crew_members,
#     "Is verified":col_verified,
#     "Cox (if required)":col_has_cox
#     })
# refactor data in cox colu,
# df_playwaze_teams[col_has_cox] = df_playwaze_teams[col_has_cox].replace({"Y":True, np.nan:False, "N":False})
# change the entry ids so the column name and values match the crew id from the members report
# df_playwaze_teams[col_entry_id] = df_playwaze_teams[col_entry_id].str.replace("teams/", "", regex=True)
# df_playwaze_teams.rename(columns = {col_entry_id: col_crew_id}, inplace=True)

# load rowers report
# df_playwaze_rowers = pd.read_excel(playwaze_members_uploaded_file)
# df_playwaze_rowers = df_playwaze_rowers.rename(columns={
#     "Team":col_crew_name,
#     "Team type": col_event
#     })

# assign a position to rowers
# df_playwaze_rowers["Position"] = df_playwaze_rowers.groupby('Crew Name').cumcount()
# df_playwaze_rowers["Position"] = df_playwaze_rowers["Position"] + 1

# extract coxes from teams report
# df_coxes = df_playwaze_teams.loc[df_playwaze_teams[col_has_cox] == 1, ["Cox (if required) Name", col_crew_name, col_event, "Club", col_crew_id]]
# df_coxes = df_coxes.rename(columns={"Cox (if required) Name": "Name"})
# df_coxes["Position"] = "C"

# add membership number to cox if they already exist in the members data
# create a de-duplicated df of individuals and membership numbers. TODO: optional import of Azolve report to make sure we get everyone
# df_members = df_playwaze_rowers[df_playwaze_rowers.duplicated(subset=["Name", "MembershipNumber"]) == False]

# # lookup coxed in the members dataframe and assing memberhip number of they have one
# df_coxes = pd.merge(df_coxes, df_members[["Name", "MembershipNumber"]], left_on=["Name"], right_on=["Name"], how="left")
# #add these to the rowers dataframe
# df_playwaze_rowers = df_playwaze_rowers.append(df_coxes, ignore_index=True)
# # count number of unique athletes
# # de-duplicate on name because some coxes won't have an ID, not ideal if people have the same name - TODO: add in more columns to de-dupe on - DOB would be good
# num_rowers = df_playwaze_rowers.loc[df_playwaze_rowers.duplicated(subset="Name")==False, "Name"].count()

#=============================== Playwaze Bug Workaround: Some Team Types blank in Teams Report
# events = []

# clubs = df_playwaze_teams[col_club].unique() # get list of clubs
# replace_dict = dict.fromkeys(clubs, "") # create dictionary to relace club name with an empty string

# df_playwaze_teams[col_event] = df_playwaze_teams[col_crew_name].replace(replace_dict, regex=True) # remove club name by replacing with empty strings
# df_playwaze_teams[col_event] = df_playwaze_teams[col_event].replace("\(composite\) ", "", regex=True) # remove (composite) as the club list/regex sometimes leave this dependingon list order
# df_playwaze_teams[col_event] = df_playwaze_teams[col_event].str.strip()
# df_playwaze_teams[col_event] = df_playwaze_teams[col_event].str[:-2]

#================================ Composite Crews ================================
# where a crew is a composite, remove the composite suffix from the club name, add a composite column
df_playwaze_teams[col_composite] = False
df_playwaze_teams[col_composite] = df_playwaze_teams[col_composite].mask(df_playwaze_teams[col_club].str.contains("(composite)"),True)
df_playwaze_teams[col_club] = df_playwaze_teams[col_club].str.replace(" \(composite\)", "", regex=True)

df_playwaze_rowers[col_composite] = False
df_playwaze_rowers[col_composite] = df_playwaze_rowers[col_composite].mask(df_playwaze_rowers[col_club].str.contains("(composite)"),True)
df_playwaze_rowers[col_club] = df_playwaze_rowers[col_club].str.replace(" \(composite\)", "", regex=True)

# create an "col_entering_club" column
df_playwaze_rowers[col_entering_club] = df_playwaze_rowers[col_club]
# where a rower in a composite crew - put them with their Primary Club
df_playwaze_rowers[col_club] = df_playwaze_rowers[col_club].where(df_playwaze_rowers[col_composite]==False, df_playwaze_rowers[col_primary_club])

# # get rid of duplicate crew names: this can happen if a crew has a cox and captain assigned
# df_entries = df_playwaze_teams.loc[df_playwaze_teams.duplicated(subset=col_crew_name) == False].sort_values(by=[col_event, col_crew_name, col_has_cox])
# num_entries = df_entries[col_crew_id].count()

# extract number of seats for each crew
# re_boat = r"([1248])[x\-\+][\+]?"
# df_entries["Seats"] = df_entries[col_event].str.extract(re_boat)#.astype(int)

# # extract coxed boats
# df_entries["Coxed"] = df_entries[col_event].str.contains(r"\+$").astype(int)

# # calculate number of rowers missing
# df_entries["Seats"] = df_entries["Seats"].astype(int)
# df_entries["Missing Rowers"] = df_entries["Seats"] - df_entries[col_crew_members].astype(int)

# find missing coxes
df_entries["Missing Cox"] = df_entries[col_has_cox] != df_entries["Coxed"]

# count total steats (excl. coxes)
# TODO: caculate this including and excluding coxes
# num_seats = df_entries["Seats"].sum()

# get events & entries
df_events = (df_entries.groupby(col_event).count())[col_crew_members].rename("Entries")


rowers_display_columns = ["Event", "Crew Name", "Club", "Position", "Name"]

df_entries_by_club_count = (df_entries.groupby(by="Club").count())[col_crew_id].rename("Entries")
clubs_list = df_entries_by_club_count.index.tolist() #get list of clubs

#================= Main Page ================================

#================= Entries ================================

# if view_entries == "Entries":
    # st.header("Entries")
    # st.write(f"Number of Entries: {num_entries}")
    # st.write(f"Number of Seats: {num_seats}")
    # st.write(f"Number of Rowers (unique): {num_rowers}")

    # entries_filter = st.selectbox(
    #         "Filter:",
    #         ("None", "Unverified Crews", "Missing Coxes")
    #     )

    # # set columns to display
    # team_display_columns = [col_event, col_crew_name, "Seats", "Coxed", col_verified, col_crew_members, "Missing Rowers", col_has_cox, "Missing Cox", "Club"]

    if entries_filter == "Unverified Crews":
        df = df_entries.loc[df_entries[col_verified] == "N", team_display_columns]
    elif entries_filter == "Missing Coxes":
        df = df_entries.loc[df_entries["Missing Cox"] == 1,team_display_columns]
    else:
    #     df = df_entries[team_display_columns]

    # st.write(df)
    # csv_downloader(df, "entries.csv")

#================= Crews ================================

elif view_entries == "Crews":
    
    # st.header("Crews")
    
    # club_filter = st.selectbox("Filter by club:", ["All"] + clubs_list)
    # member_info = st.selectbox("Display:", ["Name", "MembershipNumber"])

    # # set columns to display
    # rowers_display_cols = ["Event", "Crew Name", "Club", "Position", member_info]
	
    # df_playwaze_rowers = df_playwaze_rowers.sort_values(by=[col_event, col_crew_name, "Club"])
    
    # # pivot the dataframe so that each row is a crew, and crew members are listed by their position across the row
    # df = df_playwaze_rowers[rowers_display_cols].pivot(index=[col_event, col_crew_name, "Club"], columns="Position", values=member_info).reset_index()
    
    # add in crews that don't have any rowers
    # get the crew lists from both tables
    df_members_crews = df_playwaze_rowers[["Crew Name", "Event", "Club"]]
    df_members_crews = df_members_crews[df_members_crews.duplicated(subset="Crew Name") == False]

    # find crews in entries that aren't in members (ie.e crew that have noone entered in them)
    # hacky - concat both lists so we can use np.setdiff1d and then split them again, assign a combo of characters that is very unlikely to appear in an actual crew name
    split_string = "|+_*&" 
    df_all_crews = df_entries[col_event] + split_string + df_entries[col_crew_name] + split_string + df_entries["Club"]
    df_members_crews = df_members_crews["Event"] + split_string +  df_members_crews["Crew Name"] + split_string + df_members_crews["Club"]

    np_missing_crews = np.setdiff1d(df_all_crews, df_members_crews)
    np_missing_crews = [s.split(split_string) for s in np_missing_crews]

    # reconstruct a dataframe from the contatenated data
    df_missing_crews = pd.DataFrame()   
    df_missing_crews["Event"] = [ x[0] for x in np_missing_crews ]
    df_missing_crews["Crew Name"] = [ x[1] for x in np_missing_crews ]
    df_missing_crews["Club"] = [ x[2] for x in np_missing_crews ]

    # add the missing crews to the crews dataframe
    df = df.append(df_missing_crews, ignore_index=True).sort_values(by=["Event", "Crew Name"]).reset_index(drop=True)

    # replace nan
    df = df.replace(np.nan, '', regex=True)

    if club_filter != "All":
        df = df[df["Club"] == club_filter]

    # st.write(df)
    # csv_downloader(df, "crews.csv")

#================= Events ================================

# elif view_entries == "Events":
#     st.header("Events")
#     df = df_events
#     st.write(df)
#     csv_downloader(df, "events.csv")

#================= Clubs ================================

elif view_entries == "Clubs":

    st.header("Clubs")

    # put all composite and end of list so that individual rowers will appear next to their actual club (if they are in a crew from their club)
    club_sorter = sorted(clubs_list)
    for club in club_sorter:
        if "(composite)" in club:
            club_sorter.remove(club)
            club_sorter.append(club)

    #convert club to categorical variable for easy sorting
    df_playwaze_rowers["Club"] = df_playwaze_rowers["Club"].astype("category")
    df_playwaze_rowers["Club"].cat.set_categories(club_sorter, inplace=True)

    #sort by puts composite crews 
    df_rowers_by_club_count = (df_playwaze_rowers.loc[df_playwaze_rowers.sort_values(by="Club").duplicated(subset="MembershipNumber")==False, ["Club", "MembershipNumber"]]).groupby("Club").count().squeeze().rename("Rowers") #squeeze: force convert to series

    #convert back to text as Streamlit can't handle categorical columns
    df_playwaze_rowers["Club"] = df_playwaze_rowers["Club"].astype(str)

    #seats per club
    df_seats_by_club_count = (df_entries.groupby(by="Club").sum())["Seats"].rename("Seats")

    df = pd.merge(df_entries_by_club_count, df_rowers_by_club_count, left_index=True, right_index=True, how="left")
    df = pd.merge(df, df_seats_by_club_count, left_index=True, right_index=True, how="left")
    st.write(df)
    csv_downloader(df, "clubs.csv")

    ########### list of rowers per club ################
    
    # get the club name from the filter box
    club_filter = st.selectbox("Filter by club:", ["All"] + clubs_list)

    # subset columns and de-duplicate
    df = df_playwaze_rowers[["MembershipNumber", "Name", "Club"]]
    df = df[df.duplicated()==False].sort_values(by="Name")

    # select all the rowers from that club
    if club_filter != "All":
        df = df[df["Club"] == club_filter].drop("Club", axis=1)
        
    st.write(df)
    csv_downloader(df, "clubs.csv")


elif view_entries == "Rowers":
    st.header("Rowers")
    df = df_playwaze_rowers[["MembershipNumber", "Name", "Crew Name", "Club"]]
    df['idx'] = df.groupby('Name').cumcount()
    df = df.pivot(index=["MembershipNumber", "Name", "Club"], values="Crew Name", columns="idx").reset_index()

    club_filter = st.selectbox("Filter by club:", ["All"] + clubs_list)

    sort_by = st.selectbox("Sort by:", ["Name", "Club", "Membership Number"])
    if club_filter != "All":
        df = df[df["Club"] == club_filter]

    df = df.sort_values(by=sort_by)

    st.write(df)
    csv_downloader(df, "rowers.csv")

elif view_entries == "CofD":
    st.header("CofD")

    

    df = df_playwaze_rowers[["Event", col_entering_club, "Club", "Name", "MembershipNumber", "Position", "Team Id"]]
    df = df.sort_values(by=col_entering_club)
    st.write(df)
    df[["First Name", "Surname"]] = df["Name"].str.split(" ",1, expand=True) # seperate first name and surname
    df = df.drop("Name", axis=1)

    # get crew letter - where we have brought in coxes, they do not have a crew letter so we extract it from the crew name
    df["Team Letter"] = df_playwaze_rowers["Team Letter"].where(df_playwaze_rowers["Team Letter"].notna(), df_playwaze_rowers["Crew Name"].str[-1])

    # calulate age
    # age on day of event (user input, default to today)
    # junior age (age 1st september preceding event)
    # masters age (age on 31st December of year of event)

    # if junior age < 18 (or 17? <=? check): rowing age = junior age
    # elif masters age >= 27: rowing age = masters age
    # else rowing age = age


    st.write(df)
    # csv_downloader(df, "rowers.csv")
