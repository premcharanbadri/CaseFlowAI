from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'
m=json.loads((OUT/'metrics.json').read_text())
cases=pd.read_csv(ROOT/'data'/'synthetic_cases.csv')
v=pd.read_csv(OUT/'validation_thresholds.csv')
plt.rcParams.update({'font.size':11,'axes.titlesize':14,'figure.dpi':130})

summary=cases.groupby('rerouted')['handle_minutes'].agg(['mean','count'])
fig,ax=plt.subplots(figsize=(7.5,4.1))
ax.bar(['Correct first route','Misrouted'],summary['mean'])
ax.set_ylabel('Average human handling time (minutes)')
ax.set_title('Root-cause diagnostic: misrouted cases take longer')
for i,h in enumerate(summary['mean']): ax.text(i,h+.15,f'{h:.1f} min',ha='center')
ax.set_ylim(0,max(summary['mean'])*1.22)
fig.tight_layout()
fig.savefig(OUT/'root_cause.png')
plt.close(fig)

fig,ax=plt.subplots(figsize=(8.5,4.5))
ax.plot(v.coverage*100,v.precision_routed*100,marker='o',label='ML threshold policy')
ax.axhline(97,ls='--',label='97% precision guardrail')
ax.set_xlabel('Coverage: % all cases suggested')
ax.set_ylabel('Precision among suggested cases (%)')
ax.set_title('Accuracy versus coverage: abstention creates value')
ax.set_ylim(90,101.5)
ax.legend(loc='lower left')
fig.tight_layout()
fig.savefig(OUT/'precision_coverage.png')
plt.close(fig)

fig,ax=plt.subplots(figsize=(7.5,4.5))
labels=['Rules-assisted','AI-assisted']
val=[m['model']['rules_net_minutes_per_case'],m['model']['ai_net_minutes_per_case']]
ax.bar(labels,val)
ax.set_ylabel('Expected net minutes saved per incoming case')
ax.set_title('Modeled value after QA and routing-error penalty')
for i,h in enumerate(val): ax.text(i,h+.04,f'{h:.2f} min',ha='center')
ax.set_ylim(0,max(val)*1.2)
fig.tight_layout()
fig.savefig(OUT/'rules_vs_ai_value.png')
plt.close(fig)
