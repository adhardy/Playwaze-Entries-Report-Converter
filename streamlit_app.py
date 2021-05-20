import pandas as pd
import numpy as np
import streamlit as st
import base64 

st.title("Scottish Rowing Playwaze Entry System Report Converter")

# create csv downloader
def csv_downloader(data, filename):
	csvfile = data.to_csv()
	b64 = base64.b64encode(csvfile.encode()).decode()
	href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download as CSV</a>'
	st.markdown(href,unsafe_allow_html=True)

#================================ Sidebar ================================

view_entries = st.sidebar.selectbox(
    "Select View:",
    ("Entries", "Rowers", "Events", "Clubs")
)

#================================ File Upload ================================

st.sidebar.header("Upload Playwaze Teams Report")


playwaze_teams_file_check = False
playwaze_teams_expected_filename = "Playwaze teams.xlsx"
playwaze_teams_uploaded_file = st.sidebar.file_uploader(f"Upload '{playwaze_teams_expected_filename}'",type=['xlsx'])
if playwaze_teams_uploaded_file is not None:
    playwaze_teams_uploaded_file_details = {"FileName":playwaze_teams_uploaded_file.name,"FileType":playwaze_teams_uploaded_file.type,"FileSize":playwaze_teams_uploaded_file.size}
    if playwaze_teams_uploaded_file_details["FileName"] != playwaze_teams_expected_filename:
        st.error(f"File name must be: '{playwaze_teams_expected_filename}'")
        
        st.stop()
    else:
        playwaze_teams_file_check = True
else:
    st.header("<- Please Upload A Playwaze Teams Report to Continue")
    st.stop()

playwaze_members_file_check = False
playwaze_members_expected_filename = "Playwaze team members.xlsx"
playwaze_members_uploaded_file = st.sidebar.file_uploader(f"Upload '{playwaze_members_expected_filename}'",type=['xlsx'])
if playwaze_members_uploaded_file is not None:
    playwaze_members_uploaded_file_details = {"FileName":playwaze_members_uploaded_file.name,"FileType":playwaze_members_uploaded_file.type,"FileSize":playwaze_members_uploaded_file.size}
    if playwaze_members_uploaded_file_details["FileName"] != playwaze_members_expected_filename:
        st.error(f"File name must be: '{playwaze_members_expected_filename}'")
        st.stop()
    else:
        playwaze_members_file_check = True
else:
    st.header("<- Please Upload A Playwaze Members Report to Continue")
    st.stop()

#================================ Pre Processing ================================

col_event = "Event"
col_crew_name = "Crew Name"
col_crew_members = "Rowers"
col_verified = "Verified"
col_has_cox = "has cox"

#load teams
df_teams = pd.read_excel(playwaze_teams_uploaded_file)
df_playwaze_teams = df_teams.rename(columns={
    "Entry type":col_event,
    "Entry name":col_crew_name,
    "Number of players": col_crew_members,
    "Is verified":col_verified,
    "Is entry cox (if required)":col_has_cox
    })
df_playwaze_teams[col_has_cox] = df_playwaze_teams[col_has_cox].replace({"Y":1, np.nan:0, "N":0})

#load rowers
df_playwaze_rowers = pd.read_excel(playwaze_members_uploaded_file)
df_playwaze_rowers = df_playwaze_rowers.rename(columns={
    "Team":col_crew_name,
    "Team type": col_event
    })

#iterate over rowers in df, assign position to each one
last_team = ""
df_playwaze_rowers["Position"] = int(0)
for i, rower in df_playwaze_rowers.iterrows():
    idx = rower.name
    team = rower[col_crew_name]
    name = rower["Name"]
    if team != last_team:
        position = 1
    df_playwaze_rowers.loc[idx, "Position"] = position
    position += 1
    last_team = team

#extract coxes from teams report
df_coxes = df_playwaze_teams.loc[df_playwaze_teams[col_has_cox] == "Y", ["Name", col_crew_name, col_event]]
df_coxes["Position"] = "C"
#add to rowers dataframe
df_playwaze_rowers = df_playwaze_rowers.append(df_coxes, ignore_index=True)
df_playwaze_rowers = df_playwaze_rowers.sort_values(by=["Event", "Crew Name", "Position"])
#count number of unique athletes
num_rowers = df_playwaze_rowers.loc[df_playwaze_rowers.duplicated(subset="MembershipNumber")==False, "MembershipNumber"].count()

#get rid of duplicate crew names
df_entries = df_playwaze_teams.loc[df_playwaze_teams.duplicated(subset=col_crew_name) == False].sort_values(by=[col_event, col_crew_name, col_has_cox])
num_entries = df_entries["Entry Id"].count()

#extract number of seats
re_boat = r"([1248])[x\-\+][\+]?$"
df_entries["Seats"] = df_entries[col_event].str.extract(re_boat).astype(int)
#extract coxed boats
df_entries["Coxed"] = df_entries[col_event].str.contains(r"\+$").astype(int)
# df_entries["Crew Members"] = df_entries["Seats"] #add in coxes eventually
df_entries["Missing Rowers"] = df_entries["Seats"] - df_entries[col_crew_members]

#find missing coxes
df_entries["Missing Cox"] = df_entries[col_has_cox] != df_entries["Coxed"]

#count steats
num_seats = df_entries["Seats"].sum()

#get events & entries
df_events = (df_entries.groupby(col_event).count())[col_crew_members].rename("Entries")

#set columns to display
team_display_columns = [col_event, col_crew_name, "Seats", "Coxed", col_verified, col_crew_members, "Missing Rowers", col_has_cox, "Missing Cox"]
rowers_display_columns = ["Event", "Crew Name", "Position", "Name"]

#================= Main Page ================================


if view_entries == "Entries":
    st.header("Entries")
    st.write(f"Number of Entries: {num_entries}")

    show_unverified = st.checkbox('Show Un-verified crews only')
    if show_unverified:
        df = df_entries.loc[df_entries[col_verified] == "N", team_display_columns]
    else:
        df = df_entries[team_display_columns]

    st.write(f"Number of Seats: {num_seats}")
    st.write(df)
    csv_downloader(df, "entries.csv")

elif view_entries == "Rowers":
    st.header("Rowers")
    st.write(f"Number of Rowers (unique): {num_rowers}")
    df = df_playwaze_rowers[rowers_display_columns].pivot(index=[col_event, col_crew_name], columns="Position", values="Name")
    st.write(df)
    csv_downloader(df, "rowers.csv")

elif view_entries == "Events":
    st.header("Events")
    df = df_events
    st.write(df)
    csv_downloader(df, "events.csv")

elif view_entries == "Clubs":
    st.header("Individuals Per Club")
    df = df_playwaze_rowers.loc[df_playwaze_rowers.duplicated(subset="MembershipNumber")==False, ["Club", "MembershipNumber"]].groupby("Club").count()
    st.write(df)
    csv_downloader(df, "rowers_per_club.csv")

