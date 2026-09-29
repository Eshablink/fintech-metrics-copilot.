select
  borrower_id,
  segment,
  arm,
  simulated,
  company
from {{ source('raw', 'borrowers') }}
