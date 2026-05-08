import pandas as pd
from namespaces import *
from functions import *
from operators import *
#with additional algorithm for extend expression on top of logical views
#kept as archive for further reference, but not used in the main codebase, as it is not fully developed and tested yet
def translate_view(lv, g) -> pd.DataFrame:
    ls = g.value(lv, RML['viewOn'])
    reference_formulation = g.value(ls, RML['referenceFormulation'])
    df = pd.DataFrame()
    if reference_formulation:
        source = g.value(ls, RML['source'])
        source_path = g.value(source, RML['path'])
        query = g.value(ls, RML['iterator'])
        # base source can be reused for resolving logical sources in general, outside logical views
        source_value = read_source(source_path)
        df['<it>'] = [get_iterations(reference_formulation, source_value, query)]
     #   df = base_source(source_path, reference_formulation, query1)
    else: 
        dfs = translate_view(ls, g)
        df['<it>'] = [dfs.to_dict(orient='records')]
        reference_formulation = RML['LV']
    function = lambda x: to_index(x['<it>'])
    df = extend(df, function, '#')
    df = flatten(df, ['#', '<it>'])
    source_function = lambda x: x['<it>']
    fields = g.objects(lv, RML['field'])
    for field in fields:
        field_attribute = g.value(field, RML['fieldName']).value
        df = add_field(field, field_attribute, reference_formulation, source_function, df, g) 
    df = df.drop(columns=['<it>'])
    left_joins = g.objects(lv, RML['leftJoin'])
    for left_join in left_joins:
        df = add_join(left_join, df, g, 'left')
    inner_joins = g.objects(lv, RML['innerJoin'])
    for inner_join in inner_joins:
        df = add_join(inner_join, df, g, 'inner')
    return df

def add_field(field, field_attribute, source_reference_formulation, source_function, df, g):
    function = create_ext_expr_field(field, source_reference_formulation, source_function, g)
    df = extend(df, function, field_attribute)
    function = lambda x: to_index(x[field_attribute])
    df = extend(df, function, field_attribute + '.#')
    df = flatten(df, [field_attribute, field_attribute + '.#'])
    reference_formulation = g.value(field, RML['referenceFormulation']) 
    nested_source_function = lambda x: x[field_attribute]
    fields = g.objects(field, RML['field']) 
    for nested_field in fields:
        nested_field_attribute = field_attribute + '.' + g.value(nested_field, RML['fieldName']).value
        df = add_field(nested_field, nested_field_attribute, reference_formulation, nested_source_function, df, g) 
    if reference_formulation:
        df = df.drop(columns=[field_attribute])
    return df

def create_ext_expr_field(field, source_reference_formulation, source_function, g):
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

def add_join(join, df, g, join_type='left'):
    parent_logical_view = g.value(join, RML['parentLogicalView'])
    dfp = translate_view(parent_logical_view, g)
    child_attributes = df.columns.tolist()
    parent_attributes = []
    source_function = lambda x: x
    fields = g.objects(join, RML['field'])
    for field in fields:
        field_attribute = g.value(field, RML['fieldName']).value
        parent_attributes.append(field_attribute)
        field_attribute = 'f!'+ field_attribute
        function = create_ext_expr_lv(field, g)
        dfp = extend(dfp, function, field_attribute)
    join_attributes = set()
    join_conditions = g.objects(join, RML['joinCondition'])
    for join_condition in join_conditions:  
        jc_attribute = 'c!' +  str(len(join_attributes))
        child_map = g.value(join_condition, RML['childMap'])
        function = create_ext_expr_lv(child_map, g)
        df = extend(df, function, jc_attribute)
        parent_map = g.value(join_condition, RML['parentMap'])
        function = create_ext_expr_lv(parent_map, g)
        dfp = extend(dfp, function, jc_attribute)
        join_attributes.add((jc_attribute, 'p!' + jc_attribute))
    dfp = dfp.add_prefix('p!')
    dfp = dfp.groupby([parent for (child, parent) in join_attributes]).agg(pd.Series.tolist).reset_index()
    if join_type == 'left':
        df = left_join(df, dfp, join_attributes)
    if join_type == 'inner':
        df = inner_join(df, dfp, join_attributes)
    df.columns = [col.removeprefix("p!f!") for col in df.columns] 
    df = df[parent_attributes + child_attributes]    
    for parent_attribute in parent_attributes:
        function = lambda x: to_index(x[parent_attribute])
        df = extend(df, function, parent_attribute + '.#')
        df = flatten(df, [parent_attribute, parent_attribute + '.#'])
    return df

def create_ext_expr_lv(field, g):
    constant = g.value(field, RML['constant'])
    if constant:
        return lambda _: constant.value
    reference = g.value(field, RML['reference'])
    if reference:
        return lambda x: x[reference.value]
    template = g.value(field, RML['template'])
    if template:
        template_parts = split(template.value) 
        template_part = template_parts[0]
        template_results =[]
        for template_part in template_parts:   
            if template_part['type'] == 'reference':
                template_results.push(lambda x: str(x[template_part['value']]))
            else: 
                template_results.push(lambda _: str(template_part['value']))
        return ''.join(template_results)