import pandas as pd
import streamlit as st
import base64 

st.title("Scottish Rowing Playwaze Entry System Report Converter")

# create csv downloader
def csv_downloader(data, filename):
	csvfile = data.to_csv()
	b64 = base64.b64encode(csvfile.encode()).decode()
	href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download as CSV</a>'
	st.markdown(href,unsafe_allow_html=True)

#================================ File Upload ================================

st.header("Upload Playwaze Teams Report")

playwaze_teams_expected_filename = "Playwaze teams.xlsx"
playwaze_teams_uploaded_file = st.file_uploader(f"Upload {playwaze_teams_expected_filename}",type=['xlsx'])
if playwaze_teams_uploaded_file is not None:
    file_details = {"FileName":playwaze_teams_uploaded_file.name,"FileType":playwaze_teams_uploaded_file.type,"FileSize":playwaze_teams_uploaded_file.size}
    if file_details["FileName"] != playwaze_teams_expected_filename:
        st.error(f"File name must be: '{playwaze_teams_expected_filename}'")
        st.stop()
else:
    st.stop()

st.header("Upload Playwaze Team Members Report")

playwaze_members_expected_filename = "Playwaze team members.xlsx"
playwaze_members_uploaded_file = st.file_uploader("Upload Playwaze Members File",type=['xlsx'])
if playwaze_members_uploaded_file is not None:
    file_details = {"FileName":playwaze_members_uploaded_file.name,"FileType":playwaze_members_uploaded_file.type,"FileSize":playwaze_members_uploaded_file.size}
    if file_details["FileName"] != playwaze_members_expected_filename:
        st.error(f"File name must be: '{playwaze_members_expected_filename}'")
        st.stop()
else:
    st.stop()

#================================ Pre Processing ================================

col_event = "Event"
col_crew_name = "Crew Name"
col_crew_members = "Rowers"
col_verified = "Verified"

#load teams
df_teams = pd.read_excel(playwaze_teams_uploaded_file)
df_playwaze_teams = df_teams.rename(columns={
    "Entry type":col_event,
    "Entry name":col_crew_name,
    "Number of players": col_crew_members,
    "Is verified":col_verified
    })

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

df_coxes = df_playwaze_teams.loc[df_playwaze_teams["Is entry cox (if required)"] == "Y", ["Name", col_crew_name, col_event]]
df_coxes["Position"] = "C"
df_playwaze_rowers = df_playwaze_rowers.append(df_coxes, ignore_index=True)
df_playwaze_rowers = df_playwaze_rowers.sort_values(by=["Event", "Crew Name", "Position"])


num_rowers = df_playwaze_rowers.loc[df_playwaze_rowers.duplicated(subset="MembershipNumber")==False, "MembershipNumber"].count()
df_entries = df_playwaze_teams.loc[df_playwaze_teams.duplicated(subset=col_crew_name) == False].sort_values(by=[col_event, col_crew_name])
num_entries = df_entries["Entry Id"].count()


#extract number of seats
re_boat = r"([1248])[x\-\+][\+]?$"
df_entries["Seats"] = df_entries[col_event].str.extract(re_boat).astype(int)
#extract coxed boats
df_entries["Coxed"] = df_entries[col_event].str.contains(r"\+$").astype(int)
df_entries["Crew Members"] = df_entries["Seats"]

num_seats = df_entries["Seats"].sum()

#get eevents & entries
df_events = (df_entries.groupby(col_event).count())[col_crew_members].rename("Entries")

team_display_columns = [col_event, col_crew_name, "Seats", "Coxed", col_verified, col_crew_members, "Crew Members"]
rowers_display_columns = ["Event", "Crew Name", "Position", "Name"]

# df_events = df_playwaze_teams.loc[df_playwaze_teams.duplicated(subset=col_event) == False, col_event]



#================= Web Page ================================

st.header("Entries")
st.write(f"Number of Entries: {num_entries}")
st.write(f"Number of Seats: {num_seats}")
df = df_entries[team_display_columns]
st.write(df)
csv_downloader(df, "entries.csv")

st.header("Rowers")
st.write(f"Number of Rowers (unique): {num_rowers}")
df = df_playwaze_rowers[rowers_display_columns].pivot(index=[col_event, col_crew_name], columns="Position", values="Name")
st.write(df)
csv_downloader(df, "rowers.csv")

st.header("Events")
df = df_events
st.write(df)
csv_downloader(df, "events.csv")