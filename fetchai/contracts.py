"""Fictional contracting artifacts, actual uAgent cryptographic signatures.

These demonstrate integrity and delegated approval, not legal corporate identity.
"""
import json
from pathlib import Path
from uagents_core.identity import Identity
from governance import digest

TERMS_VERSION='SAAS-DEMO-2026-v1'
SOURCES={
 'subscription_billing':'https://www.salesforce.com/en-us/wp-content/uploads/sites/4/documents/legal/salesforce_MSA.pdf',
 'document_structure':'https://www.salesforce.com/company/legal/customer-agreements/',
 'order_form_and_disputes':'https://www.snowflake.com/en/legal/terms-of-service/',
 'services_scope':'https://handbook.gitlab.com/handbook/sales/field-operations/sales-operations/deal-desk/',
}

def payment_plan(offer):
    annual=offer['price']
    if type(annual) is not int or annual<=0 or offer['term_months']!=24:
        raise ValueError('Expected an annual price and 24-month term')
    return {'billing_frequency':'annual_in_advance','currency':'USD','term_months':24,
        'total_contract_commitment':annual*2,'amount_due_at_signature':0,
        'first_invoice_amount':annual,'payment_terms_days':offer['payment_days'],
        'deposit':0,'separate_implementation_fee':0,'tax_amount':0,
        'tax_basis':'fictional approved tax-exempt vendor-master record',
        'invoices':[{'period':'year_1','service_month_start':0,'service_month_end':12,
                     'invoice_month':0,'due_days_after_invoice':offer['payment_days'],'amount':annual},
                    {'period':'year_2','service_month_start':12,'service_month_end':24,
                     'invoice_month':12,'due_days_after_invoice':offer['payment_days'],'amount':annual}],
        'remediation_fee_included_in_each_annual_invoice':offer.get('remediation_annual_cost',0),
        'credit_activation':'Signed order, approved credit and undisputed invoice permit onboarding before invoice due date.',
        'demo_execution':'Payment messages replay the first invoice at its due day; no real funds move. Year two remains scheduled.'}

def unsigned_bundle(deal_id,offer,revision=0):
    return {'document_id':deal_id+'-r'+str(revision),'deal_id':deal_id,'revision':revision,
        'terms_version':TERMS_VERSION,'fictional_demo_only':True,
        'parties':{'buyer':'Acme (fictional)','vendor':offer['name']},
        'order_form':{'vendor_key':offer['vendor'],'seats':offer['seats'],'term_months':offer['term_months'],
            'annual_subscription_fee':offer['price'],'currency':'USD','remediation_included':offer.get('remediation',False),
            'remediation_annual_fee':offer.get('remediation_annual_cost',0),'implementation_days':offer.get('implementation_days',7),
            'evidence_revision':offer.get('evidence_revision','BASE-v1'),'payment_plan':payment_plan(offer)},
        'msa':{'liability_months_of_fees':offer['liability_months'],'auto_renew':offer['auto_renew'],
            'renewal_uplift_cap_pct':offer['uplift_pct'],'price_fixed_for_current_24_month_term':True,
            'scope_change_requires_signed_amendment':True,'invoice_dispute_holds_disputed_amount_only':True,
            'purchase_order_cannot_silently_amend_signed_terms':True},
        'dpa_security_addendum':{'data_region':'EU' if not offer['security_gaps'] else 'unconfirmed',
            'training_on_customer_data':offer['trains_on_data'],'scim_required':True,'saml_required':True,
            'evidence_revision':offer.get('evidence_revision','BASE-v1')},
        'implementation_sow':{'separate_fee':0,'included_in_subscription':True,'pilot_seats':25,'rollout_seats':225,
            'acceptance_checks':['EU tenant region','SAML login','SCIM create/deactivate','250 entitlements'],
            'additional_paid_services_require_separate_sow_and_approval':True},
        'research_sources':SOURCES}

def sign_bundle(agent,bundle,role):
    hashed=digest(bundle)
    return {'role':role,'signer_address':agent.address,'document_hash':hashed,
        'algorithm':'uAgents secp256k1 / SHA-256','signature':agent.sign_digest(bytes.fromhex(hashed)),
        'scope':'fictional document approval only'}

def verify_signature(bundle,receipt,expected_address,role):
    try:
        hashed=digest(bundle)
        return (receipt.get('role')==role and receipt.get('signer_address')==expected_address
            and receipt.get('document_hash')==hashed
            and Identity.verify_digest(expected_address,bytes.fromhex(hashed),receipt['signature']))
    except Exception:
        return False

def verify_packet(packet,buyer_address,vendor_address):
    bundle=packet.get('bundle',{})
    signatures=packet.get('signatures',{})
    return all(verify_signature(bundle,signatures.get(role,{}),address,role)
        for role,address in [('buyer',buyer_address),('vendor',vendor_address)])

def packet_path(root,packet):
    b=packet['bundle']
    return Path(root)/'.runtime'/'contracts'/(b['document_id']+'-'+digest(b)[:12]+'.json')

def store_packet(root,packet):
    path=packet_path(root,packet)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(packet,indent=2),encoding='utf-8')
    return '/documents/'+packet['bundle']['deal_id']+'/'+str(packet['bundle']['revision'])+'/'+digest(packet['bundle'])[:12]
