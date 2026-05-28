{{
    config(
        materialized='incremental',
        unique_key='date_day'
    )
}}

with date_spine as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2020-01-01' as date)",
        end_date="cast(dateadd(year, 1, current_date) as date)"
    ) }}
)

select
    date_day,
    year(date_day) as year_number,
    month(date_day) as month_number,
    dayofweek(date_day) as day_of_week,
    coalesce(dayofweek(date_day) in (1, 7), false)
        as is_weekend
from date_spine
