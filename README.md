# Scottish Rowing Playwaze Entries Report Converter

This web was developed to turn reports from the Scottish Rowing network on [Playwaze](www.playwze.com) into more a user friendly and rowing-ified format.

[Web App](https://share.streamlit.io/adhardy/playwaze-entries-report-converter/src/streamlit_app.py)

The app allows users to view the new reports as data tables within the browser, or download them as csv files.

# Deploying to Streamlit

The app is written using [Streamlit](www.streamlit.io).

A [ready-deployed](https://share.streamlit.io/adhardy/playwaze-entries-report-converter/src/streamlit_app.py) version of the app is available to use. This will always use the most up-to-date code in the master branch.

The app can be easily re-deployed on streamlit. Create an account at [www.streamlit.io](www.streamlit.io) and click the "new app" button. Enter the url of of the repository: https://github.com/adhardy/Playwaze-Entries-Report-Converter. Streamlit will deploy the app for you and it will be available to use within a few minutes.

# Deploying Locally

The app can be run locally. First, prepare your environment:
- Download the repository
- Install Python (3.7+)
- Install [dependancies](requirements.txt)

To run the app:
- Navigate to the directory to which the reporistory was downloaded in a command line terminal.
- Run: "streamlit run src/streamlit_app.py"
- The terminal will give you an IP address to access the app on your local network. Click this link or copy and paste it into your browser.
