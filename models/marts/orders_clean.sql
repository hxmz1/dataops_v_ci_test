select
    customer_id,
    product,
    _row_number,
    _loaded_at,
    order_id,
    order_date,
    country,
    quantity,
    unit_price
from {{ ref('int_orders_checked') }}
where reject_reason is null
