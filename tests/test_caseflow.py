import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from caseflow import generate_data,evaluate_policy,projected_minutes_per_case,rules_predict

def test_synthetic_data_integrity():
    df=generate_data(250,seed=42)
    assert df.case_id.is_unique
    assert all(df.created_at <= df.resolved_at)
    assert all((df.rerouted==0) == (df.initial_queue==df.correct_queue))
    assert df.handle_minutes.min()>0

def test_guardrails_protect_priority():
    metrics=evaluate_policy(['Billing','Billing','Access'],
        np.array(['Billing','Access','Access']),
        np.array([[.99,.01],[.2,.8],[.01,.99]]),
        ['Standard','Critical','Standard'],.90)
    assert metrics['auto_routed']==2
    assert metrics['wrong_routes']==0

def test_savings_penalize_wrong_routing():
    p={'coverage':0.6,'error_rate_all_cases':.03}
    assert abs(projected_minutes_per_case(p)-2.34)<1e-9

def test_manual_only_zero_savings():
    assert projected_minutes_per_case({'coverage':0.,'error_rate_all_cases':0.})==0

def test_rules_do_not_invent_categories():
    predictions=rules_predict(__import__('pandas').Series(['invoice refund','unknown generic request']))
    assert predictions[0]=='Billing'
    assert predictions[1]=='Manual review'
