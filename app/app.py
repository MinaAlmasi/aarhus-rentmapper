'''
Streamlit app for visualising district and street data in Aarhus.
Link to app: https://aarhus-rentmap.streamlit.app/.

To run app locally, type:
    streamlit run app/app.py

by Anton Drasbæk Schiønning (@drasbaek) and Mina Almasi (@MinaAlmasi)
Spatial Analytics, Cultural Data Science (F2023)
'''

# utils 
import pathlib

# web app
import streamlit as st

# add logo 
from PIL import Image

# sys append to make street view work with custom modules
import sys
sys.path.append(str(pathlib.Path(__file__).parents[1] / "src"))

# import district and street view functions
from district_view import district_view
from street_view import street_view

def add_logo(path: pathlib.Path):
    '''
    Function for adding logo to streamlit app.

    Args: 
        path: Path to script
    '''
    # add padding to top and bottom
    st.write('<style>div.block-container{padding-top:1.8rem;padding-bottom:0.2}</style>', unsafe_allow_html=True)

    # load logo
    logo = Image.open(path.parents[0] / "assets" / "app-logo.png")

    # create columns to center image 
    left, center, right = st.columns([0.5, 1, 0.5])
    
    # plot img in center
    with center: 
        st.image(logo, width=470)

    # add grey border with specific padding
    st.markdown("""<hr style="height:1px;border:none;background-color:#778899;margin:0;" />""",unsafe_allow_html=True)


def add_sidebar(path: pathlib.Path):
    '''
    Function for adding sidebar to streamlit app.

    Args:   
        path: Path to script

    Returns:
        view: View selected in "view selector"
    '''
    with st.sidebar:
        
        # remove padding from top and bottom
        st.write('<style>div.block-container{padding-top:0rem;padding-bottom:0}</style>', unsafe_allow_html=True)

        # set width of sidebar 
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"][aria-expanded="true"]{
                min-width: 250px; 
                max-width: 250px;
            }
            """,
        unsafe_allow_html=True,
        )   
        
        # add view selector
        view = st.radio("Select view", options=("District", "Street"))
        
        # set font size of "Select view" heading
        st.markdown(
            """<style>
        div[class*="stRadio"] > label > div[data-testid="stMarkdownContainer"] > p {
            font-size: 25px;
        }
            </style>
            """, unsafe_allow_html=True)

        return view


def main():
    # define paths
    path = pathlib.Path(__file__)

    # add favicon, define page width and set page title
    favicon = Image.open(path.parents[0] / "assets" / "favicon.ico")
    st.set_page_config(page_title="rentmapper", page_icon=favicon, layout="wide")

    # add logo
    add_logo(path)
    
    # add sidebar and obtain view selection
    view = add_sidebar(path)

    # run view based on selection in "view selector"
    if view == "District":
        district_view(path)
    
    if view == 'Street':
        street_view(path)
    
    with st.sidebar:
        # add white space
        st.markdown("<br>" * 11, unsafe_allow_html=True)

        # add github usernames
        st.markdown('<p style="color:white; font-weight:bold; text-decoration:none; text-align:center;"><a style="color:white; text-decoration:none;" href="https://github.com/MinaAlmasi">@MinaAlmasi</a> & <a style="color:white; text-decoration:none;" href="https://github.com/drasbaek">@drasbaek</a></p>', unsafe_allow_html=True)


if __name__ == '__main__':
    main()