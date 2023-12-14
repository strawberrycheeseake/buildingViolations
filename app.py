""" 
Name:       Joakim Tronstad 
CS230:      Section 2 
Data:       boston_building_violations_7000_sample.csv 
URL:        Link to your web application on Streamlit Cloud (if posted)  

 
Description:     
 
This program ... (a few sentences about your program and the queries and charts) 
""" 

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import pydeck as pdk
from datetime import datetime

# Reading the data into a DataFrame and cleaning it for rows with relevant data missing
dfBuildingViolations = pd.read_csv("boston_building_violations_7000_sample.csv", index_col="case_no")

csv_columns = [col for col in dfBuildingViolations.columns if col not in ["value", "violation_sthigh", "contact_addr2"]]

dfBuildingViolations = dfBuildingViolations.dropna(subset=csv_columns)

# Function for creating and plotting map of all building violations with streamlit (used 'https://pydeck.gl/' to learn about streamlit maps)
def longitude_latitude(df):
    columns = ["description", "violation_street", "violation_suffix", "violation_city", "violation_zip", "violation_state", "latitude", "longitude", "status"] # columns relevant for plotting the map
    dfMap = df.loc[:, columns] # creating df with the map columns
    dfMap = dfMap.dropna(subset=columns) # cleaning map df

    # viewstate of the map
    view_BuildingViolations = pdk.ViewState(
        latitude = dfMap["latitude"].mean(),
        longitude = dfMap["longitude"].mean(),
        zoom = 10.5,
        pitch = 0
    )
    
    # plotting datapoints on map
    layer1 = pdk.Layer(
        "ScatterplotLayer",
        data = dfMap,
        get_position = "[longitude, latitude]",
        get_radius = 25,
        auto_highlight = True,
        get_color = [186, 85, 211],
        pickable = True
    )

    # tooltip when hovering over datapoints
    tool_tip = {"html": 
                "Building Street: <b>{violation_street}, {violation_suffix}</b></br>"
                "Building City: <b>{violation_city}</b></br>"
                "Building Zip: <b>{violation_zip}</b></br>"
                "Building State: <b>{violation_state}</b><br/>"
                "Violation Description: <b>{description}<b></br>"
                "Status: <b>{status}<b></br>",
                "style": {"backgroundColor": "steelblue",
                          "color": "white"}
    }

    # creating map
    violationsMар = pdk.Deck(
        map_style = "dark",
        initial_view_state = view_BuildingViolations,
        layers=layer1,
        tooltip=tool_tip
    )

    # plotting map with streamlit
    st.pydeck_chart(violationsMар)

# Function to sort by date
def sort_by_date(df):
    # initiate empty lists for new columns "date" and "time"
    date = []
    time = []

    # creating df including only the "status_dttm" column
    columns = ["status_dttm"]
    dfDateTime = df.loc[:, columns]

    # for loop for splitting each date-time couple into a date and a time and appending to respective "date" and "time" lists
    for case_no, row in dfDateTime.iterrows():
        try:
            date_time = row.status_dttm.split()
            date.append(date_time[0])
            time.append(date_time[1])
        except:
            date.append(None)
            time.append(None)

    # adding "date" and "time" column to dfBuildingViolations with data from "date" and "time" lists
    df["date"] = date
    df["time"] = time

    # cleaning new columns "date" and "time"
    date_columns = ["date", "time"]
    df = df.dropna(subset=date_columns)

    # converting "date" column into datetime format
    df["date"] = pd.to_datetime(df["date"])

    # sorting df by "date" column in decending order
    df = df.sort_values("date", ascending=False)

    return df

# make a list of all unique cities
def cities(df, column="violation_city"):
    cities = df[column].unique().tolist()

    return cities

# filter by city, write dataframe, and plot graph
def filterByCity(cities):
    st.header(":blue[Building Violations by City]", divider="blue")
    # creates selectbox with all unique city names
    city = st.selectbox(
        "Select a City:",
        cities)

    st.write('Building Violations in', city + ":") # write dataframe header

    # select column headers and locate rows containing the selected city
    dfCity = dfBuildingViolations.loc[:, ["date", "status", "description", "violation_street", "violation_suffix", "violation_city", "violation_state", "violation_zip", "contact_addr1", "contact_city", "contact_state", "contact_zip", "longitude", "latitude"]]
    dfCity = dfCity.loc[dfCity["violation_city"] == city]

    # sort dataframe by date
    dfCity["date"] = pd.to_datetime(dfCity["date"]).dt.date
    dfCity = dfCity.sort_values("date", ascending=False)

    longitude_latitude(dfCity)

    st.dataframe(dfCity) # write dataframe to streamlit ui

# function to create and display pie chart (used 'https://discuss.streamlit.io/t/how-to-draw-pie-chart-with-matplotlib-pyplot/13967/2' to develop streamlit pie chart)
def pieChart(df):
    cityCounts = df.groupby("violation_city").size().reset_index(name="count") # count rows per city

    max_value = cityCounts["count"].max()

    # find the index of the row with the highest number of violations
    index_of_max_val = cityCounts.index[cityCounts["count"] == max_value][0]

    # set explode to 0.1 for the violation_city with the most violations
    explode = [0]*cityCounts.shape[0]
    explode[index_of_max_val] = 0.1

    # create a pie chart using matplotlib
    fig, ax = plt.subplots()
    pie_chart = ax.pie(cityCounts["count"], labels=cityCounts["violation_city"], labeldistance=1.1, autopct="%1.0f%%", shadow = True, pctdistance=0.75, startangle=90, explode=explode)

    # Set the font size of the labels
    for text in pie_chart[1]:  # pie_chart[1] contains the label texts
        text.set_fontsize(6)  # Adjust the font size as needed
    
    for text in pie_chart[2]:
        text.set_fontsize(8)

    ax.axis("equal")  # equal aspect ratio ensures that the pie chart is circular

    # plot the pie chart in streamlit
    st.header(":blue[Pie Chart Representing Violations per City]", divider="blue")
    st.pyplot(fig)

# functuon to cerate a datetime slider plus accompanying data (used 'https://ecoagi.ai/topics/Python/streamlit-datetime-slider' to learn about datetime sliders)
def slider(df):
    st.header(":blue[Building Violations Over Time]", divider="blue")

    # Create slider for date
    start_time, end_time = st.slider(
        "Specify time interval:",
        datetime(2010, 1, 1), datetime(2024, 1, 1),
        value=(datetime(2014, 1, 1), datetime(2020, 1, 1)),
        format="MM/DD/YY")

    # Filter DataFrame based on the selected date range
    filtered_df = df[(pd.to_datetime(df["date"]) >= pd.to_datetime(start_time)) & (pd.to_datetime(df["date"]) <= pd.to_datetime(end_time))]
    filtered_df = filtered_df.loc[:, ["date", "status", "description", "violation_street", "violation_suffix", "violation_city", "violation_state", "violation_zip", "contact_addr1", "contact_city", "contact_state", "contact_zip"]]

    # Sort dataframe by Date as default
    filtered_df["date"] = pd.to_datetime(filtered_df["date"]).dt.date
    filtered_df = filtered_df.sort_values("date", ascending=False)

    filtered_df_chart = filtered_df.groupby("violation_city").size().reset_index(name="count")

    st.write('Building Violations Within Specified Time Interval:')

    # plot bar chart based on slider
    st.bar_chart(filtered_df_chart.set_index("violation_city")) # plot barchart with cities on x-axis and number of violations on y-axis

    # Display the filtered DataFrame
    st.dataframe(filtered_df)

def open_close(df):    
    # initialize an empty dictionary to store the city-status counts
    statusCity = {}

    # iterate over the DataFrame
    for case_no, row in df.iterrows():
        city = row.violation_city
        status = row.status
        
        # use setdefault to initialize the inner dictionary for the city if it doesn't exist
        statusCity.setdefault(city, {}).setdefault(status, 0)
        
        # increment the count for the status in the inner dictionary
        statusCity[city][status] += 1

    dfStatusPerCity = pd.DataFrame(statusCity)
    dfStatusPerCity = dfStatusPerCity.transpose()

    # plot a stacked bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    dfStatusPerCity.plot(kind='bar', stacked=True, ax=ax)

    # set labels and title
    ax.set_xlabel("City")
    ax.set_ylabel("Count")
    ax.set_title("Stacked Bar Chart of Status Counts by City")

    # display the legend
    ax.legend(title="Status")

    st.header(":blue[Closed v. Open Cases]", divider="blue")
    # plot the stacked bar chart in Streamlit
    st.pyplot(fig)

def map():
    filter = st.radio(
    "Filter to see Open, Closed, or All Cases",
    ["All", "Open", "Closed"],
    captions = ["All cases recorded.", "All cases which remain ongoing.", "All past cases whcih are now closed."])

    if filter == "Open":
        df = dfBuildingViolations.loc[dfBuildingViolations["status"] == "Open"]
    elif filter == "Closed":
        df = dfBuildingViolations.loc[dfBuildingViolations["status"] == "Closed"]
    else:
        df = dfBuildingViolations
    
    longitude_latitude(df)

def main():
    st.title("Building Violation Data for the Boston Area")
    st.image("boston.jpg")

    # start by sorting dataframe by date
    sort_by_date(dfBuildingViolations)

    # plot map of all violations
    st.header(":blue[Map of Builiding Violations in Boston]", divider="blue")
    map()

    # plot chart showing open and closed cases
    open_close(dfBuildingViolations)

    # plot pie chart with all violations as percentages
    pieChart(dfBuildingViolations)

    # plot chart with violations based on user input
    filterByCity(cities(dfBuildingViolations))

    # plot slider and accompanying information based on slider
    slider(dfBuildingViolations)

main()
# if __name__ == "__main__":
#     main()
