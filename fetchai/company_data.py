"""Versioned fictional ERP/HRIS/security records and department-scoped tools."""
from copy import deepcopy
import hashlib
import json

VERSION='acme-2026-10-24-v1'
TEAMS=[('Product Analytics',80,36000),('Engineering',65,30000),('Revenue Operations',45,21000),('Operations',35,18000),('Finance',25,15000)]

def records():
    employees=[]
    for team,count,budget in TEAMS:
        for _ in range(count):
            i=len(employees)+1
            employees.append({'id':f'E{i:04}', 'department':team,'cost_center':'CC'+str(TEAMS.index((team,count,budget))+100),
                'region':'EU' if i%4==0 or i in (1,2) else 'US',
                'analytics_active_30d':not (i%7==0 or i in (247,248,249)),'employment_status':'active'})
    return {'version':VERSION,'synthetic':True,'employees':employees,
        'legacy_scim_snapshot':{'as_of':'2026-10-01','employee_ids':[e['id'] for e in employees[:242]]},
        'department_budgets':[{'department':t,'seats':n,'annual_allocation':b} for t,n,b in TEAMS],
        'growth_forecast':{'current_seats':250,'next_year_demand':270,'incremental_seats_not_yet_approved':20},
        'cash_forecast':{'opening_cash':2400000,'payroll_30d':1100000,'committed_payables_30d':620000,'reserve_floor':500000,'annual_cost_of_capital_pct':8},
        'contract_history':[{'year':2024,'seats':220,'annual_fee':105600,'discount_pct':20,'scope':'analytics'},
                            {'year':2025,'seats':250,'annual_fee':120000,'discount_pct':20,'scope':'analytics'}],
        'data_assets':[{'system':'Warehouse','region':'EU','classification':'confidential','personal_data':True},
                       {'system':'CRM','region':'US','classification':'restricted','personal_data':True},
                       {'system':'Product events','region':'EU','classification':'confidential','personal_data':False}],
        'security_requirements':{'eu_users':64,'scim_required':True,'sso_required':True,'model_training_allowed':False,'unresolved_audit_exceptions_allowed':0},
        'contract_playbook':[{'id':'CL-01','control':'liability_months','minimum':12,'waivable':False},
                             {'id':'CL-02','control':'renewal_uplift_pct','maximum':3,'waivable':False},
                             {'id':'CL-03','control':'net_payment_days','minimum':45,'waivable':False}],
        'vendor_master':{'beacon':{'id':'V-100','approved_bank_last4':'4417','currency':'USD','tax_status':'sample-exempt','status':'approved'},
                         'quickdash':{'id':'V-200','approved_bank_last4':'2290','currency':'USD','tax_status':'sample-exempt','status':'conditional'}},
        'bank_change_tickets':[{'id':'AP-481','vendor':'beacon','requested_last4':'9911','status':'unverified','action':'hold; verify through existing contact'}],
        'invoice_history':[{'reference':'INV-2025-BEACON','vendor':'beacon','annual_amount':120000,'status':'paid'},
                           {'reference':'INV-2025-QUICKDASH','vendor':'quickdash','annual_amount':118000,'status':'rejected-no-po'}],
        'onboarding':{'region':'EU','sso':'SAML','scim':True,'pilot_seats':25,'rollout_seats':225,'rollback':'disable connector and revoke service token'}}

SCOPES={
 'research':['employees','department_budgets','growth_forecast','contract_history'],
 'procurement':['department_budgets','contract_history','growth_forecast'],
 'security':['data_assets','security_requirements'],
 'legal':['contract_playbook','data_assets'],
 'finance':['department_budgets','cash_forecast','contract_history'],
 'ap':['vendor_master','bank_change_tickets','invoice_history'],
 'it':['employees','legacy_scim_snapshot','onboarding'],
 'orchestrator':['department_budgets','growth_forecast','contract_playbook'],
}

def department_context(role):
    data=records()
    scoped={key:deepcopy(data[key]) for key in SCOPES[role]}
    if 'employees' in scoped:
        people=scoped.pop('employees')
        scoped['workforce_rollup']={'eligible_employees':len(people),'active_analytics_users':sum(p['analytics_active_30d'] for p in people),
            'eu_employees':sum(p['region']=='EU' for p in people),'departments':len(TEAMS),'source':'HRIS authoritative 2026-10-24'}
    if role=='it':
        old=set(scoped.pop('legacy_scim_snapshot')['employee_ids'])
        missing=[e['id'] for e in data['employees'] if e['id'] not in old]
        scoped['directory_reconciliation']={'legacy_count':len(old),'authoritative_count':len(data['employees']),
            'missing_from_legacy':missing,'resolution':'Use the newer HRIS roster; add eight validated employees to the rollout plan.'}
    return {'dataset_version':VERSION,'synthetic':True,'records':scoped,
        'receipt':hashlib.sha256(json.dumps(scoped,sort_keys=True).encode()).hexdigest()}

def tools(role,payload):
    context=department_context(role)
    data=records()
    output={'dataset_version':VERSION,'source_receipt':context['receipt']}
    if role in ('research','procurement'):
        output.update(eligible_seats=250,active_seats=212,unused_now=38,forecast_demand=270,
            decision='Keep the approved 250 seats: current utilization alone does not justify reducing required scope; 20 growth seats require a separate approval.')
    elif role=='security':
        output.update(eu_users=64,personal_data_systems=2,required_controls=['EU residency','SCIM','SAML','no model training'],
            decision='Residency and access controls are mandatory because employee access and personal-data systems are in scope.')
    elif role=='legal':
        output.update(non_waivable_clauses=[r['id'] for r in data['contract_playbook']],
            decision='Compare each clause with the final structured quote and Security clearance; sales assurances cannot waive the playbook.')
    elif role=='finance':
        c=data['cash_forecast']; headroom=c['opening_cash']-c['payroll_30d']-c['committed_payables_30d']-c['reserve_floor']
        output.update(allocated_annual_budget=sum(r['annual_allocation'] for r in data['department_budgets']),liquidity_above_reserve_before_purchase=headroom,
            net10_exception_permitted=False,decision='Separate annual expense from two-year commitment; do not exchange binding net-45 terms for an unapproved early-payment discount.')
    elif role=='ap':
        winner=payload['winner']; master=data['vendor_master'][winner['vendor']]
        output.update(approved_bank_last4=master['approved_bank_last4'],unverified_bank_changes=[t['id'] for t in data['bank_change_tickets'] if t['vendor']==winner['vendor']],
            prior_paid_invoice_references=[r['reference'] for r in data['invoice_history'] if r['status']=='paid'],
            decision='Hold the bank-change request; match this invoice to the approved bank record and independently countersigned order.')
    elif role=='it':
        output.update(context['records']['directory_reconciliation'])
        output.update(pilot_seats=25,rollout_seats=225,eu_users=64,decision='Reconcile the stale SCIM snapshot against authoritative HRIS, then stage 25 pilot seats and 225 rollout seats.')
    return context,output
