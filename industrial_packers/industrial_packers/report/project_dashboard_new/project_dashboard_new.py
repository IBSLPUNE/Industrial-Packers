# Copyright (c) 2024, your_company_name and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, getdate

def execute(filters=None):
    """
    Main function to execute the report.
    Gathers columns and data based on the provided filters.
    """
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)
    
    return columns, data

def get_columns():
    """Defines the columns that will be displayed in the report."""
    return [
        {"fieldname": "item_code", "label": "Item Code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 200},
        {"fieldname": "warehouse", "label": "Warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
        {"fieldname": "actual_qty", "label": "Actual Qty", "fieldtype": "Float", "width": 100},
        {"fieldname": "stock_uom", "label": "UOM", "fieldtype": "Link", "options": "UOM", "width": 100},
        # --- NEW COLUMNS ADDED HERE ---
        {"fieldname": "project_start_date", "label": "Project Start Date", "fieldtype": "Date", "width": 120},
        {"fieldname": "project_end_date", "label": "Project End Date", "fieldtype": "Date", "width": 120},
        # Ageing Buckets based on FIFO
        {"fieldname": "age_0_30", "label": "0-30 Days", "fieldtype": "Float", "width": 100},
        {"fieldname": "age_31_60", "label": "31-60 Days", "fieldtype": "Float", "width": 100},
        {"fieldname": "age_61_90", "label": "61-90 Days", "fieldtype": "Float", "width": 100},
        {"fieldname": "age_91_above", "label": "91+ Days", "fieldtype": "Float", "width": 100},
        # Project Details
        {"fieldname": "project", "label": "Project", "fieldtype": "Link", "options": "Project", "width": 150},
    ]

def get_data(filters):
    """Fetches and processes the data for the report."""
    data = []
    today = getdate()

    # --- Build SQL conditions from filters ---
    conditions = ""
    filter_values = {}

    if filters.get("item"):
        conditions += " AND b.item_code = %(item)s"
        filter_values["item"] = filters.get("item")

    if filters.get("warehouse"):
        conditions += " AND b.warehouse = %(warehouse)s"
        filter_values["warehouse"] = filters.get("warehouse")
        
    if filters.get("project"):
        conditions += " AND i.custom_project_ = %(project)s"
        filter_values["project"] = filters.get("project")

    # --- Get current stock balances from the Bin table ---
    # --- QUERY MODIFIED TO INCLUDE PROJECT DATES ---
    bin_stock_query = f"""
        SELECT
            b.item_code,
            i.item_name,
            b.warehouse,
            b.actual_qty,
            i.stock_uom,
            i.custom_project_ as project,
            p.expected_start_date,
            p.expected_end_date
        FROM
            `tabBin` b
        JOIN
            `tabItem` i ON b.item_code = i.name
        LEFT JOIN
            `tabProject` p ON i.custom_project_ = p.name
        WHERE
            b.actual_qty > 0.001
            {conditions}
        ORDER BY
            b.item_code, b.warehouse
    """
    bin_stock_list = frappe.db.sql(bin_stock_query, filter_values, as_dict=1)
    
    # --- FIFO Ageing Calculation ---
    for item_bin in bin_stock_list:
        qty_to_distribute = item_bin.actual_qty
        
        ageing_buckets = {
            "age_0_30": 0,
            "age_31_60": 0,
            "age_61_90": 0,
            "age_91_above": 0,
        }

        incoming_entries = frappe.db.sql(
            """
                SELECT
                    posting_date,
                    actual_qty
                FROM
                    `tabStock Ledger Entry`
                WHERE
                    item_code = %(item_code)s
                    AND warehouse = %(warehouse)s
                    AND actual_qty > 0
                    AND docstatus = 1
                ORDER BY
                    posting_date DESC, posting_time DESC
            """,
            {"item_code": item_bin.item_code, "warehouse": item_bin.warehouse},
            as_dict=1,
        )
        
        if not incoming_entries:
            ageing_buckets["age_91_above"] = qty_to_distribute
        else:
            for entry in incoming_entries:
                if qty_to_distribute <= 0:
                    break

                age = (today - getdate(entry.posting_date)).days
                qty_from_this_entry = min(qty_to_distribute, entry.actual_qty)

                if 0 <= age <= 30:
                    ageing_buckets["age_0_30"] += qty_from_this_entry
                elif 31 <= age <= 60:
                    ageing_buckets["age_31_60"] += qty_from_this_entry
                elif 61 <= age <= 90:
                    ageing_buckets["age_61_90"] += qty_from_this_entry
                else:
                    ageing_buckets["age_91_above"] += qty_from_this_entry
                
                qty_to_distribute -= qty_from_this_entry

        # --- Append the processed row to the final data list ---
        # --- ROW MODIFIED TO INCLUDE PROJECT DATES ---
        row = {
            "item_code": item_bin.item_code,
            "item_name": item_bin.item_name,
            "warehouse": item_bin.warehouse,
            "actual_qty": item_bin.actual_qty,
            "stock_uom": item_bin.stock_uom,
            "project_start_date": item_bin.expected_start_date,
            "project_end_date": item_bin.expected_end_date,
            "project": item_bin.project,
            **ageing_buckets
        }
        data.append(row)
        
    return data


