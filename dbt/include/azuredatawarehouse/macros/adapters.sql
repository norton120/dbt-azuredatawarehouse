{% macro azuredatawarehouse__list_schemas(database) %}
    {% call statement('list_schemas', fetch_result=True, auto_begin=False) -%}
        SELECT DISTINCT schema_name
        FROM "{{ database }}".information_schema.schemata
        WHERE catalog_name = '{{ database }}'
    {%- endcall %}

    {{ return(load_result('list_schemas').table) }}
{% endmacro %}

{% macro azuredatawarehouse__create_schema(database_name, schema_name, auto_begin=False) %}
    {% call statement('create_schema') -%}
        CREATE SCHEMA {{ schema_name }}
    {%- endcall %}
{% endmacro %}

{% macro azuredatawarehouse__drop_relation(relation) -%}
    {% call statement('drop_relation', auto_begin=False) -%}
        if object_id('{{ relation.schema }}.{{ relation.identifier }}') is not null
	        DROP {{ relation.type }} {{ relation.schema }}.{{ relation.identifier }}
    {%- endcall %}
{% endmacro %}

{% macro azuredatawarehouse__truncate_relation(relation) -%}
    {% call statement('truncate_relation') -%}
        TRUNCATE TABLE {{ relation }}
    {%- endcall %}
{% endmacro %}

{% macro azuredatawarehouse__check_schema_exists(database, schema) -%}
    {% call statement('check_schema_exists', fetch_result=True, auto_begin=False) -%}
        SELECT 
            decode(count(*), 0, null)
        FROM 
            {{ database }}.information_schema.schemata
        WHERE 
            catalog_name    = '{{ database }}'
            and schema_name = '{{ schema }}'
    {%- endcall %}

    {{ return(load_result('check_schema_exists').table) }}
{% endmacro %}

{% macro azuredatawarehouse__list_relations_without_caching(information_schema, schema) %}
    {% call statement('list_relations_without_caching', fetch_result=True) %}
        SELECT
            '{{ information_schema.database }}' as "database"
            , table_name as name
            , table_schema as "schema"
            , case 
                when table_type = 'BASE TABLE'
                    then 'table'
                else lower(table_type)
            end as type
        FROM 
            {{ information_schema.database }}.information_schema.TABLES
        WHERE 
            table_schema = '{{ schema }}'
    {% endcall %}

    {{ return(load_result('list_relations_without_caching').table) }}
{% endmacro %}

{% macro azuredatawarehouse__create_table_as(temporary, relation, sql) -%}
    {%- set temp_view_indentifier = relation.identifier + '_dbtazuredatawarehouse_tmp' -%}
    {%- set temp_view_sql = sql.replace("'", "''") -%}

    if object_id('{{ temp_view_indentifier }}') is not null
	    drop view {{ temp_view_indentifier }};

    exec('create view {{ relation.schema }}.{{ temp_view_indentifier }} as {{ temp_view_sql }}');

    SELECT * 
    into {{ relation.schema }}.{% if temporary: -%}#{%- endif %}{{ relation.identifier }} 
    FROM {{ relation.schema }}.{{ temp_view_indentifier }};

    drop view {{ relation.schema }}.{{ temp_view_indentifier }};
{% endmacro %}

{% macro azuredatawarehouse__create_view_as(relation, sql, auto_begin=False) -%}
    create view {{ relation.schema }}.{{ relation.identifier }} as
    {{ sql }};
{%- endmacro %}

{% macro azuredatawarehouse__rename_relation(FROM_relation, to_relation) -%}
  {% call statement('rename_relation') -%}
    EXEC sp_rename '{{ FROM_relation.schema }}.{{ FROM_relation.identifier }}', '{{ to_relation.identifier }}'
  {%- endcall %}
{% endmacro %}

{% macro azuredatawarehouse__get_columns_in_relation(relation) -%}
    {% call statement('get_columns_in_relation', fetch_result=True) %}
        SELECT 
            column_name
            , data_type
            , character_maximum_length
            , numeric_precision
            , numeric_scale
        FROM 
            information_schema.columns
        WHERE 
            table_catalog    = '{{ relation.database }}'
            and table_schema = '{{ relation.schema }}'
            and table_name   = '{{ relation.identifier }}'
    {% endcall %}

    {% set table = load_result('get_columns_in_relation').table %}
    {{ return(sql_convert_columns_in_relation(table)) }}
{% endmacro %}
