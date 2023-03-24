# third party
import streamlit as st

# first party
from utils.helpers import list_to_dict


@st.cache_data(show_spinner=False)
def dynamic_request(_prop, method, *args, **kwargs):
    return getattr(_prop, method)(*args, **kwargs)


if __name__ == '__main__':
    pass
