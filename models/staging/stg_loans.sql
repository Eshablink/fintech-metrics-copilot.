select
  loan_id,
  borrower_id,
  cast(principal_minor as bigint) as principal_minor,
  cast(due_date as date) as due_date,
  cast(origination_date as date) as origination_date,
  simulated,
  company
from {{ source('raw', 'loans') }}
