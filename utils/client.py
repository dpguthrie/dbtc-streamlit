# third party
import streamlit as st
from requests.exceptions import ConnectionError


@st.cache_data(show_spinner=False)
def dynamic_request(_prop, method, *args, **kwargs):
    try:
        return getattr(_prop, method)(*args, **kwargs)
    except ConnectionError as e:
        st.error(e)
        st.stop()


if __name__ == '__main__':
    pass
