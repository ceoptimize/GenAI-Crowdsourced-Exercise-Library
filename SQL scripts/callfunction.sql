SELECT generate_dynamic_confidence_view_new(
    'JointJointMovement',            -- Main table name
    'JointJointMovementID',          -- Main table ID column
    'JointID',                       -- FK in main table to join with join_table1
    'JointMovementID',               -- FK in main table to join with join_table2
    'Joint',                         -- First join table name
    'JointID',                       -- First join table ID column
    'Joint',                         -- Column to display from the first join table
    'JointMovement',                 -- Second join table name
    'JointMovementID',               -- Second join table ID column
    'JointMovement'                  -- Column to display from the second join table
);