import frappe
from frappe import _

def execute(filters=None):
    # Ensure get_columns is defined
    columns = get_columns()

    # Fetch data from the SQL query with filters
    data = get_data(filters)

    

    return columns, data

def get_columns():
    # Define the columns that will appear in the report
    return [
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 150},
        {"label": _("Transfer Quantity"), "fieldname": "transfer_qty", "fieldtype": "Float", "width": 120},
        {"label": _("Source Warehouse"), "fieldname": "source_warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
        {"label": _("Target Warehouse"), "fieldname": "target_warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
        {"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("Stock Entry Type"), "fieldname": "stock_entry_type", "fieldtype": "Data", "width": 120},
        {"label": _("ID"), "fieldname": "name", "fieldtype": "Link", "options": "Stock Entry","width": 120},
        {"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
        {"label": _("Project"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},
    ]

def get_data(filters):
    filters = filters or {}
    query = """
        SELECT
            se_item.item_code AS item_code,
            it.item_name AS item_name,
            SUM(se_item.qty) AS total_qty,
            SUM(se_item.transfer_qty) AS transfer_qty,
            se_item.s_warehouse AS source_warehouse,
            se_item.t_warehouse AS target_warehouse,
            se.posting_date AS posting_date,
            se.stock_entry_type AS stock_entry_type,
            se.company AS company,
            se.name,
            se.project AS project
        FROM
            `tabStock Entry` se
        LEFT JOIN
            `tabStock Entry Detail` se_item ON se.name = se_item.parent
        LEFT JOIN
            `tabItem` it ON se_item.item_code = it.item_code
        WHERE
            se.docstatus = 1
    """

    conditions = []
    if filters.get("project"):
        conditions.append("se.project = %(project)s")
    if filters.get("customer"):
        conditions.append("se.customer = %(customer)s")
    if filters.get("customer_product"):
        conditions.append("se_item.item_code = %(customer_product)s")
    if filters.get("company"):
        conditions.append("se.company = %(company)s")
    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("se.posting_date BETWEEN %(from_date)s AND %(to_date)s")
    elif filters.get("from_date"):
        conditions.append("se.posting_date >= %(from_date)s")
    elif filters.get("to_date"):
        conditions.append("se.posting_date <= %(to_date)s")

    # Add condition for the checkbox filter
    if filters.get("show_transit_warehouses") == 1:
        conditions.append("se_item.t_warehouse LIKE %(transit_filter)s")
        filters["transit_filter"] = "Transit%"

    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += """
        GROUP BY
            se_item.item_code, it.item_name, se_item.s_warehouse, se_item.t_warehouse,
            se.posting_date, se.stock_entry_type, se.company, se.project
        ORDER BY
            se.posting_date DESC
    """
    
    data = frappe.db.sql(query, filters, as_dict=True)
    return data

