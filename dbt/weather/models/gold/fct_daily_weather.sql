with daily_weather as (
    select
        location_id,
        cast(forecast_time as date) as date,
        avg(temperature_2m) as average_temperature,
        avg(relative_humidity) as average_humidity,
        avg(windspeed_10m) as average_windspeed,
        sum(precipitation) as sum_precipitation
    from {{ ref('stg_forecast') }}
    group by
        location_id,
        cast(forecast_time as date)
),

daily_air_quality as (
    select
        location_id,
        cast(measured_at as date) as date,
        avg(pm10) as average_pm10,
        avg(pm2_5) as average_pm2_5,
        avg(ozone) as average_ozone,
        avg(nitrogen_dioxide) as average_nitrogen_dioxide
    from {{ ref('stg_air_quality') }}
    group by
        location_id,
        cast(measured_at as date)
),

all_data_historical as (
    select
        daily_weather.location_id,
        daily_weather.date,
        daily_weather.average_temperature,
        daily_weather.average_humidity,
        daily_weather.average_windspeed,
        daily_weather.sum_precipitation,
        daily_air_quality.average_pm10,
        daily_air_quality.average_pm2_5,
        daily_air_quality.average_ozone,
        daily_air_quality.average_nitrogen_dioxide,
        historical.temperature_2m_max,
        historical.temperature_2m_min,
        historical.precipitation_sum,
        historical.windspeed_10m_max
    from
        daily_weather
    left join daily_air_quality
        on
            daily_weather.location_id = daily_air_quality.location_id
            and daily_weather.date = daily_air_quality.date
    left join {{ ref('stg_historical') }}
        as historical on daily_weather.location_id = historical.location_id
    and daily_weather.date = historical.date
),

all_data_historical_location_date as (
    select
        historical_all.location_id,
        historical_all.date,
        historical_all.average_temperature,
        historical_all.average_humidity,
        historical_all.average_windspeed,
        historical_all.sum_precipitation,
        historical_all.average_pm10,
        historical_all.average_pm2_5,
        historical_all.average_ozone,
        historical_all.average_nitrogen_dioxide,
        historical_all.temperature_2m_max,
        historical_all.temperature_2m_min,
        historical_all.precipitation_sum,
        historical_all.windspeed_10m_max,
        {{ dbt_utils.generate_surrogate_key(['historical_all.location_id', 'historical_all.date']) }}
            as daily_weather_sk

    from
        all_data_historical as historical_all
    left join
        {{ ref('dim_location') }} as dim_location
        on historical_all.location_id = dim_location.location_id
    left join
        {{ ref('dim_date') }} as dim_date
        on historical_all.date = dim_date.date_day
)

select *
from
    all_data_historical_location_date
