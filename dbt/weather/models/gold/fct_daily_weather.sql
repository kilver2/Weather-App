with daily_weather as (
    select 
        location_id,
        cast(forecast_time as date) as `date`,
        avg(temperature_2m) as average_temperature,
        avg(relative_humidity) as average_humidity,
        avg(windspeed_10m) as average_windspeed,
        sum(precipitation) as sum_precipitation
    from {{ ref('stg_forecast') }}
    group by
        location_id,
        cast(forecast_time as date)
),

daily_air_quality as(
    select
        location_id,
        cast(forecast_time as date) as `date`,
        avg(pm10) as average_pm10,
        avg(pm2_5) as average_pm2_5,
        avg(ozone) as average_ozone,
        avg(nitrogen_dioxide) as average_nitrogen_dioxide
    from {{ ref('stg_air_quality') }}
    group by
        location_id,
        cast(forecast_time as date)
),

all_data_historical as (
    select daily_weather.location_id,
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
        {{ ref('stg_historical') }} as historical
    left join daily_weather on historical.location_id = daily_weather.location_id and 
                                historical.date = daily_weather.date
    left join daily_air_quality on historical.location_id = daily_air_quality.location_id and
                                    historical.date = daily_air_quality.date
),

all_data_historical_location_date as (
    select all_data_historical.location_id,
            all_data_historical.date,
            all_data_historical.average_temperature,
            all_data_historical.average_humidity,
            all_data_historical.average_windspeed,
            all_data_historical.sum_precipitation,
            all_data_historical.average_pm10,
            all_data_historical.average_pm2_5,
            all_data_historical.average_ozone,
            all_data_historical.average_nitrogen_dioxide,
            all_data_historical.temperature_2m_max,
            all_data_historical.temperature_2m_min,
            all_data_historical.precipitation_sum,
            all_data_historical.windspeed_10m_max,
            {{dbt_utils.generate_surrogate_key(['all_data_historical.location_id', 'all_data_historical.date'])}} as daily_weather_sk
        
    from 
        all_data_historical as historical_all
    left join {{ref('dim_location')}} as dim_location on historical_all.location_id = dim_location.location_id
    left join {{ref('dim_date')}} as dim_date on historical_all.date = dim_date.date
)

select *
from
    all_data_historical_location_date

