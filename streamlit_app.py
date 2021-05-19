import pandas as pd
import streamlit as st


#================= Pre Processing ================================

col_event = "Event"
col_crew_name = "Crew Name"
col_crew_members = "Rowers"
col_verified = "Verified"

#load teams
df_teams = pd.read_excel("Playwaze teams.xlsx")
df_playwaze_teams = df_teams.rename(columns={
    "Entry type":col_event,
    "Entry name":col_crew_name,
    "Number of players": col_crew_members,
    "Is verified":col_verified
    })

#load rowers
df_playwaze_rowers = pd.read_excel("Playwaze team members.xlsx")
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





df_entries = df_playwaze_teams.loc[df_playwaze_teams.duplicated(subset=col_crew_name) == False].sort_values(by=[col_event, col_crew_name])

#extract number of seats
re_boat = r"([1248])[x\-\+][\+]?$"
df_entries["Seats"] = df_entries[col_event].str.extract(re_boat).astype(int)
#extract coxed boats
df_entries["Coxed"] = df_entries[col_event].str.contains(r"\+$").astype(int)
df_entries["Crew Members"] = df_entries["Seats"]

#get eevents & entries
df_events = (df_entries.groupby(col_event).count())[col_crew_members].rename("Entries")

team_display_columns = [col_event, col_crew_name, "Seats", "Coxed", col_verified, col_crew_members, "Crew Members"]
rowers_display_columns = ["Event", "Crew Name", "Position", "Name"]

# df_events = df_playwaze_teams.loc[df_playwaze_teams.duplicated(subset=col_event) == False, col_event]



#================= Web Page ================================

st.title("Scottish Rowing Junior Summer Regatta")

st.header("Entries")
st.write(df_entries[team_display_columns])

st.header("Rowers")
st.write(df_playwaze_rowers[rowers_display_columns].pivot(index=[col_event, col_crew_name], columns="Position", values="Name"))

st.header("Events")
st.write(df_events)