// // Copyright (c) 2024, Lucky and contributors
// // For license information, please see license.txt

// frappe.query_reports["Custom Total Stock Summary"] = {
// 	"filters": [

// 	]
// };

frappe.query_reports["Custom Total Stock Summary"] = {
    "filters": [
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project"
        },
        {
            "fieldname": "project_start_date",
            "label": __("Project Start Date"),
            "fieldtype": "Date"
        },
        {
            "fieldname": "project_end_date",
            "label": __("Project End Date"),
            "fieldtype": "Date"
        },
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer"
        },
        {
            "fieldname": "customer_product",
            "label": __("Customer Product"),
            "fieldtype": "Link",
            "options": "Item"
        },
        {
            "fieldname": "warehouse",
            "label": __("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse"
        },
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company"
        },
        {
            "fieldname": "project_name",
            "label": __("Project Name"),
            "fieldtype": "Link",
            "options": "Project"
        }
    ]
};
