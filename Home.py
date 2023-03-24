# third party
import streamlit as st
from dbtc import dbtCloudClient

# first party
from utils.client import dynamic_request
from utils.helpers import list_to_dict


st.set_page_config(
    page_title="dbtc",
    page_icon="👋",
    
)
st.write("# Welcome to the dbtc Explorer! 👋")


st.markdown(
    """
    **dbtc** is an open-source python library that provides a simple interface
    to both the admin and metadata APIs for dbt Cloud.
    \n
    To get started, input your service
    token below.
    """
)

service_token = st.text_input(
    label='Input Service Token',
    type='password',
    key='service_token',
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

if st.session_state.service_token != '':
    st.cache_data.clear()
    st.session_state.dbtc_client = dbtCloudClient(
        service_token=st.session_state.service_token
    )
    accounts = dynamic_request(
        st.session_state.dbtc_client.cloud,
        'list_accounts'
    ).get('data', [])
    st.session_state.accounts = list_to_dict(accounts)
    try:
        st.session_state.account_id = list(st.session_state.accounts.keys())[0]
    except IndexError:
        st.error(
            'No accounts were found with the service token entered.  '
            'Please try again.'
        )
    else:
        projects = dynamic_request(
            st.session_state.dbtc_client.cloud,
            'list_projects',
            st.session_state.account_id
        ).get('data', [])
        st.session_state.projects = projects
        st.success('Success!  Explore the rest of the app!')
