select
  payment_id,
  exposure_id,
  loan_id,
  cast(amount_minor as bigint) as amount_minor,
  cast(payment_date as date) as payment_date,
  status,
  simulated,
  company
from {{ source('raw', 'payments') }}
