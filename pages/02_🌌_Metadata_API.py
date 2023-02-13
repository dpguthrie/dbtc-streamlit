# stdlib
import inspect
import json

# third party
import streamlit as st
from dbtc.client import schema

st.set_page_config(
    page_title='dbtc Explorer - Metadata API', page_icon='🌌', layout='centered'
)


if 'dbtc_client' not in st.session_state:
    st.warning('Go to home page and enter your service token')
    st.stop()


# first party
from utils import client, inputs
from utils.helpers import is_valid_argument, prop_public_methods


st.write("# Explore the Metadata API! 👋")

inputs.get_account_widget()
inputs.get_project_widget()

st.subheader('Select a Method below')

# Retrieve metadata public methods
public_methods = prop_public_methods(st.session_state.dbtc_client.metadata)
public_method = st.selectbox('Select Method', options=public_methods, key='metadata_public_method')
public_method_api = getattr(st.session_state.dbtc_client.metadata, public_method)
st.help(public_method_api)

# Iterate through parameters of selected function, creating widgets
parameters = inspect.signature(public_method_api).parameters
st.session_state.form_params = {}
for key, parameter in parameters.items():
    if key == 'database':
        database = st.text_input(label='Database', key='database')
        st.session_state.form_params['database'] = database
    elif key == 'environment_id':
        environment_id = inputs.get_environment_widget(parameter.default is not None)
        st.session_state.form_params['environment_id'] = environment_id
    elif key == 'identifier':
        identifier = st.text_input(label='Identifier', key='identifier')
        st.session_state.form_params['identifier'] = identifier
    elif key == 'job_id' or key == 'job_definition_id':
        job_id = inputs.get_job_widget(parameter.default is not None)
        st.session_state.form_params[key] = job_id
    elif key == 'last_run_count':
        last_run_count = st.number_input(
            label='Last Run Count',
            min_value=1,
            max_value=10,
            value=10,
            key='last_run_count'
        )
        st.session_state.form_params['last_run_count'] = last_run_count
    elif key == 'name':
        name = st.text_input(label='Name', key='name')
        st.session_state.form_params['name'] = name
    elif key == 'run_id':
        run_id = inputs.get_run_widget()
        st.session_state.form_params['run_id'] = run_id
    elif key == 'schema':
        schema = st.text_input(label='Schema', key='schema')
        st.session_state.form_params['schema'] = schema
    elif key == 'unique_id':
        unique_id = st.text_input(label='Unique ID', key='unique_id')
        st.session_state.form_params['unique_id'] = unique_id
    elif key == 'with_catalog':
        with_catalog = st.checkbox(
            label='With Catalog?',
            value=False,
            key='with_catalog',
            help='Return only runs that have catalog information',
        )
        st.session_state.form_params['with_catalog'] = with_catalog
    else:
        pass

submitted = st.button('Make Request')

if submitted:
    tab1, tab2 = st.tabs(['Python', 'CLI'])
    arg_string = ''
    for k, v in st.session_state.form_params.items():
        if isinstance(v, list):
            if len(v) > 0:
                arg_string += f'{k}={v}, '
        elif v is not None and v != '':
            arg_string += f'{k}={v}, '
    arg_string = arg_string[:-2]
    tab1.code(
    f'''
from dbtc import dbtCloudClient

client = dbtCloudClient(service_token='***')

# Or if the environment variable DBT_CLOUD_SERVICE_TOKEN is set
# client = dbtCloudClient()

data = client.metadata.{public_method}({arg_string})
print(data)
    '''
    )
    kwargs = {}
    for k, v in st.session_state.form_params.items():
        if is_valid_argument(v):
            kwargs[k] = v
    cli_method = public_method.replace('_', '-')
    cli_args = ' '.join([f'--{k.replace("_", "-")} {v}' for k, v in kwargs.items()])
    tab2.code(f'$ dbtc --token *** {cli_method} {cli_args}')
    tab2.markdown('Or if `DBT_CLOUD_SERVICE_TOKEN` is set as an environment variable:')
    tab2.code(f'$ dbtc {cli_method} {cli_args}')
    data = client.dynamic_request(
        st.session_state.dbtc_client.metadata,
        public_method,
        **kwargs
    )
    st.write(data)
