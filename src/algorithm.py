import pandas as pd
from namespaces import *
from functions import *
from operators import *


def validate_new_field_name(df, field_attribute, context):
    if field_attribute in df.columns:
        raise ValueError(f"Duplicate field name '{field_attribute}' in {context}.")

def translate_view(lv, g, mapping_dir=None) -> pd.DataFrame:
    ls = g.value(lv, RML['viewOn'])
    (reference_formulation, source, query) = get_source_and_root_query(ls, g, mapping_dir)
    df = base_source(reference_formulation, source, query)
    function = lambda x: to_index(x['<it>'])
    df = extend(df, function, '#')
    df = flatten(df, ['#', '<it>'])
    fields = g.objects(lv, RML['field'])
    for field in fields:
        field_attribute = g.value(field, RML['fieldName']).value
        df = add_field(field, field_attribute, reference_formulation, '<it>', df, g) 
    df = df.drop(columns=['<it>'])
    left_joins = g.objects(lv, RML['leftJoin'])
    for left_join in left_joins:
        df = add_join(left_join, df, g, 'left', mapping_dir)
    inner_joins = g.objects(lv, RML['innerJoin'])
    for inner_join in inner_joins:
        df = add_join(inner_join, df, g, 'inner', mapping_dir)
    return df

def add_field(field, field_attribute, source_reference_formulation, source_attribute, df, g):
    validate_new_field_name(df, field_attribute, 'logical view')
    function = create_ext_expr_field(field, source_reference_formulation, source_attribute, g)
    df = extend(df, function, field_attribute)
    function = lambda x: to_index(x[field_attribute])
    df = extend(df, function, field_attribute + '.#')
    df = flatten(df, [field_attribute, field_attribute + '.#'])
    reference_formulation = g.value(field, RML['referenceFormulation']) 
    fields = g.objects(field, RML['field']) 
    for nested_field in fields:
        nested_field_attribute = field_attribute + '.' + g.value(nested_field, RML['fieldName']).value
        df = add_field(nested_field, nested_field_attribute, reference_formulation, field_attribute, df, g) 
    if reference_formulation:
        df = df.drop(columns=[field_attribute])
    return df

def create_ext_expr_field(field, source_reference_formulation, source_attribute, g):
    source_function = lambda x: x[source_attribute]
    reference_formulation = g.value(field, RML['referenceFormulation'])
    if reference_formulation:
        reference_formulation = g.value(field, RML['referenceFormulation'])
        query1 = g.value(field, RML['iterator'])
        return lambda x: get_iterations(reference_formulation, source_function(x), query1)
    constant = g.value(field, RML['constant'])
    if constant:
        return lambda _: constant.value
    reference = g.value(field, RML['reference'])
    if reference:
        return lambda x: get_expression_evaluation_results(source_reference_formulation, source_function(x), reference.value)
    template = g.value(field, RML['template'])
    if template:
        template_str = template.value
        return lambda x: convert_template(source_reference_formulation, source_function(x), template_str)

def add_join(join, df, g, join_type='left', mapping_dir=None):
    parent_logical_view = g.value(join, RML['parentLogicalView'])
    (reference_formulation, source, query) = get_source_and_root_query(parent_logical_view, g, mapping_dir)
    dfp = base_source(reference_formulation, source, query)
    dfp = flatten(dfp, '<it>')
    child_attributes = df.columns.tolist()
    parent_attributes = []
    fields = g.objects(join, RML['field'])
    for field in fields:
        field_attribute = g.value(field, RML['fieldName']).value
        if field_attribute in child_attributes:
            raise ValueError(f"Duplicate field name '{field_attribute}' between join fields and logical view fields.")
        dfp = add_field(field, field_attribute, RML['LV'], '<it>', dfp, g)
        parent_attributes.append(field_attribute)
    df['<lv>'] =df.to_dict(orient='records')
    join_attributes = set()
    join_conditions = g.objects(join, RML['joinCondition'])
    for join_condition in join_conditions:  
        jc_attribute = 'c!' +  str(len(join_attributes))
        child_map = g.value(join_condition, RML['childMap'])
        df = add_field(child_map, jc_attribute, RML['LV'], '<lv>', df, g) 
        parent_map = g.value(join_condition, RML['parentMap'])
        dfp = add_field(parent_map, 'p!' + jc_attribute, RML['LV'], '<it>', dfp, g)   
        join_attributes.add((jc_attribute, 'p!' + jc_attribute))
    if join_type == 'left':
        df = left_join(df, dfp, join_attributes)
    if join_type == 'inner':
        df = inner_join(df, dfp, join_attributes)
    df = df[child_attributes + parent_attributes]
    for parent_attribute in parent_attributes:
        function = lambda x: to_index(x[parent_attribute])
        df = extend(df, function, parent_attribute + '.#')
        df = flatten(df, [parent_attribute, parent_attribute + '.#'])
    return df
