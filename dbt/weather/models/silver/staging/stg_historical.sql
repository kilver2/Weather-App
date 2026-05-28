{{
    config(
        materialized='table',
        unique_key='historical_sk'
    )
}}

with historical as (
    select
        location_id,
        cast(temperature_2m_max as double) as temperature_2m_max,
        cast(temperature_2m_min as double) as temperature_2m_min,
        cast(precipitation_sum as double) as precipitation_sum,
        cast(windspeed_10m_max as double) as windspeed_10m_max,
        cast(ingested_at as timestamp) as ingested_at,
        cast(date as date) as date,
        {{ dbt_utils.generate_surrogate_key(['location_id', 'date']) }}
            as historical_sk
    from
        {{ source('bronze', 'raw_historical') }}
),

ranked_historical as (
    select
        *,
        row_number()
            over (
                partition by historical_sk
                order by ingested_at
            )
            as row_num
    from historical
)

select * except (row_num)
from ranked_historical
where row_num = 1
