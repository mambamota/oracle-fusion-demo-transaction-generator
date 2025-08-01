-- Final Working Opening Balance Query
-- This query fetches the latest opening balances per bank account from CE_STMT_BALANCES
-- Uses OPBD (Opening Balance) balance code

-- Query 1: Latest Opening Balances per Bank Account
SELECT 
    'LATEST_OPENING_BALANCES' as source_type,
    bank_account_id,
    'OPBD' as balance_type,
    TO_CHAR(balance_date,'YYYY-MM-DD') as balance_date,
    balance_amount as opening_balance,
    TO_CHAR(LAST_UPDATE_DATE,'YYYY-MM-DD') as last_update_date
FROM 
    CE_STMT_BALANCES ce1
WHERE 
    balance_code = 'OPBD'
    AND balance_amount != 0
    AND balance_date = (
        SELECT MAX(balance_date) 
        FROM CE_STMT_BALANCES ce2 
        WHERE ce2.bank_account_id = ce1.bank_account_id 
        AND ce2.balance_code = 'OPBD'
        AND ce2.balance_amount != 0
    )
ORDER BY 
    bank_account_id;

-- Query 2: Daily Opening Balances (for a specific date range)
SELECT 
    'DAILY_OPENING_BALANCES' as source_type,
    bank_account_id,
    'OPBD' as balance_type,
    TO_CHAR(balance_date,'YYYY-MM-DD') as balance_date,
    balance_amount as opening_balance,
    TO_CHAR(LAST_UPDATE_DATE,'YYYY-MM-DD') as last_update_date
FROM 
    CE_STMT_BALANCES
WHERE 
    balance_code = 'OPBD'
    AND balance_amount != 0
    AND balance_date >= TO_DATE('2024-01-01', 'YYYY-MM-DD')
    AND balance_date <= TO_DATE('2024-12-31', 'YYYY-MM-DD')
ORDER BY 
    bank_account_id, balance_date;

-- Query 3: Daily Closing Balances (for comparison)
SELECT 
    'DAILY_CLOSING_BALANCES' as source_type,
    bank_account_id,
    'CLBD' as balance_type,
    TO_CHAR(balance_date,'YYYY-MM-DD') as balance_date,
    balance_amount as closing_balance,
    TO_CHAR(LAST_UPDATE_DATE,'YYYY-MM-DD') as last_update_date
FROM 
    CE_STMT_BALANCES
WHERE 
    balance_code = 'CLBD'
    AND balance_amount != 0
    AND balance_date >= TO_DATE('2024-01-01', 'YYYY-MM-DD')
    AND balance_date <= TO_DATE('2024-12-31', 'YYYY-MM-DD')
ORDER BY 
    bank_account_id, balance_date;

-- Query 4: Opening and Closing Balances Comparison
SELECT 
    op.bank_account_id,
    op.balance_date,
    op.balance_amount as opening_balance,
    cl.balance_amount as closing_balance,
    (cl.balance_amount - op.balance_amount) as daily_change
FROM 
    CE_STMT_BALANCES op
LEFT JOIN 
    CE_STMT_BALANCES cl ON op.bank_account_id = cl.bank_account_id 
    AND op.balance_date = cl.balance_date
    AND cl.balance_code = 'CLBD'
WHERE 
    op.balance_code = 'OPBD'
    AND op.balance_amount != 0
    AND op.balance_date >= TO_DATE('2024-01-01', 'YYYY-MM-DD')
    AND op.balance_date <= TO_DATE('2024-12-31', 'YYYY-MM-DD')
ORDER BY 
    op.bank_account_id, op.balance_date; 