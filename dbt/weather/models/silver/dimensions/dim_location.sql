{{ config(materialized='table') }}

with locations as (
    select
        cast(location_id as string) as location_id,
        cast(name as string) as name,
        cast(lat as double) as lat,
        cast(lon as double) as lon,
        cast(country as string) as country,
        cast(timezone as string) as timezone,
        {{ dbt_utils.generate_surrogate_key(['location_id']) }} as location_sk

    from
        {{ ref('locations') }}
)

select *
from locations
