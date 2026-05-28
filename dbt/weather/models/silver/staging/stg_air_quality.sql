{{
    config(
        materialized='incremental',
        unique_key='air_quality_sk'
    )
}}

with air_quality as (
    select  
        location_id,
        cast(pm10 as double) as pm10,
        cast(pm2_5 as double) as pm2_5,
        cast(ozone as double) as ozone,
        cast(nitrogen_dioxide as double) as nitrogen_dioxide,
        cast(measured_at as timestamp) as measured_at,
        cast(ingested_at as timestamp) as ingested_at,
        {{ dbt_utils.generate_surrogate_key(['location_id', 'measured_at']) }} as air_quality_sk
    
    from
        {{ source('bronze', 'raw_air_quality') }}
),

ranked_air_quality as(
    select
        *,
        ROW_NUMBER() over (
            partition by air_quality_sk
            order by ingested_at desc
        )
        as row_num
    from air_quality
)

select * except(row_num)
from ranked_air_quality
where row_num = 1