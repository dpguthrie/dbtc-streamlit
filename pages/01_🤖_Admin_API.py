# stdlib
import inspect
import json

# third party
import streamlit as st

st.set_page_config(
    page_title='dbtc Explorer - Admin API', page_icon='🤖', layout='centered'
)

# first party
from utils import client
from utils import inputs
from utils.helpers import is_valid_argument, prop_public_methods


if 'account_id' not in st.session_state:
    st.warning('Go to home page and enter your service token')
    st.stop()

st.write("# Explore the Admin API! 👋")

st.subheader('Select a Method below')

public_methods = prop_public_methods(st.session_state.dbtc_client.cloud)

public_method = st.selectbox('Select Method', options=public_methods, key='admin_public_method')

public_method_api = getattr(st.session_state.dbtc_client.cloud, public_method)

st.help(public_method_api)
parameters = inspect.signature(public_method_api).parameters

st.session_state.form_params = {}
for key, parameter in parameters.items():
    if key == 'account_id':
        inputs.get_account_widget()
        st.session_state.form_params['account_id'] = st.session_state.account_id
    elif key == 'connection_id':
        connection_id = inputs.get_connection_widget(parameter.default is not None)
        st.session_state.form_params['connection_id'] = connection_id
    elif key == 'credentials_id':
        credentials_id = inputs.get_credential_widget(parameter.default is not None)
        st.session_state.form_params['credentials_id'] = credentials_id
    elif key == 'delete_cloned_job':
        delete_cloned_job = st.checkbox(
            label='Delete Cloned Job?',
            value=True,
            key='delete_cloned_job',
            help='Indicate whether cloned job should be deleted after completion.',
        )
        st.session_state.form_params['delete_cloned_job'] = delete_cloned_job
    elif key == 'environment_id':
        environment_id = inputs.get_environment_widget(parameter.default is not None)
        st.session_state.form_params['environment_id'] = environment_id
    elif key == 'include_related':
        include_related = st.text_input(label='Include Related', key='include_related')
        st.session_state.form_params['include_related'] = include_related
    elif key == 'group_id':
        group_id = inputs.get_group_widget(parameter.default is not None)
        st.session_state.form_params['group_id'] = group_id
    elif key == 'job_id' or key == 'job_definition_id':
        job_id = inputs.get_job_widget(parameter.default is not None)
        st.session_state.form_params[key] = job_id
    elif key == 'limit':
        limit = st.number_input(label='Limit', min_value=1, max_value=100, value=100, key='limit')
        st.session_state.form_params['limit'] = limit
    elif key == 'logged_at_end':
        logged_at_end = st.date_input(
            label='Logged At End',
            key='logged_at_end',
        )
        st.session_state.form_params['logged_at_end'] = logged_at_end
    elif key == 'logged_at_start':
        logged_at_start = st.date_input(
            label='Logged At Start',
            key='logged_at_start',
        )
        st.session_state.form_params['logged_at_start'] = logged_at_start
    elif key == 'offset':
        offset = st.number_input(label='Offset', min_value=0, value=0, key='offset')
        st.session_state.form_params['offset'] = offset
    elif key == 'order_by':
        order_by = st.text_input(label='Order By', key='order_by')
        st.session_state.form_params['order_by'] = order_by
    elif key == 'path':
        path = st.text_input(label='Path', key='path')
        st.session_state.form_params['path'] = path
    elif key == 'payload':
        payload = st.text_area(
            label='Payload',
            key='payload',
            help='Payload should be a valid JSON string',
            placeholder='{"key": "value"}',
        )
        if payload != '':
            st.session_state.form_params['payload'] = json.loads(payload)
    elif key == 'permission_id':
        permission_id = st.number_input(label='Permission ID', min_value=1, value=1)
        st.session_state.form_params['permission_id'] = permission_id
    elif key == 'poll_interval':
        poll_interval = st.number_input(
            label='Poll Interval',
            min_value=5,
            value=10,
            )
        st.session_state.form_params['poll_interval'] = poll_interval
    elif key == 'project_id':
        project_id = inputs.get_project_widget(
            ['job_id', 'environment_id'], parameter.default is not None
        )
        st.session_state.form_params['project_id'] = st.session_state.project_id
    elif key == 'repository_id':
        repository_id = st.number_input(label='Repository ID', min_value=1, value=1)
        st.session_state.form_params['repository_id'] = repository_id
    elif key == 'run_id':
        run_id = inputs.get_run_widget()
        st.session_state.form_params['run_id'] = run_id
    elif key == 'offset':
        offset = st.number_input(label='Offset', min_value=0, value=0, key='offset')
        st.session_state.form_params['offset'] = offset
    elif key == 'service_token_id':
        service_token_id = inputs.get_service_token_widget()
        st.session_state.form_params['service_token_id'] = service_token_id
    elif key == 'should_poll':
        should_poll = st.checkbox(
            label='Should Poll?',
            value=True,
            key='should_poll',
            help='Indicate whether job should poll until completion or not',
        )
        st.session_state.form_params['should_poll'] = should_poll
    elif key == 'status':
        status = st.multiselect(
            label='Status',
            options=['cancelled', 'error', 'queued', 'running', 'starting', 'success'],
            default=None,
        )
        st.session_state.form_params['status'] = status
    elif key == 'step':
        step = st.number_input(label='Step', min_value=1, value=4, step=1)
        st.session_state.form_params['step'] = step
    elif key == 'trigger_on_failure_only':
        trigger_on_failure_only = st.checkbox(
            label='Trigger on Failure Only?',
            value=True,
            key='trigger_on_failure_only',
        )
        st.session_state.form_params['trigger_on_failure_only'] = \
            trigger_on_failure_only
    elif key == 'type':
        env_type = st.selectbox(
            label='Select Type',
            options=[None, 'deployment', 'development'],
            key='env_type',
        )
        st.session_state.form_params['type'] = env_type
    elif key == 'user_id':
        user_id = inputs.get_users_widget()
        st.session_state.form_params['user_id'] = user_id
    else:
        pass

if public_method.startswith('delete_'):
    st.warning('Delete operations will prompt you to confirm')
submitted = st.button('Make Request')

if submitted:
    tab1, tab2 = st.tabs(['Python', 'CLI'])
    arg_string = ''
    for k, v in st.session_state.form_params.items():
        if isinstance(v, list):
            if len(v) > 0:
                arg_string += f'{k}={v}, '
        elif v is not None and v != '':
            if isinstance(v, str):
                v = f"'{v}'"
            arg_string += f'{k}={v}, '
    arg_string = arg_string[:-2]
    tab1.code(
    f'''
from dbtc import dbtCloudClient

client = dbtCloudClient(service_token='***')

# Or if the environment variable DBT_CLOUD_SERVICE_TOKEN is set
# client = dbtCloudClient()

data = client.cloud.{public_method}({arg_string})
print(data)
    '''
    )
    kwargs = {}
    for k, v in st.session_state.form_params.items():
        if is_valid_argument(v):
            kwargs[k] = v
    cli_method = st.session_state.admin_public_method.replace('_', '-')
    cli_args = ' '.join([f'--{k.replace("_", "-")} {v}' for k, v in kwargs.items()])
    cli_args_x_account_id = ' '.join(
        [f'--{k.replace("_", "-")} {v}' for k, v in kwargs.items() if k != 'account_id']
    )
    tab2.code(f'$ dbtc --token *** {cli_method} {cli_args}')
    tab2.markdown('Or if `DBT_CLOUD_SERVICE_TOKEN` is set as an environment variable:')
    tab2.code(f'$ dbtc {cli_method} {cli_args}')
    tab2.markdown('Or if `DBT_CLOUD_SERVICE_TOKEN` and `DBT_CLOUD_ACCOUNT_ID` are set as environment variables:')
    tab2.code(f'$ dbtc {cli_method} {cli_args_x_account_id}')
    if public_method.startswith('delete_'):
        st.error("Are you sure you'd like to proceed?")
        if st.button('Proceed'):        
            data = client.dynamic_request(
                st.session_state.dbtc_client.cloud,
                st.session_state.admin_public_method,
                **kwargs
            )
            st.write(data)
    else:
        data = client.dynamic_request(
            st.session_state.dbtc_client.cloud,
            st.session_state.admin_public_method,
            **kwargs
        )
        st.write(data)
