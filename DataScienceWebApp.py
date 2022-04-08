
#Data from https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
#if you download the csv file you will have to change the path in order to get the program to run
DATA_URL =("/home/rhyme/Desktop/Project/Motor_Vehicle_Collisions_-_Crashes.csv")
#setting a title for the data science web application
st.title("Motor Vehicle Collisions in New York City")
st.markdown("This application is a Streamlit dashbboard to analyze motor vehicle crashes in NYC")
@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL,nrows=nrows, parse_dates=[["CRASH_DATE","CRASH_TIME"]])
#dropping the misssing values from the location columns because those accidents wont be mapped properly
    data.dropna(subset=['LATITUDE','LONGITUDE'],inplace =True)
#convert the column titles to lowercase to make them easier to work with via lambda function
    lowercase = lambda x: str(x).lower()
#two lines below converts the column titles into lowercase and then changes the long column name to something easier to work with
    data.rename(lowercase, axis = 'columns', inplace=True)
    data.rename(columns ={"crash_date_crash_time" : 'date/time'}, inplace=True)
    return data
#loading a 100,000 rows of data
data = load_data(100000)
original_data= data
st.header("Where are the most people injured in NYC?")
#19 was the highest numer of people of injured in a singular accident
#using the slider function
injured_people= st.slider("number of people injured in vehicle collisions ",0,19)
st.map(data.query("injured_persons >= @injured_people")[['latitude','longitude']].dropna(how='any'))


st.header("how many collisions occur during a given time of day")
#setiing the range over a 24 hour spread
hour= st.slider("Hour to look at", 0,23)
#setting the values in the date/time column to the pandas dt hour function
data= data[data['date/time'].dt.hour == hour]

st.markdown('Vehicle collisions between %i:00 and %i:00' % (hour,( hour+1)%24))
#setting the midpoint
midpoint = (np.average(data["latitude"]), np.average(data["longitude"]))

st.write(pdk.Deck(
#Choose the style of map and initial_view_state
    map_style= "mapbox://styles/mapbox/light-v9",
    initial_view_state =
        {
        "latitude": midpoint[0],
        'longitude': midpoint[1],
        'zoom':11,
#use pitch to control view of 3d plot
        'pitch': 50,},
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data = data[['date/time','latitude', 'longitude']],
        get_position=["longitude", "latitude"],
        radius= 100,
        extruded= True,
        pickable= True,
        elevation_scale=4,
        elevation_range=[0,1000],

        ),
    ],
))

st.subheader("breakdown by minute between %i:00 and %i:00" %(hour, (hour+1)%24))
filtered= data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour+1))
]
hist=np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0,60))[0]
chart_data= pd.DataFrame({'minute': range(60), 'crashes':hist})
fig= px.bar(chart_data ,x='minute',y= 'crashes',hover_data= ['minute', 'crashes'],height=400)
st.write(fig)

st.header("Top 5 dangerous streets by affected type of person")
select= st.selectbox("Affected type of people", ['Pedestrians','Cyclists','Motorists'])

if select== 'Pedestrians':
    st.write(original_data.query('injured_pedestrians >=1')[['on_street_name','injured_pedestrians']].sort_values(by=['injured_pedestrians'],ascending=False).dropna(how='any')[:5])


elif select== 'Cyclists':
    st.write(original_data.query('injured_cyclists >=1')[['on_street_name','injured_cyclists']].sort_values(by=['injured_cyclists'],ascending=False).dropna(how='any')[:5])


else :
    st.write(original_data.query('injured_motorists >=1')[['on_street_name','injured_motorists']].sort_values(by=['injured_motorists'],ascending=False).dropna(how='any')[:5])



if st.checkbox("Show Raw Data", False) :
    st.subheader('Raw Data')
    st.write(data)
