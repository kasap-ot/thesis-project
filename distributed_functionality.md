# Types of offers (1st wave features)
- there are GLOBAL and REGIONAL offers
- there will be a checkbox (select options) for the offer-type
- GLOBAL offers are visible to ALL students
- REGIONAL offers are visible ONLY to students in the same region as the offer

# Data storage locations (2nd wave features)
- GLOBAL offers are stored in all 3 regions (3 copies)
- REGIONAL offers are stored only in their region (one copy)

# Types of student-users (3rd wave features)
- there are GLOBAL and REGIONAL students
- GLOBAL students can view GLOBAL offers (all offers) and their REGIONAL offers
- REGIONAL students can only view offers in their region 

# Dilemmas
- should we store country or region information
- it would be good if we can display the location of the offers
- perhaps we can add a field "location" to the offers-table - a basic string
- we can then just keep track of the region in a separate table
- need to consider: how routes, controllers, schemas, tables, and templates will change