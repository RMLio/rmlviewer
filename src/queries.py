def all_reference_maps_per_ls(ls):
        return f"""
    PREFIX rml: <http://w3id.org/rml/>
    SELECT DISTINCT ?ReferenceMap ?Reference WHERE {{
    ?tm rml:logicalSource <{ls}> .       
    ?tm (<http://example.org>|!<http://example.org>)* ?referenceMap .
    ?ReferenceMap rml:reference ?Reference.
    }}"""

def all_template_maps_per_ls(ls):
        return f"""
    PREFIX rml: <http://w3id.org/rml/>
    SELECT DISTINCT ?TemplateMap ?Template WHERE {{
    ?tm rml:logicalSource <{ls}> .       
    ?tm (<http://example.org>|!<http://example.org>)* ?referenceMap .
    ?TemplateMap rml:template ?Template.
    }}"""