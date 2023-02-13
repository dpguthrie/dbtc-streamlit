# stdlib

# third party
import streamlit as st

st.set_page_config(
    page_title="dbtc",
    page_icon="👋",
    
)
st.write("# Welcome to the dbtc Explorer! 👋")

# first party
from utils.client import populate_session_state


st.markdown(
    """
    **dbtc** is an open-source python library that provides a simple interface
    to both the admin and metadata APIs for dbt Cloud.
    \n
    To get started, input your service
    token below.
    """
)

st.text_input(
    label='Input Service Token',
    type='password',
    key='service_token',
    on_change=populate_session_state
)
st.markdown(
    """
    **👈 Select a page from the sidebar** to see some examples
    of what dbtc can do!
    ### Want to learn more?
    - Jump into dbtc's [documentation](https://dbtc.dpguthrie.com)
    - View dbt Cloud's [Admin API documentation](https://docs.getdbt.com/dbt-cloud/api-v2)
    - View dbt Cloud's [Metadata API documentation](https://docs.getdbt.com/docs/dbt-cloud-apis/metadata-api)
"""
)
