# third party
import streamlit as st
from dbtc import dbtCloudClient

# first party
from utils.helpers import list_to_dict

def get_client(service_token):
    client = dbtCloudClient(service_token=service_token)
    return client


@st.experimental_memo(show_spinner=False)
def dynamic_request(_prop, method, *args, **kwargs):
    return getattr(_prop, method)(*args, **kwargs)


def populate_session_state():
    if st.session_state.get('service_token', '') != '':
        st.session_state.dbtc_client = get_client(st.session_state.service_token)
        accounts = dynamic_request(
            st.session_state.dbtc_client.cloud,
            'list_accounts'
        ).get('data', [])
        st.session_state.accounts = list_to_dict(accounts)
        st.session_state.account_id = list(st.session_state.accounts.keys())[0]
        projects = dynamic_request(
            st.session_state.dbtc_client.cloud,
            'list_projects',
            st.session_state.account_id
        ).get('data', [])
        st.session_state.projects = projects
    if st.session_state.get('projects', None):
        st.success('Success!  Explore the rest of the app!')


if __name__ == '__main__':
    pass
