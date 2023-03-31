# stdlib
from typing import List

# third party
import streamlit as st

# first party
from utils import client
from utils.helpers import clear_session_state, list_to_dict

    

def get_account_widget(states: List[str] = [
    'project_index', 'job_index', 'environment_index'
]):
    accounts = client.dynamic_request(
        st.session_state.dbtc_client.cloud,
        'list_accounts',
    ).get('data', [])
    accounts = list_to_dict(accounts)
    st.session_state.accounts = accounts
    return st.selectbox(
        label='Select Account',
        options=accounts.keys(),
        format_func=lambda x: accounts[x]['name'],
        key='account_id',
        on_change=clear_session_state,
        args=(states, )
    )
    
    
def get_connection_widget(is_required: bool = True):
    connections = client.dynamic_request(
        st.session_state.dbtc_client.cloud,
        'list_connections',
        st.session_state.account_id,
        st.session_state.project_id,
    ).get('data', [])
    connections = list_to_dict(connections)
    options = list(connections.keys())
    if not is_required:
        options.insert(0, None)
    st.session_state.connections = connections
    return st.selectbox(
        label='Select Connection',
        options=options,
        format_func=lambda x: connections[x]['name'] if x is not None else x,
        key='connection_id',
    )
    
    
def get_delete_cloned_job_widget():
   return st.checkbox(
        label='Delete Cloned Job?',
        value=True,
        key='delete_cloned_job',
        help='Indicate whether cloned job should be deleted after completion.',
    )
    
    
def get_credential_widget(is_required: bool = True):
    credentials = client.dynamic_request(
        st.session_state.dbtc_client.cloud,
        'list_credentials',
        st.session_state.account_id,
        st.session_state.project_id,
    ).get('data', [])
    credentials = list_to_dict(credentials, value_field='schema')
    options = list(credentials.keys())
    if not is_required:
        options.insert(0, None)
    st.session_state.credentials = credentials
    return st.selectbox(
        label='Select Credential',
        options=options,
        format_func=lambda x: f"{credentials[x]['type']} - {credentials[x]['schema']} - {credentials[x]['user']}" if x is not None else x,
        key='credential_id',
    )
    
    
    
def get_environment_widget(is_required: bool = True, **kwargs):
    environments = client.dynamic_request(
        st.session_state.dbtc_client.cloud,
        'list_environments',
        st.session_state.account_id,
        project_id=st.session_state.get('project_id', []),
        **kwargs
    ).get('data', [])
    environments = list_to_dict(environments)
    options = list(environments.keys())
    if not is_required:
        options.insert(0, None)
    st.session_state.environments = environments
    return st.selectbox(
        label='Select Environment',
        options=options,
        format_func=lambda x: environments[x]['name'] if x is not None else x,
        key='environment_id',
    )

    
    
def get_group_widget(is_required: bool = True):
    groups = client.dynamic_request(
        st.session_state.dbtc_client.cloud,
        'list_groups',
        st.session_state.account_id,
    ).get('data', [])
    groups = list_to_dict(groups)
    options = list(groups.keys())
    if not is_required:
        options.insert(0, None)
    st.session_state.groups = groups
    return st.selectbox(
        label='Select Group',
        options=options,
        format_func=lambda x: groups[x]['name'] if x is not None else x,
        key='environment_id',
    )

    
def get_job_widget(is_required: bool = True, **kwargs):
    jobs = client.dynamic_request(
        st.session_state.dbtc_client.cloud,
        'list_jobs',
        st.session_state.account_id,
        project_id=st.session_state.get('project_id', None),
        **kwargs,
    ).get('data', [])
    jobs = list_to_dict(jobs)
    options = list(jobs.keys())
    if not is_required:
        options.insert(0, None)
    st.session_state.jobs = jobs
    return st.selectbox(
        label='Select Job',
        options=options,
        format_func=lambda x: jobs[x]['name'] if x is not None else x,
        key='job_id',
    )
        
        
def get_project_widget(states: List[str] = [], is_required: bool = True):
    projects = client.dynamic_request(
        st.session_state.dbtc_client.cloud,
        'list_projects',
        st.session_state.account_id,
    ).get('data', [])
    projects = list_to_dict(projects)
    options = list(projects.keys())
    if not is_required:
        options.insert(0, None)
    st.selectbox(
        label='Select Project',
        options=options,
        format_func=lambda x: projects[x]['name'] if x is not None else x,
        key='project_id',
        on_change=clear_session_state,
        args=(states, )
    )
    st.session_state.projects = projects
    
    
def get_run_widget(is_required: bool = True, **kwargs):
    runs = client.dynamic_request(
        st.session_state.dbtc_client.cloud,
        'list_runs',
        st.session_state.account_id,
        job_definition_id=st.session_state.get('job_id', None),
        order_by='-id',
        **kwargs,
    ).get('data', [])
    runs = list_to_dict(runs, value_field='id', reverse=True)
    options = list(runs.keys())
    if not is_required:
        options.insert(0, None)
    return st.selectbox(
        label='Select Run',
        options=options,
        format_func=lambda x: runs[x]['id'] if x is not None else x,
        key='run_id',
    )
    
    
def get_service_token_widget():
    service_tokens = client.dynamic_request(
        st.session_state.dbtc_client.cloud,
        'list_service_tokens',
        st.session_state.account_id,
    ).get('data', [])
    service_tokens = list_to_dict(service_tokens)
    return st.selectbox(
        label='Select Service Token',
        options=list(service_tokens.keys()),
        format_func=lambda x: service_tokens[x]['name'],
        key='service_token_id',
    )
    
    
def get_users_widget():
        users = client.dynamic_request(
            st.session_state.dbtc_client.cloud,
            'list_users',
            st.session_state.account_id,
        ).get('data', [])
        users = list_to_dict(users, value_field='email')
        return st.selectbox(
            label='Select User',
            options=list(users.keys()),
            format_func=lambda x: users[x]['email'],
            key='user_id',
        )
    