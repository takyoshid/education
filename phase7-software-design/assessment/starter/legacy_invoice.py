from datetime import datetime

INVOICES = {}
EVENTS = []


def create_invoice(invoice_id, customer, items, discount=0):
    if invoice_id in INVOICES:
        raise Exception("duplicate")
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    total = round(subtotal * (1 - discount), 2)
    invoice = {"id": invoice_id, "customer": customer, "items": items, "discount": discount, "total": total, "refunded": 0, "created": datetime.now().isoformat()}
    INVOICES[invoice_id] = invoice
    EVENTS.append(("invoice.created", invoice_id, total))
    return invoice


def refund(invoice_id, amount):
    invoice = INVOICES[invoice_id]
    if amount <= 0:
        raise Exception("bad amount")
    invoice["refunded"] += amount
    EVENTS.append(("invoice.refunded", invoice_id, amount))
    return invoice["refunded"]
