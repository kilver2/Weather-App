with forecast as (
    select
        location_id,
        cast(forecast_time as timestamp)        as forecast_time,
        cast(temperature_2m as double)          as temperature_2m,
        cast(precipitation as double)           as precipitation,
        cast(windspeed_10m as double)           as windspeed_10m,
        cast(relativehumidity_2m as int)        as relative_humidity,
        cast(ingested_at as timestamp)          as ingested_at,
        {{ dbt_utils.generate_surrogate_key(['location_id', 'forecast_time']) }} as forecast_sk
    from {{ source('bronze', 'raw_forecast') }}
),

ranked_forecast as (
    select
        *,
        ROW_NUMBER() over (
            partition by forecast_sk
            order by ingested_at desc
        ) as row_num
    from forecast
)

select * except(row_num)
from ranked_forecast
where row_num = 1