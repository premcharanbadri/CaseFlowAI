"""CaseFlow AI Streamlit dashboard. Run: streamlit run app.py"""
from pathlib import Path
import json
import pandas as pd
import streamlit as st

ROOT=Path(__file__).resolve().parent
METRICS=json.loads((ROOT/'outputs'/'metrics.json').read_text())
st.set_page_config(page_title='CaseFlow AI • Operations Strategy',page_icon='📊',layout='wide')
st.title('CaseFlow AI - Operations Strategy Dashboard')
# st.caption('DEMONSTRATION ONLY • Fully synthetic data and scenario-based financial benefits • Not a real employer case study')

def load_cases():
    return pd.read_csv(ROOT/'data'/'synthetic_cases.csv',parse_dates=['created_at'])

def load_test():
    return pd.read_csv(ROOT/'outputs'/'out_of_time_predictions.csv',parse_dates=['created_at'])

@st.cache_data
def datasets(): return load_cases(),load_test()
cases,test=datasets()
ops=METRICS['operations']; model=METRICS['model']
col=st.columns(4)
col[0].markdown(f"**Cases**<br><span style='font-size:30px; font-weight:bold;'>{len(cases):,}</span>", unsafe_allow_html=True)
col[1].markdown(f"**Average handling time**<br><span style='font-size:30px; font-weight:bold;'>{ops['average_handle_minutes']:.1f} min</span>", unsafe_allow_html=True)
col[2].markdown(f"**Observed reroute rate**<br><span style='font-size:30px; font-weight:bold;'>{100*ops['reroute_rate']:.1f}%</span>", unsafe_allow_html=True)
col[3].markdown(f"**Observed SLA breaches**<br><span style='font-size:30px; font-weight:bold;'>{100*ops['sla_breach_rate']:.1f}%</span>", unsafe_allow_html=True)


t1,t2,t3=st.tabs(['Root-cause analytics','AI vs. rules','Economics & decision'])
with t1:
    st.subheader('Where is time being lost?')
    queue=cases.groupby('correct_queue',as_index=False).agg(cases=('case_id','count'),handle_min=('handle_minutes','mean'),reroute_rate=('rerouted','mean'),sla_rate=('sla_breached','mean'))
    st.dataframe(queue,hide_index=True,use_container_width=True)
    st.bar_chart(queue.set_index('correct_queue')[['handle_min']])
    st.write('Interpretation: rerouting and missing fields are associated with slower handling in this synthetic process. Correlation does not establish their causal contribution.')
    st.dataframe(cases.groupby(['rerouted','missing_fields'],as_index=False)['handle_minutes'].agg(['mean','count']),use_container_width=True)
with t2:
    st.subheader('Model evaluation on out-of-time cases')
    m=st.columns(4)
    m[0].metric('AI full-coverage accuracy',f"{100*model['held_out_full_coverage_accuracy']:.1f}%")
    m[1].metric('AI policy coverage',f"{100*model['ai_policy']['coverage']:.1f}%")
    m[2].metric('AI routed precision',f"{100*model['ai_policy']['precision_routed']:.1f}%")
    m[3].metric('Rules routed precision',f"{100*model['rules_policy']['precision_routed']:.1f}%")
    chart=pd.DataFrame({'Coverage':[model['ai_policy']['coverage'],model['rules_policy']['coverage']],
                        'Precision':[model['ai_policy']['precision_routed'],model['rules_policy']['precision_routed']]},index=['AI threshold policy','Rules baseline'])
    st.bar_chart(chart)
    st.caption(f"AI threshold of {model['selected_threshold']:.2f} was chosen on validation data subject to ≥97% routed precision. High/critical priority cases go to human review, regardless of model confidence.")
    st.dataframe(test[['case_id','description' if 'description' in test else 'correct_queue','priority','correct_queue','ai_prediction','confidence','ai_route']].head(30),hide_index=True,use_container_width=True)
with t3:
    st.subheader('Pilot economics: assumptions, not actual savings')
    c1,c2=st.columns(2)
    volume=c1.number_input('Monthly cases',100,100000,900,100)
    labor=c2.number_input('Fully loaded labor cost ($/hour)',10.,250.,25.,5.)
    saved=c1.slider('Minutes saved for each correctly suggested standard case',0.,15.,5.,.5)
    qa=c2.slider('Quality review minutes per suggested case',0.,5.,.5,.25)
    error=c1.slider('Additional minutes for a misrouted case',0.,45.,12.,1.)
    annual_run=c2.number_input('Annual run cost ($)',0.,100000.,1800.,100.)
    build=c1.number_input('One-time implementation ($)',0.,100000.,8000.,500.)
    coverage=model['ai_policy']['coverage']
    errors=model['ai_policy']['error_rate_all_cases']
    hours=volume*(coverage*(saved-qa)-errors*error)/60
    annual=hours*labor*12
    net=annual-annual_run-build
    d=st.columns(3)
    d[0].metric('Hours released / month',f'{hours:,.1f}')
    d[1].metric('Annual capacity value',f'${annual:,.0f}')
    d[2].metric('Year-1 net value',f'${net:,.0f}')
    st.info('Released capacity is not a cash saving unless costs are actually avoided. Run a randomized pilot and measure rework, human effort, SLA rates, and classifier mistakes before scaling.')
    st.markdown('**Decision gates:** ≥97% routed precision on out-of-time data, non-inferior SLA and quality during pilot, positive risk-adjusted net benefit, and a working manual fallback.')
