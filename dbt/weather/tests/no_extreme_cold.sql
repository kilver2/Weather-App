select *
from {{ ref('stg_historical') }}
where temperature_2m_min < -100.0