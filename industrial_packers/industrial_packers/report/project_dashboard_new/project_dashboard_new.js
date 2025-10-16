frappe.query_reports["Project dashboard New"] = {
    "filters": [
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project",
            "reqd": 0 // This makes the filter optional
        },
        {
            "fieldname": "warehouse",
            "label": __("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse",
            "reqd": 0 
        },
        {
            "fieldname": "item",
            "label": __("Item"),
            "fieldtype": "Link",
            "options": "Item",
            "reqd": 0
        }
    ]
};

