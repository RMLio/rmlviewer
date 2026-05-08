from io import StringIO
import csv
from itertools import product
import json
import jsonpath_ng as jp
from lxml import etree
import re 

from namespaces import *
import algorithm 

def split(template):
    # Find constants and references using regex
    parts = re.findall(r'([^{}]+)|\{([^{}]+)\}', template)
    
    # Build structured list with tags
    result = []
    for constant, reference in parts:
        if constant:
            result.append({'type': 'constant', 'value': constant})
        elif reference:
            result.append({'type': 'reference', 'value': reference})
    
    return result

def convert_template(source_reference_formulation, source_value, template):
    template_parts = split(template) 
    template_part = template_parts[0]
    template_results = []
    if template_part['type'] == 'reference':
        template_results = [str(value) for value in get_expression_evaluation_results(source_reference_formulation, source_value, template_part['value'])]
    else: 
        template_results = [template_part['value']]
    for template_part in template_parts[1:]:    
        if template_part['type'] == 'reference':
            evaluation_results = [str(value) for value in get_expression_evaluation_results(source_reference_formulation, source_value, template_part['value'])]
        else: 
            evaluation_results = [template_part['value']]   
        cross_template_evaluation_results = list(product(template_results, evaluation_results)) 
        template_results = [template_result + evaluation_result for (template_result, evaluation_result) in cross_template_evaluation_results]
    return template_results

def read_source(source_path): 
    with open(source_path, "r", encoding="utf-8") as f:
        source_value = f.read()  
    return source_value

def get_source_and_root_query(ls, g):
    ## add this moment only support to rml:FilePath source and logical view
    reference_formulation = g.value(ls, RML['referenceFormulation'])
    if reference_formulation != None: 
        source_access = g.value(ls, RML['source'])
        source_path = g.value(source_access, RML['path'])
        source = read_source(source_path)
        query = g.value(ls, RML['iterator'])
    else: 
        reference_formulation = RML['LV']
        source = algorithm.translate_view(ls, g)
        query = None    
    return (reference_formulation, source, query)


def get_expression_evaluation_results(source_reference_formulation, source_value, query):  
    if source_reference_formulation == RML['JSONPath']:
        return evalJSONPath(source_value, query)
    if source_reference_formulation == RML['CSV']:
        return evalCSV2(source_value, query)
    if source_reference_formulation == RML['XPath']:
        return evalXpath(source_value, query)
    if source_reference_formulation == RML['LV']:
        return evalLV2(source_value, query)

def get_iterations(source_reference_formulation, source_value, query):  
    if source_reference_formulation == RML['JSONPath']:
        return evalJSONPath(source_value, query)
    if source_reference_formulation == RML['XPath']:
        return evalXpath(source_value, query)
    if source_reference_formulation == RML['CSV']:
        return evalCSV1(source_value)
    if source_reference_formulation == RML['LV']:
        return evalLV1(source_value)
    
def evalXpath(source_value, query):
    if isinstance(source_value, str):
        # this happens in case of switch of reference formulation
        # etree keeps also the context nodes
        source_value = etree.fromstring(source_value)
    iterations = source_value.xpath(query)
    return iterations
    
def evalJSONPath(source_value, query):
    jsonpath = jp.parse(query)
    if isinstance(source_value, str):
        # this happens in case of switch of reference formulation
        source_value = json.loads(source_value)
    iterations = [m.value for m in jsonpath.find(source_value)]
    return iterations

def evalCSV1(source_value):
    csv_file_like = StringIO(source_value)
    reader = csv.DictReader(csv_file_like)
    list_of_dicts = [row for row in reader]
    return list_of_dicts

def evalCSV2(source_value, reference):
    return [source_value[reference]]

def evalLV1(source_value):
    return source_value.to_dict(orient='records')

def evalLV2(source_value, reference):
    return [source_value[reference]] #TODO check if list is needed

def to_index(source_value):
    if isinstance(source_value, list):
        return list(range(len(source_value)))
    else:
        return [0] 


### not used, kept as archive TODO delete
# def get_absolute_fieldname(field, g):
#     absolute_fieldname = g.value(subject=field, predicate=RML['fieldName']).value
#     parent = g.value(predicate=RML['field'], object=field)
#     parent_declared_fieldname = g.value(subject=parent, predicate=RML['fieldName']) 
#     while parent_declared_fieldname != None:
#         absolute_fieldname = parent_declared_fieldname.value + '.' + absolute_fieldname
#         parent = g.value(predicate=RML['field'], object=parent)
#         parent_declared_fieldname = g.value(subject=parent, predicate=RML['fieldName'])
#     return absolute_fieldname    
    