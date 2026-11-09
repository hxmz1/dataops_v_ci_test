-- The six quality rules from TP1 and TP2. The first rule that matches wins.
select
    customer_id,
    product,
    _row_number,
    _loaded_at,
    order_id,
    order_date,
    country,
    quantity,
    unit_price,
    case
        when customer_id is null then 'missing_customer_id'
        when order_date is null then 'invalid_date'
        when quantity is null or quantity <= 0 then 'invalid_quantity'
        -- Rules 4, 5 and 6 go here.
        --Règle 4 — Vérification du prix
        when
            unit_price is null
            or unit_price not between 0.01 and 1000
            then 'invalid_unit_price'
        --Règle 5 — Détection des doublons
        when
            row_number() over (
                partition by order_id
                order by _row_number
            ) > 1
            then 'duplicate_order_id'
        --Règle 6 — Vérification du pays
        when country not in ('France', 'Germany', 'Italy', 'Morocco', 'Tunisia')
            then 'unknown_country'
    end as reject_reason
from {{ ref('stg_orders') }}
