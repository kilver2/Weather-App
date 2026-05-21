with date_spine as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2020-01-01' as date)",
        end_date="cast(current_date as date)"
    ) }}
)

select
    date_day,
    year(date_day) as year,
    month(date_day) as month,
    dayofweek(date_day) as day_of_week,
    case when dayofweek(date_day) in (1,7) then true else false end as is_weekend
from date_spine