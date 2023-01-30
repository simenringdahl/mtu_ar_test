import streamlit as st
import pandas as pd
import plotly.express as px  # pip install plotly-express
import plotly.graph_objects as go
# from skimage import data

from config import kilnstops_times, cumulative_storage

# --- Use local CSS:
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style", unsafe_allow_html=True)

# --- TITLE
st.set_page_config(page_title='Kilnstops explorer')
st.title('Kilnstops explorer')
st.subheader('Feed me with your excel sheet')

local_css("style/style.css")

streamlit_style = """
			<style>
			@import url('https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,700;1,300&display=swap');

			html, body, [class*="css"]  {
			font-family: 'Roboto', sans-serif;
			}
			</style>
			"""
st.markdown(streamlit_style, unsafe_allow_html=True)


# --- UPLOAD FILE
uploaded_file = st.file_uploader('Choose a file to explore.', type='xlsx')
if uploaded_file:
    st.markdown('----')
    df_kilnstops = kilnstops_times(uploaded_file)
    # st.dataframe(df_kilnstops)
    initial_storage = st.number_input('Initial level', min_value=0, max_value=1000, value=150)
    loading_upon_stop = st.slider('Loading when kilnstop', value=-1.0, min_value=-10.0, max_value=0.0, step=0.1)
    # loading_upon_running = 1
    loading_upon_running = st.slider('Loading when running', value=1.0, min_value=0.0, max_value=10.0, step=0.1)
    df_storage = cumulative_storage(df_kilnstops, initial_storage, loading_upon_running, loading_upon_stop)
    
    window = st.slider('Green bar selection', value=0, min_value=0, max_value=495)
    fig = px.line(df_storage, labels={"timestamp":"Time", "value":"Storage"})
    for i in range(window,window+20):
        fig.add_vrect(x0=df_kilnstops['date'].tolist()[i], x1=df_kilnstops['end_date'].tolist()[i], fillcolor="green", opacity=0.25, line_width=0)
    st.plotly_chart(fig)




