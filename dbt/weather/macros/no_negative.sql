{% test no_negative(model, column_name) %}

with validation as (

    select
        {{ column_name }} as negative_field

    from {{ model }}

),

validation_errors as (

    select
        negative_field

    from validation
    -- if this is true, then even_field is actually odd!
    where (negative_field < 0) 

)

select *
from validation_errors

{% endtest %}