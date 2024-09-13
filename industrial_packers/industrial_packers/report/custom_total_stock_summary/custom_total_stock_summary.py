# # Copyright (c) 2024, Lucky and contributors
# # For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data



import frappe
from frappe import _

def execute(filters=None):
    # Define columns
    columns = get_columns()

    # Fetch data from the SQL query with filters
    data = get_data(filters)

    return columns, data

def get_columns():
    # Define the columns that will appear in the report
    return [
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 150},
        {"label": _("Total Quantity"), "fieldname": "total_qty", "fieldtype": "Float", "width": 120},
        {"label": _("Transfer Quantity"), "fieldname": "transfer_qty", "fieldtype": "Float", "width": 120},
        {"label": _("Source Warehouse"), "fieldname": "source_warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
        {"label": _("Target Warehouse"), "fieldname": "target_warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
        {"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("Stock Entry Type"), "fieldname": "stock_entry_type", "fieldtype": "Data", "width": 120},
        {"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
        {"label": _("Project"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150}
    ]

def get_data(filters):
    # Base SQL query
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

    # Apply filters to the query
    conditions = []
    if filters.get("project"):
        conditions.append("se.project = %(project)s")
    if filters.get("project_start_date"):
        conditions.append("se.posting_date >= %(project_start_date)s")
    if filters.get("project_end_date"):
        conditions.append("se.posting_date <= %(project_end_date)s")
    if filters.get("customer"):
        conditions.append("se.customer = %(customer)s")
    if filters.get("customer_product"):
        conditions.append("se_item.item_code = %(customer_product)s")
    if filters.get("warehouse"):
        conditions.append("(se_item.s_warehouse = %(warehouse)s OR se_item.t_warehouse = %(warehouse)s)")
    if filters.get("company"):
        conditions.append("se.company = %(company)s")

    # Combine conditions into query
    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += """
        GROUP BY
            se_item.item_code, it.item_name, se_item.s_warehouse, se_item.t_warehouse,
            se.posting_date, se.stock_entry_type, se.company, se.project
        ORDER BY
            se.posting_date DESC
    """

    # Execute the query and return data
    data = frappe.db.sql(query, filters, as_dict=True)

    return data
