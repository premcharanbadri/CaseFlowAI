"""CaseFlow AI: reproducible synthetic service-operations decision science case.

All data are invented. No Globe Infotech, TCS, client, or employee records are used.
"""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, precision_score

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
OUT = ROOT / 'outputs'
CATEGORIES = ['Billing', 'Access', 'Technical', 'Account', 'Orders']
TEMPLATES = {
'Billing': [
    'invoice shows duplicate charge after payment confirmation',
    'customer requests explanation of incorrect service fee',
    'billing amount differs from contract for current month',
    'refund is missing after invoice adjustment',
    'credit note was not applied to customer invoice',
    'question about tax and invoice reconciliation',
],
'Access': [
    'user cannot log in after password reset',
    'multi factor authentication code is not arriving',
    'employee needs role permissions restored',
    'account access locked after sign in attempts',
    'session expires before user finishes portal task',
    'login permissions fail for newly invited team member',
],
'Technical': [
    'software integration error during batch upload',
    'API request returns timeout when saving records',
    'application displays unexpected error in dashboard',
    'system performance degrades during report generation',
    'data synchronization job fails overnight',
    'portal crashes on file attachment processing',
],
'Account': [
    'business requests update of organization contact information',
    'customer wants to change billing contact profile',
    'company needs to update registered legal address',
    'customer requests organization profile merge',
    'account owner changes due to internal reorganization',
    'contact information does not match approved account record',
],
'Orders': [
    'customer delivery status differs from tracking record',
    'shipment order is missing fulfillment confirmation',
    'order was partially fulfilled and needs investigation',
    'dispatch was delayed and delivery date changed',
    'warehouse allocation does not match purchase order',
    'order cancellation did not update fulfillment status',
],
}
GENERAL = [
 'request received from customer portal needing follow up',
 'please investigate and confirm next steps',
 'needs update before the next business day',
 'customer reports an issue with recent change',
 'operations team needs help with a pending request',
 'urgent follow up needed and status confirmation requested',
]
CHANNELS = ['Portal','Email','CRM','Phone']
QUEUE_CAPACITY = {'Billing':190, 'Access':190,'Technical':210,'Account':165,'Orders':210}
KEYWORDS = {
'Billing': ['invoice','refund','tax','credit note','charge','fee','payment'],
'Access': ['login','password','authentication','permissions','locked','session','sign in'],
'Technical': ['api','timeout','integration','crashes','synchronization','software','system'],
'Account': ['contact information','legal address','profile','account owner','organization'],
'Orders': ['order','shipment','delivery','warehouse','fulfillment','dispatch'],
}

def generate_data(n: int = 15300, seed: int = 2026) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    # 17-month synthetic historical dataset: January 2023 through May 2024.
    start = pd.Timestamp('2023-01-01')
    duration_days = (pd.Timestamp('2024-06-01')-start).days
    offsets = np.sort(rng.integers(0, duration_days*24*60, size=n))
    created = start + pd.to_timedelta(offsets, unit='m')
    labels = rng.choice(CATEGORIES, size=n, p=[.22,.22,.21,.15,.20])
    channel = rng.choice(CHANNELS, size=n, p=[.44,.35,.16,.05])
    priority = rng.choice(['Standard','High','Critical'],size=n,p=[.76,.20,.04])
    records=[]
    for i in range(n):
        correct = str(labels[i])
        # Ambiguity matters: some cases carry irrelevant category language.
        text_draw = rng.random()
        if text_draw < .08:
            # Insufficient detail: even a good model should abstain rather than invent certainty.
            text = str(rng.choice(GENERAL))
        elif text_draw < .15:
            # Misleading first message, correct business queue determined only after review.
            other = str(rng.choice([c for c in CATEGORIES if c!=correct]))
            text = str(rng.choice(TEMPLATES[other]))+'; case requires clarification'
        elif text_draw < .34:
            other = str(rng.choice([c for c in CATEGORIES if c!=correct]))
            text = str(rng.choice(TEMPLATES[correct])) + '; also mentioned ' + str(rng.choice(TEMPLATES[other]))
        elif text_draw < .44:
            text = str(rng.choice(GENERAL))+'; '+ str(rng.choice(TEMPLATES[correct]))[:20]
        else:
            text = str(rng.choice(TEMPLATES[correct]))
        if rng.random()<.18:
            text += '; '+str(rng.choice(GENERAL))
        missing = int(rng.random()<(.23 if channel[i]=='Email' else .11))
        wrong_route = int(rng.random() < (.16 if missing else .09))
        first_queue = correct if not wrong_route else str(rng.choice([c for c in CATEGORIES if c!=correct]))
        # An invented structural process model; not causal evidence from a company.
        handle = max(2.0, float(rng.normal(11.5 + 5.2*wrong_route + 3.4*missing + (2 if priority[i]=='Critical' else 0), 3.2)))
        wait = max(0.5, float(rng.gamma(2.0,2.0) + wrong_route*6.0 + (3 if correct=='Account' else 0)))
        end = created[i]+pd.Timedelta(hours=wait+handle/60)
        sla_limit = 8 if priority[i]=='Critical' else 24 if priority[i]=='High' else 48
        # SLA breach is constrained to be reasonably rare; heavy-tail waiting produces misses.
        slow_case = (rng.random() < (.095 if wrong_route else .033))
        if slow_case: wait += 30 if priority[i]=='High' else 50 if priority[i]=='Standard' else 10
        end = created[i]+pd.Timedelta(hours=wait+handle/60)
        records.append((f'C{i+1:06d}',created[i],str(channel[i]),str(priority[i]),text,correct,first_queue,
                        missing,wrong_route,round(handle,2),round(wait,2),end,int(wait+handle/60>sla_limit),sla_limit))
    return pd.DataFrame(records,columns=['case_id','created_at','channel','priority','description','correct_queue',
                      'initial_queue','missing_fields','rerouted','handle_minutes','wait_hours', 'resolved_at','sla_breached','sla_limit_hours'])


def rules_predict(description: pd.Series) -> np.ndarray:
    predictions=[]
    for text in description.str.lower():
        counts = {c:sum(text.count(term) for term in terms) for c,terms in KEYWORDS.items()}
        best = max(counts, key=counts.get)
        if counts[best]==0 or list(counts.values()).count(counts[best])>1:
            predictions.append('Manual review')
        else:
            predictions.append(best)
    return np.array(predictions)


def make_classifier() -> Pipeline:
    return Pipeline([
       ('tfidf',TfidfVectorizer(ngram_range=(1,2),min_df=3,max_features=3500,sublinear_tf=True)),
       ('model',LogisticRegression(max_iter=700, C=3.0))
    ])


def evaluate_policy(y_true, pred, probs, priority, threshold):
    confidence = probs.max(axis=1)
    allowed = (confidence>=threshold)&(np.asarray(priority)=='Standard')
    selected = pred[allowed]
    labels = np.asarray(y_true)
    correct = (selected==labels[allowed])
    return {'threshold':round(float(threshold),2), 'coverage':float(allowed.mean()),
        'precision_routed':float(correct.mean()) if len(selected) else 0.0,
        'error_rate_all_cases':float((allowed & (pred != labels)).mean()),
        'auto_routed':int(allowed.sum()),'wrong_routes':int((~correct).sum())}


def projected_minutes_per_case(policy, saved=5.0, qa=0.5, error_penalty=12.0):
    # Conservative: savings only accrue on auto-suggested, standard cases.
    # Extra error penalty from wrong route, then QA for every suggested case.
    return policy['coverage']*(saved-qa) - policy['error_rate_all_cases']*error_penalty


def main():
    DATA.mkdir(exist_ok=True, parents=True)
    OUT.mkdir(exist_ok=True,parents=True)
    df = generate_data()
    df.to_csv(DATA/'synthetic_cases.csv',index=False)
    # Repeatable temporal validation: train < Jan 2024; validation Jan-Feb 2024; test Mar-May 2024.
    train = df[df.created_at < '2024-01-01'].copy()
    valid = df[(df.created_at>='2024-01-01')&(df.created_at<'2024-03-01')].copy()
    test = df[df.created_at>='2024-03-01'].copy()
    clf = make_classifier()
    clf.fit(train.description,train.correct_queue)
    vproba=clf.predict_proba(valid.description)
    vpred=clf.classes_[vproba.argmax(axis=1)]
    candidates=[]
    for t in np.arange(.50, .951,.025):
        row=evaluate_policy(valid.correct_queue,vpred,vproba, valid.priority,t)
        row['savings_minutes_per_case']=projected_minutes_per_case(row)
        row['meets_guardrail']=bool(row['precision_routed'] >=.97 and row['coverage']>=.25)
        candidates.append(row)
    valid_df=pd.DataFrame(candidates)
    valid_df.to_csv(OUT/'validation_thresholds.csv',index=False)
    eligible=valid_df[valid_df.meets_guardrail]
    if eligible.empty:
        # Controlled fallback to a never-auto-route policy is a valid safety outcome.
        chosen_t=1.01
    else:
        chosen_t=float(eligible.sort_values(['savings_minutes_per_case','precision_routed'],ascending=False).iloc[0]['threshold'])
    tproba=clf.predict_proba(test.description)
    tpred=clf.classes_[tproba.argmax(axis=1)]
    test_policy=evaluate_policy(test.correct_queue,tpred,tproba,test.priority,chosen_t)
    rule_pred=rules_predict(test.description)
    rule_non_manual=rule_pred!='Manual review'
    rule_precision=(rule_pred[rule_non_manual] == test.correct_queue.to_numpy()[rule_non_manual]).mean()
    # Apply same high/critical human review policy to rules baseline.
    rule_allowed=rule_non_manual&(test.priority.to_numpy()=='Standard')
    rule_error_rate_all=((rule_pred != test.correct_queue.to_numpy())&rule_allowed).mean()
    rule_policy={'coverage':float(rule_allowed.mean()),'precision_routed':float((rule_pred[rule_allowed]==test.correct_queue.to_numpy()[rule_allowed]).mean()),
                 'error_rate_all_cases':float(rule_error_rate_all),'auto_routed':int(rule_allowed.sum()),'wrong_routes':int(((rule_pred != test.correct_queue.to_numpy())&rule_allowed).sum())}
    # KPI and financial assumptions (examples; do not present as historical results).
    month_cases=900; hourly_rate=25.; saved_minutes=5.; qa_minutes=.5; penalty=12.;
    monthly_minutes=month_cases*projected_minutes_per_case(test_policy,saved_minutes,qa_minutes,penalty)
    monthly_hours=monthly_minutes/60
    annual_capacity_value=monthly_hours*hourly_rate*12
    annual_license=1800.; implementation=8000.;
    financial={'monthly_volume':month_cases,'labor_rate_per_hour':hourly_rate,
       'gross_saved_minutes_per_eligible_case':saved_minutes,'qa_minutes_per_eligible_case':qa_minutes,
       'additional_minutes_per_wrong_routing':penalty,'one_time_implementation_cost':implementation,
       'annual_software_cost':annual_license,'monthly_released_hours':round(monthly_hours,2),
       'annual_capacity_value':round(annual_capacity_value,2),'first_year_net_capacity_value':round(annual_capacity_value-annual_license-implementation,2),
       'steady_state_annual_net_capacity_value':round(annual_capacity_value-annual_license,2)}
    metric = {
       'notice':'SYNTHETIC DATA AND MODELED ASSUMPTIONS: not historical employer performance or measured causal impact',
       'dataset':{'all':len(df),'train':len(train),'validation':len(valid),'out_of_time_test':len(test),'period':'2023-01 through 2024-05'},
       'operations':{'average_handle_minutes':round(float(df.handle_minutes.mean()),2),
           'reroute_rate':round(float(df.rerouted.mean()),4),
           'sla_breach_rate':round(float(df.sla_breached.mean()),4),
           'incomplete_fields_rate':round(float(df.missing_fields.mean()),4),
           'average_handling_time_rerouted':round(float(df.loc[df.rerouted==1,'handle_minutes'].mean()),2),
           'average_handling_time_first_pass':round(float(df.loc[df.rerouted==0,'handle_minutes'].mean()),2)},
       'model':{'held_out_full_coverage_accuracy':round(float(accuracy_score(test.correct_queue,tpred)),4),
                'held_out_macro_f1':round(float(f1_score(test.correct_queue,tpred,average='macro')),4),
                'selected_threshold':round(chosen_t,3),
                'ai_policy':{k:round(v,4) if isinstance(v,float) else v for k,v in test_policy.items()},
                'rules_policy':{k:round(v,4) if isinstance(v,float) else v for k,v in rule_policy.items()},
                'rules_net_minutes_per_case':round(projected_minutes_per_case(rule_policy),4),
                'ai_net_minutes_per_case':round(projected_minutes_per_case(test_policy),4)},
       'financial':financial,
    }
    (OUT/'metrics.json').write_text(json.dumps(metric,indent=2))
    test_out=test[['case_id','created_at','priority','channel','description','correct_queue','initial_queue','missing_fields','rerouted','handle_minutes','sla_breached']].copy()
    test_out['ai_prediction']=tpred
    test_out['confidence']=tproba.max(axis=1).round(4)
    test_out['ai_route']=np.where((tproba.max(axis=1)>=chosen_t)&(test.priority.to_numpy()=='Standard'),tpred,'Human review')
    test_out['rule_route']=np.where(rule_allowed,rule_pred,'Human review')
    test_out.to_csv(OUT/'out_of_time_predictions.csv',index=False)
    # Export anonymized SQL-ready relational data.
    conn=sqlite3.connect(DATA/'caseflow.db')
    try:
        df.to_sql('cases',conn,if_exists='replace',index=False)
        test_out.to_sql('test_decisions',conn,if_exists='replace',index=False)
    finally: conn.close()
    return metric

if __name__ == '__main__':
    print(json.dumps(main(),indent=2))
