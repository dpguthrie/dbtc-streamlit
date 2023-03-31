# stdlib
import json
from typing import Any, List

# third party
import pandas as pd
import streamlit as st


NOT_PUBLIC_METHODS = (
    'get_project_by_name',
    'get_account_by_name',
    'list_runs_v4',
    'get_run_v4',
    'full_url',
)

URLS = {
    'run': 'https://cloud.getdbt.com/deploy/{account_id}/projects/{project_id}/runs/{run_id}',
    'job': 'https://cloud.getdbt.com/deploy/{account_id}/projects/{project_id}/jobs/{job_id}',
    'docs': 'https://cloud.getdbt.com/accounts/{account_id}/jobs/{docs_job_id}/docs/#!/model/{unique_id}'
}


def list_to_dict(
    ls: List[Any],
    id_field: str = 'id',
    value_field: str = 'name',
    reverse: bool = False,
):
    if ls:
        ls = sorted(ls, key=lambda d: d[value_field], reverse=reverse)
        return {d[id_field]: d for d in ls}
    
    return {}


def snake_to_title(string: str, splitter: str = '_'):
    return ' '.join([s.capitalize() for s in string.split(splitter)])


def is_public_method(_prop, method_name: str):
    if (
        not method_name.startswith('_')
        and hasattr(getattr(_prop, method_name), '__call__')
        and not method_name in NOT_PUBLIC_METHODS
    ):
        return True
        
    return False


def prop_public_methods(prop):
    return [p for p in dir(prop) if is_public_method(prop, p)]


def is_valid_argument(value):
    if value is None:
        return False
    
    if isinstance(value, list) or isinstance(value, str):
        if len(value) == 0:
            return False
        
    return True


def clear_session_state(states: List[str]):
    for state in states:
        if state in st.session_state:
            del st.session_state[state]
            
            
def apply_datetime_to_columns(df: pd.DataFrame, columns: List[str]):
    df[columns] = df[columns].apply(pd.to_datetime)
    return df


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


if __name__ == '__main__':
    pass

