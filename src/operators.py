
import pandas as pd

from namespaces import *
from functions import *

def base_source(source_reference_formulation, source, query):
    df = pd.DataFrame()
    df['<it>'] = [get_iterations(source_reference_formulation, source, query )]
    return df 

def flatten(df, attributes):
    return df.explode(attributes)

def extend(df, function, new_field_attribute):
    df[new_field_attribute] = df.apply(function, axis=1)
    return df 

def left_join(df, dfp, join_condition_attributes):
    dfp = dfp.groupby([parent for (child, parent) in join_condition_attributes]).agg(pd.Series.tolist).reset_index()
    df = df.merge(dfp, how='left', left_on=[attr for (attr, _) in join_condition_attributes],
                      right_on=[attr for (_, attr) in join_condition_attributes])
    return df

def inner_join(df, dfp, join_condition_attributes):
    dfp = dfp.groupby([parent for (child, parent) in join_condition_attributes]).agg(pd.Series.tolist).reset_index()
    df = df.merge(dfp, how='inner', left_on=[attr for (attr, _) in join_condition_attributes],
                      right_on=[attr for (_, attr) in join_condition_attributes])
    return df

