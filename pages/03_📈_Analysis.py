# stdlib
from datetime import datetime, timezone
from typing import Dict, List

# third party
import altair as alt
import pandas as pd
import plotly.express as px
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid import JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from streamlit_plotly_events import plotly_events

# first party
from utils import agstyler
from utils.helpers import local_css


st.set_page_config(
    page_title='dbtc Explorer - Analysis', page_icon='📈', layout='wide'
)

if 'account_id' not in st.session_state:
    st.warning('Go to home page and enter your service token')
    st.stop()

# first party
from utils import client
from utils import inputs
from utils.helpers import URLS


DATETIME_COLUMNS = [
    'created_at',
    'updated_at',
    'dequeued_at',
    'started_at',
    'finished_at',
    'should_start_at',
    'last_checked_at',
    'last_heartbeat_at',
]
ABOVE_BELOW_RUNS = 3
OVERRIDE_HEIGHT = 600


def _set_color(x):
    color: str = 'blue'
    if x == 'Success':
        color = '#00CC96'
    elif x == 'Error':
        color = '#EF553B'
    elif x == 'Cancelled':
        color = '#FECB52'
    return color


def _enhance_df(df: pd.DataFrame):
    
    # Convert to minutes
    df['duration_m'] = df['duration'].apply(get_minutes)
    df['queued_duration_m'] = df['queued_duration'].apply(get_minutes)
    df['run_duration_m'] = df['run_duration'].apply(get_minutes)
    
    # Convert datetime columns
    df[DATETIME_COLUMNS] = df[DATETIME_COLUMNS].apply(
        pd.to_datetime
    )
    df['created_at'] = df['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Additional transformations
    df['run_duration_m_avg'] = df['run_duration_m'].mean()
    df['queued_duration_m_avg'] = df['queued_duration_m'].mean()
    return df


def get_minutes(time_str: str):
    h, m, s = time_str.split(':')
    return round(int(h) * 60 + int(m) + (int(s) / 60), 1)


def get_all_runs(**kwargs):
    all_data = []
    for OFFSET in range(0, st.session_state.n_runs, 100):
        data = client.dynamic_request(
            st.session_state.dbtc_client.cloud,
            'list_runs',
            st.session_state.account_id,
            offset=OFFSET,
            limit=100,
            order_by='-id',
            **kwargs,
        ).get('data', [])
        if len(data) == 0:
            break
        
        all_data.extend(data)
    df = pd.DataFrame(all_data)
    return _enhance_df(df)




def get_env_runs_stats(df: pd.DataFrame):
    df['job_name'] = df['job'].apply(lambda x: x.get('name'))
    df['is_success'] = df['status_humanized'] == 'Success'
    df = df.groupby('job_name').agg(
        avg_runtime=('run_duration_m', 'mean'),
        total_runs=('id', 'count'),
        total_success=('is_success', 'sum'),
        last_run=('started_at', 'max'),
        last_runtime=('run_duration_m', 'first'),
        std_runtime=('run_duration_m', 'std'),
        max_runtime=('run_duration_m', 'max'),
        account_id=('account_id', 'mean'),
        project_id=('project_id', 'mean'),
        job_id=('job_definition_id', 'mean'),
    )
    df['success_rate'] = round(df['total_success'] / df['total_runs'] * 100, 2)
    df['url'] = df.apply(lambda x: f'https://cloud.getdbt.com/deploy/{int(x.account_id)}/projects/{int(x.project_id)}/jobs/{int(x.job_id)}', axis=1)
    df['last_run'] = df['last_run'].dt.strftime('%Y-%m-%d %H:%M:%S')
    cols = ['avg_runtime', 'last_runtime', 'std_runtime', 'max_runtime']
    df[cols] = df[cols].round(1)
    return df[[
        'total_runs',
        'total_success',
        'success_rate',
        'last_run',
        'last_runtime',
        'avg_runtime',
        'max_runtime',
        'std_runtime',
        'url',
        'job_id',
    ]]
    
    
def get_aggregate_stats(df: pd.DataFrame):
    total_runs = df['total_runs'].sum()
    total_success = df['total_success'].sum()
    max_runtime = df['max_runtime'].max()
    success_rate = total_success / total_runs
    return {
        'success_rate': success_rate,
        'completed_runs': total_success,
        'max_runtime': max_runtime,
    }
    

def build_last_n_runs_chart(runs_df: pd.DataFrame):

    # Get job URL
    job_url = URLS['job'].format(**{
        'account_id': st.session_state.account_id,
        'project_id': st.session_state.project_id,
        'job_id': st.session_state.job_id,
    })
    job = st.session_state.jobs[st.session_state.job_id]['name']

    # Create line chart for runs
    runs_fig = px.line(
        runs_df,
        x='started_at',
        y='run_duration_m',
        hover_data={'id': False, 'status_humanized': True},
        hover_name='id',
        markers=True,
        title=f'Last {st.session_state.n_runs} Runs - <a href="{job_url}">{job}</a>',
    ).update_layout(
        title_x=0.5,
        xaxis_title='Date',
        yaxis_title='Time (minutes)',
        hovermode='closest',
    ).update_traces(
        marker=dict(
            color='white',
            line=dict(
                color=list(map(_set_color, runs_df['status_humanized'])),
                width=3,
            ),
            
        ),       
    )
    avg = px.line(
        runs_df,
        x='started_at',
        y='run_duration_m_avg',
    ).update_traces(
        line_color='red', line_dash='dash'
    )
    runs_fig.add_traces(avg.data)
    return runs_fig


def build_gantt_chart(runs_df: pd.DataFrame, selected_run: List[Dict]):
    kwargs = {'fields': [
        'name',
        'executionTime',
        'executeStartedAt',
        'executeCompletedAt',
        'status',
        'threadId',
        'uniqueId',
    ]}
    if selected_run:
        idx = selected_run[0]['pointNumber']
        run_id = runs_df.loc[idx]['id']
    else:
        run_id = runs_df.loc[0]['id']
    url = URLS['run'].format(**{
        'account_id': st.session_state.account_id,
        'project_id': st.session_state.project_id,
        'run_id': run_id,
    })
    kwargs['run_id'] = int(run_id)
    models = client.dynamic_request(
        st.session_state.dbtc_client.metadata,
        'get_models',
        st.session_state.job_id,
        **kwargs
    ).get('data', {}).get('models', [])
    models = [m for m in models if m['threadId'] is not None]
    if len(models) == 0:
        st.info(f'No model timing info for run [{run_id}]({url})')
        return None, pd.DataFrame([])
    
    df = pd.DataFrame(models)
    GANTT_DATETIME_COLS = ['executeStartedAt', 'executeCompletedAt']
    df[GANTT_DATETIME_COLS] = df[GANTT_DATETIME_COLS].apply(pd.to_datetime)
    fig = px.timeline(
        df,
        x_start='executeStartedAt',
        x_end='executeCompletedAt',
        y='threadId',
        color='executionTime',
        color_continuous_scale='blues',
        hover_data={
            'executeStartedAt': False,
            'executeCompletedAt': False,
            'threadId': False,
            'name': False,
            'status': True,
        },
        title=f'Model Timing - <a href="{url}">{run_id}</a>',
        hover_name='name',
    ).update_layout(title_x=0.5, hovermode='closest')
    return fig, df


def get_all_model_runs(run_ids: List[int]):
    data = []
    progress_bar = st.progress(0)
    total_run_ids = len(run_ids)
    for i, run_id in enumerate(run_ids):
        models = client.dynamic_request(
            st.session_state.dbtc_client.metadata,
            'get_models',
            job_id=st.session_state.job_id,
            run_id=run_id,
            fields=[
                'executeStartedAt',
                'executionTime',
                'status',
                'runId',
                'name',
            ]
        ).get('data', {}).get('models', [])
        data.extend(models)
        progress_bar.progress((i + 1) / total_run_ids)
    return pd.DataFrame(data)


def build_all_model_timing_chart(df, top_n: int = 5):
    top = df.groupby('name')['executionTime'].sum().nlargest(top_n)
    df = df[df['name'].isin(top.index)]
    fig = px.line(
        df,
        x='executeStartedAt',
        y='executionTime',
        color='name',
        hover_data=['status'],
        markers=True,
        title=f'Top {top_n} Models',
    ).update_layout(title_x=0.5)
    return fig


def get_intersections():
    def model_in_job(job_name, model_name):
        return model_name in job_models[job_name]
    
    job_models = {}
    for job_id, job_definition in st.session_state.jobs.items():
        is_ci_job = any([job_definition['triggers'][x] for x in ['github_webhook', 'git_provider_webhook']])
        if not False:
            data = client.dynamic_request(
                st.session_state.dbtc_client.metadata,
                'get_models',
                job_id,
                fields=['runGeneratedAt', 'name']
            )['data']
            if data is not None:
                job_models[job_definition['name']] = [
                    m['name'] for m in data['models'] if m['runGeneratedAt'] is not None
                ]
                
    df = pd.DataFrame(columns=job_models.keys(), index=list(set(
        [m for job in job_models.values() for m in job]
    )))
    df = df.apply(lambda x: pd.DataFrame(x).apply(lambda y: model_in_job(x.name, y.name), axis=1))*1
    df['total_jobs'] = df.iloc[:].sum(axis=1)
    df = df.loc[df['total_jobs'] > 1].sort_index().iloc[:, :-1].T
    return df


def get_model_timing_data(unique_id: str, run_ids: List[int]):
    data = []
    progress_bar = st.progress(0)
    total_run_ids = len(run_ids)
    for i, run_id in enumerate(run_ids):
        model = client.dynamic_request(
            st.session_state.dbtc_client.metadata,
            'get_model',
            job_id=st.session_state.job_id,
            run_id=run_id,
            unique_id=unique_id,
            fields=[
                'executeStartedAt',
                'executionTime',
                'status',
                'runId',
                'rawSql',
                'compiledSql',
            ]
        ).get('data', {}).get('model', {})
        if model is None:
            model = {}
        data.append(model)
        progress_bar.progress((i + 1) / total_run_ids)
    return pd.DataFrame(data)


def build_model_timing_chart(df: pd.DataFrame, unique_id: str):
    model_name = unique_id.split('.')[-1]
    docs_job_id = st.session_state.projects[st.session_state.project_id]['docs_job_id']
    if docs_job_id is not None:
        docs_url = URLS['docs'].format(**{
            'account_id': st.session_state.account_id,
            'docs_job_id': docs_job_id,
            'unique_id': unique_id,
        })
        model_title = f'<a href="{docs_url}">{model_name}</a>'
    else:
        model_title = model_name
    fig = px.line(
        df,
        x='executeStartedAt',
        y='executionTime',
        hover_data=['status'], markers=True,
        title=f'Model Timing - {model_title}',
    ).update_layout(title_x=0.5)
    
    return fig

        
def get_sql(model_df: pd.DataFrame, run_id: int):
    st.subheader('View SQL')
    row = model_df[model_df['runId'] == run_id].iloc[0]
    tab1, tab2 = st.tabs(['Raw', 'Compiled'])
    with tab1:
        st.code(row['rawSql'])
    with tab2:
        st.code(row['compiledSql'])
    

st.write('# Analyze Historical Performance')

st.markdown('''
1. Make selections in the dropdowns below
2. Click on the elements in the charts to drilldown further
''')

# Add styling for metrics
css = '''
[data-testid="metric-container"] {
    text-align: center;
} 

[data-testid="stMetricLabel"] {
    display: flex;
}
'''
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)


# Create widgets
inputs.get_account_widget()
inputs.get_project_widget()
inputs.get_environment_widget(type='deployment')
runs = st.number_input(
    label='Number of Runs',
    min_value=100,
    max_value=10000,
    step=100,
    key='n_runs'
)

if len(st.session_state.environments.keys()) > 0:
    
    selected_model: List[Dict] = None
    
    # All runs for specific environment
    env_runs_df = get_all_runs(
        environment_id=st.session_state.environment_id,
        include_related=['job'],
    )
    
    env_runs_df_xf = get_env_runs_stats(env_runs_df).reset_index()
    
    # Aggregating stats from xf df
    agg_stats = get_aggregate_stats(env_runs_df_xf)
    
    # Create metrics
    col1, col2, col3 = st.columns(3)
    col1.metric('Success Rate', f'{round(agg_stats["success_rate"] * 100, 2)}%')
    col2.metric('Completed Runs', agg_stats['completed_runs'])
    col3.metric('Longest Runtime (mins)', agg_stats['max_runtime'])
    
    # Create table for aggregate stats
    xf_formatter = {
        'job_name': ('Job', {**agstyler.PINLEFT, 'width': 250, 'cellRenderer': JsCode('''
                function(params) {console.log(params.data.url); return '<a href="' + params.data.url + '" target="_blank">' + params.value + '</a>'}
            ''')}),
        'total_runs': ('Runs', {'width': 75}),
        'success_rate': ('Success %', {'width': 100}),
        'last_run': ('Last Run', {}),
        'last_runtime': ('Last Runtime', {'width': 75}),
        'avg_runtime': ('Avg', {'width': 75}),
        'max_runtime': ('Max', {'width': 75}),
        'std_runtime': ('Std', {'width': 75}),
    }

    xf_grid = agstyler.draw_grid(
        env_runs_df_xf,
        formatter=xf_formatter,
        selection=None,
    )

    inputs.get_job_widget(environment_id=st.session_state.environment_id)
    
    runs_df = get_all_runs(
        job_definition_id=st.session_state.job_id,
        include_related=['job']
    )
    
    # Create line chart for last N runs
    runs_fig = build_last_n_runs_chart(runs_df)
    selected_run = plotly_events(runs_fig, override_height=OVERRIDE_HEIGHT)
    
    # Grab top model runs over same time period
    # run_ids = runs_df['id'].tolist()
    # model_runs_df = get_all_model_runs(run_ids)
    # model_runs_fig = build_all_model_timing_chart(model_runs_df)
    
    # All Model Timing Chart
    # selected_model_run = plotly_events(model_runs_fig, override_height=OVERRIDE_HEIGHT)
    
    # Model Timing chart
    model_timing_fig, models_df = build_gantt_chart(runs_df, selected_run)
    
    if model_timing_fig is not None:
        selected_model = plotly_events(model_timing_fig, override_height=OVERRIDE_HEIGHT)
        
    if selected_model:
        unique_id = models_df.loc[selected_model[0]['pointNumber']]['uniqueId']
        try:
            run_index = selected_run[0]['pointNumber']
        except IndexError:
            run_index = 0
        above_below = st.number_input(
            label='+/- Runs',
            min_value=ABOVE_BELOW_RUNS,
            max_value=10,
            step=1,
            key='above_below_runs'
        )
        min_idx = max(0, run_index - st.session_state.above_below_runs)
        max_idx = min(run_index + st.session_state.above_below_runs, len(runs_df))
        run_ids = runs_df.iloc[min_idx:max_idx]['id'].tolist()
        
        model_df = get_model_timing_data(unique_id, run_ids)
        try:
            model_df['executeStartedAt'] = model_df['executeStartedAt'].apply(pd.to_datetime)
        except KeyError:
            pass
        else:
            model_fig = build_model_timing_chart(model_df, unique_id)
            selected_model_run = plotly_events(model_fig, override_height=OVERRIDE_HEIGHT)
            
            if selected_model_run:
                model_run_index = selected_model_run[0]['pointNumber']
                get_sql(model_df, model_df.loc[model_run_index]['runId'])
            else:
                get_sql(model_df, runs_df.loc[run_index]['id'])
