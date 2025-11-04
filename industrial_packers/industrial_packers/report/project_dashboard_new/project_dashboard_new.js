frappe.query_reports["Project dashboard New"] = {
    "filters": [
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project",
            "reqd": 0 
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
            "reqd": 0,
            
            // --- THIS IS THE NEW PART ---
            "get_query": function() {
                var project = frappe.query_report.get_filter_value("project");
                
                // If no project is selected, return an empty query (show all items)
                if (!project) {
                    return {};
                }
                
                // If a project IS selected, filter the Item list
                return {
                    "filters": {
                        // "custom_project_" is the fieldname in the "Item" Doctype
                        // that links to the Project
                        "custom_project_": project
                    }
                };
            }
            // --- END OF NEW PART ---
        }
    ]
};


