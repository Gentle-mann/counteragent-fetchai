"""CounterAgent charter rules, adapted from src/companies.ts.

Fictional companies and sample trust packs. No legal commitments or money movement.
"""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Vendor:
    key: str
    name: str
    list_price: int
    floor: int
    max_discount: float
    max_payment_days: int
    requires_renewal: bool
    min_uplift: float
    liability_months: int
    trains_on_data: bool
    security_gaps: tuple[str, ...]


VENDORS = {
    "beacon": Vendor("beacon", "Beacon Analytics", 150000, 106000, 25, 60,
                     False, 3, 12, False, ()),
    "quickdash": Vendor("quickdash", "Quickdash", 118000, 96000, 20, 30,
                        True, 9, 3, True,
                        ("SOC2 audit exceptions", "EU residency unconfirmed", "SCIM unavailable")),
}


def finite(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return value


def validate_budget(value):
    value = finite(value, "budget")
    if not 50000 <= value <= 1000000:
        raise ValueError("Annual budget must be between $50,000 and $1,000,000")
    return int(value)


def enforce(vendor: Vendor, proposed: dict):
    """Treat model values as proposals. Private floors never leave this function."""
    price = finite(proposed.get("price"), "price")
    payment = finite(proposed.get("payment_days", 30), "payment_days")
    uplift = finite(proposed.get("uplift_pct", vendor.min_uplift), "uplift_pct")
    renewal = proposed.get("auto_renew", vendor.requires_renewal)
    if not isinstance(renewal, bool):
        raise ValueError("auto_renew must be a boolean")
    minimum = max(vendor.floor, math.ceil(vendor.list_price * (1 - vendor.max_discount / 100)))
    blocks = []
    safe_price = min(vendor.list_price, max(minimum, round(price)))
    if safe_price != round(price):
        blocks.append("Vendor price charter enforced")
    if payment > vendor.max_payment_days:
        blocks.append("Vendor payment-term charter enforced")
    renewal = renewal or vendor.requires_renewal
    return {
        "vendor": vendor.key, "name": vendor.name, "list_price": vendor.list_price,
        "price": safe_price, "seats": 250, "term_months": 24,
        "payment_days": max(1, min(vendor.max_payment_days, round(payment))),
        "auto_renew": renewal, "uplift_pct": max(vendor.min_uplift, uplift) if renewal else 0,
        "liability_months": vendor.liability_months, "trains_on_data": vendor.trains_on_data,
        "security_gaps": list(vendor.security_gaps), "blocks": blocks,
    }


def violations(offer, budget):
    problems = []
    if offer["price"] > budget:
        problems.append("Annual price exceeds buyer budget")
    if offer["payment_days"] < 45:
        problems.append("Payment terms below net 45")
    if offer["auto_renew"] and offer["uplift_pct"] > 3:
        problems.append("Renewal uplift exceeds 3%")
    if offer["liability_months"] < 12:
        problems.append("Liability protection below 12 months")
    if offer["trains_on_data"]:
        problems.append("Vendor trains on customer data")
    problems.extend(offer["security_gaps"])
    return problems


def award(offers, budget):
    reviews = [{"offer": offer, "violations": violations(offer, budget)} for offer in offers]
    cleared = [r["offer"] for r in reviews if not r["violations"]]
    winner = min(cleared, key=lambda o: o["price"]) if cleared else None
    tcv = winner["price"] * winner["term_months"] / 12 if winner else 0
    authority = "finance" if tcv <= 200000 else "orchestrator" if tcv <= 500000 else "human"
    return {"reviews": reviews, "winner": winner, "tcv": tcv, "approval_required": authority}
