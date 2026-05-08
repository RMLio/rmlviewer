"""
This module holds the View-to-CSV-Convertor class which is responsible for converting an RML mapping containing views
to an RML mapping without views. All views are materialized as CSV files and added to the resulting RML mapping as
conventional logical sources.
"""

import argparse
import sys
import uuid

from rdflib import Graph, Literal, BNode, URIRef
from itertools import chain

from namespaces import *
from util import *
from algorithm import *
from queries import *


def normalize_rml_kgc(g):
    """
    Normalize RML triples in the graph by converting shorthand properties to their expanded forms.
    Converts properties like rml:subject to rml:subjectMap with nested structure.
    """
    counter = 0
    
    def get_new_blank_node():
        """Generate a new blank node"""
        return BNode()
    
    # Helper to find objects for a predicate
    def get_objects_for_predicate(predicate):
        return list(g.objects(None, predicate))
    
    # Helper to find subjects for a predicate-object pair
    def get_subjects_for_predicate_object(predicate, obj):
        return list(g.subjects(predicate, obj))
    
    # 1. Normalize 'subject' property to 'subjectMap'
    subject_triples = list(g.triples((None, RML['subject'], None)))
    for s, p, o in subject_triples:
        g.remove((s, p, o))
        subject_map = get_new_blank_node()
        g.add((s, RML['subjectMap'], subject_map))
        g.add((subject_map, RML['constant'], o))
    
    # 2. Normalize 'class' property to 'predicateObjectMap'
    class_triples = list(g.triples((None, RML['class'], None)))
    for s, p, o in class_triples:
        g.remove((s, p, o))
        po_map = get_new_blank_node()
        
        # Find tripleMaps with this subject
        triple_maps = list(g.triples((None, RML['subjectMap'], s)))
        for tm_s, tm_p, tm_o in triple_maps:
            g.add((tm_s, RML['predicateObjectMap'], po_map))
            
            p_map = get_new_blank_node()
            o_map = get_new_blank_node()
            
            g.add((po_map, RML['predicateMap'], p_map))
            g.add((p_map, RML['constant'], RDF['type']))
            g.add((po_map, RML['objectMap'], o_map))
            g.add((o_map, RML['constant'], o))
    
    # 3. Normalize 'predicate' property to 'predicateMap'
    predicate_triples = list(g.triples((None, RML['predicate'], None)))
    for s, p, o in predicate_triples:
        g.remove((s, p, o))
        p_map = get_new_blank_node()
        g.add((s, RML['predicateMap'], p_map))
        g.add((p_map, RML['constant'], o))
    
    # 4. Normalize 'object' property to 'objectMap'
    object_triples = list(g.triples((None, RML['object'], None)))
    for s, p, o in object_triples:
        g.remove((s, p, o))
        o_map = get_new_blank_node()
        g.add((s, RML['objectMap'], o_map))
        g.add((o_map, RML['constant'], o))
    
    # 5. Normalize 'child' property to 'childMap'
    child_triples = list(g.triples((None, RML['child'], None)))
    for s, p, o in child_triples:
        g.remove((s, p, o))
        child_map = get_new_blank_node()
        g.add((s, RML['childMap'], child_map))
        g.add((child_map, RML['reference'], o))
    
    # 6. Normalize 'parent' property to 'parentMap'
    parent_triples = list(g.triples((None, RML['parent'], None)))
    for s, p, o in parent_triples:
        g.remove((s, p, o))
        parent_map = get_new_blank_node()
        g.add((s, RML['parentMap'], parent_map))
        g.add((parent_map, RML['reference'], o))
    
    # 7. Normalize 'datatype' property to 'datatypeMap'
    datatype_triples = list(g.triples((None, RML['datatype'], None)))
    for s, p, o in datatype_triples:
        g.remove((s, p, o))
        datatype_map = get_new_blank_node()
        g.add((s, RML['datatypeMap'], datatype_map))
        g.add((datatype_map, RML['constant'], o))
    
    # 8. Normalize 'language' property to 'languageMap'
    language_triples = list(g.triples((None, RML['language'], None)))
    for s, p, o in language_triples:
        g.remove((s, p, o))
        language_map = get_new_blank_node()
        g.add((s, RML['languageMap'], language_map))
        g.add((language_map, RML['constant'], o))
    
    # 9. Add type declarations for subjectMap
    subjectmap_triples = list(g.triples((None, RML['subjectMap'], None)))
    for s, p, o in subjectmap_triples:
        g.add((s, RDF['type'], RML['TriplesMap']))
        g.add((o, RDF['type'], RML['SubjectMap']))
    
    # 10. Add type declarations for predicateObjectMap
    pom_triples = list(g.triples((None, RML['predicateObjectMap'], None)))
    for s, p, o in pom_triples:
        g.add((s, RDF['type'], RML['TriplesMap']))
        g.add((o, RDF['type'], RML['PredicateObjectMap']))
    
    # 11. Add type declarations for predicateMap
    pm_triples = list(g.triples((None, RML['predicateMap'], None)))
    for s, p, o in pm_triples:
        g.add((s, RDF['type'], RML['PredicateObjectMap']))
        g.add((o, RDF['type'], RML['PredicateMap']))
    
    # 12. Add type declarations for objectMap
    om_triples = list(g.triples((None, RML['objectMap'], None)))
    for s, p, o in om_triples:
        # Check if this is a RefObjectMap (has parentTriplesMap)
        is_ref = any(g.triples((s, RML['parentTriplesMap'], None)))
        g.add((s, RDF['type'], RML['PredicateObjectMap']))
        if is_ref:
            g.remove((o, RDF['type'], RML['ObjectMap']))  # Remove if it exists
            g.add((o, RDF['type'], RML['RefObjectMap']))
            # Add type for the referenced TriplesMap
            ref_tm = list(g.objects(s, RML['parentTriplesMap']))
            for ref in ref_tm:
                g.add((ref, RDF['type'], RML['TriplesMap']))
        else:
            g.add((o, RDF['type'], RML['ObjectMap']))
    
    # 13. Add TermMap type to SubjectMap, PredicateMap, ObjectMap, and GraphMap
    for term_type in [RML['SubjectMap'], RML['PredicateMap'], RML['ObjectMap']]:
        term_triples = list(g.triples((None, RDF['type'], term_type)))
        for s, p, o in term_triples:
            g.add((s, RDF['type'], RML['TermMap']))
    
    # 14. Handle GraphMap
    graphmap_triples = list(g.triples((None, RML['graphMap'], None)))
    for s, p, o in graphmap_triples:
        g.add((s, RDF['type'], RML['GraphMap']))
        g.add((s, RDF['type'], RML['TermMap']))
    
    # 15. Set termType to Literal for languageMap subjects
    languagemap_triples = list(g.triples((None, RML['languageMap'], None)))
    for s, p, o in languagemap_triples:
        g.remove((o, RML['termType'], RML['IRI']))  # Remove if exists
        g.add((o, RML['termType'], RML['Literal']))
    
    # 16. Set termType to Literal for datatypeMap subjects
    datatypemap_triples = list(g.triples((None, RML['datatypeMap'], None)))
    for s, p, o in datatypemap_triples:
        g.remove((o, RML['termType'], RML['IRI']))  # Remove if exists
        g.add((o, RML['termType'], RML['Literal']))
    
    # 17. Handle explicit reference formulation in iterable field
    field_triples = list(g.triples((None, RML['field'], None)))
    for s, p, field in field_triples:
        iterator = list(g.objects(field, RML['iterator']))
        if iterator:
            ref_form = list(g.objects(field, RML['referenceFormulation']))
            if not ref_form:
                # Look for referenceFormulation in parent structures
                target_field = field
                while not ref_form and target_field:
                    # Get parent of field
                    parent_of_field = list(g.subjects(RML['field'], target_field))
                    if parent_of_field:
                        parent = parent_of_field[0]
                        # Check if this parent is a viewOn
                        abstract_ls = list(g.objects(parent, RML['viewOn']))
                        if abstract_ls:
                            ref_form = list(g.objects(abstract_ls[0], RML['referenceFormulation']))
                        else:
                            ref_form = list(g.objects(parent, RML['referenceFormulation']))
                        if not ref_form:
                            target_field = parent
                        else:
                            break
                    else:
                        break
                
                if ref_form:
                    g.add((field, RML['referenceFormulation'], ref_form[0]))




# this is important for not removing double used triples when rewriting the mapping
# also important for rewriting reference to JSON references
def make_tree_shaped_mapping(g): 

    # Create tree-shaped graph
    tree_g = Graph()
    def clone_branch(subject, graph):
        new_subject = BNode()  # create unique node
        for p, o in g.predicate_objects(subject):
            tree_g.add((new_subject, p, o))
            # If object is also a subject with outgoing edges, recurse
            if (o, None, None) in g:
                clone_branch(o, graph)
        return new_subject
    # Apply cloning
    for subj in set(g.subjects()):
        clone_branch(subj, g)
    # tree_g now contains a tree-shaped version
    return tree_g


class ViewConvertor:
    """
    Converts an RML Mapping file from a file with views to a file without views.
    Also Materializes the views as CSV files.
    """

    def __init__(self, mapping: str, output_dir: str):
        """Create an instance of the ViewToCsvConvertor class.

        Parameters
        ----------
        mapping : str
            The mapping file that will be converted.
        output_dir: str
            Directory to which the output is saved
        """
        self.mapping = resolve_path(mapping)
        self.materialized_logical_views = {}
        self.output_dir = resolve_path(output_dir, True)

    def materialize(self, lv, df):
        filename = os.path.join(self.output_dir, 'view' + str(len(self.materialized_logical_views)) + '.json')
        df.to_json(filename, orient="records", indent=4)
        self.materialized_logical_views[lv] = filename

    def algorithm1(self, g):
        triplesmaps = g.subjects(RML['subjectMap'], None)  # no poMap because can be more than one and poMap is not always required                   
        for tm in triplesmaps:
            ls = g.value(tm, RML['logicalSource'])
            is_lv = any(g.triples((ls, RML['viewOn'], None)))
            if is_lv:
                df = translate_view(ls, g)
                self.materialize(ls, df)    
                    
    def rewrite_mapping(self, g): 
        # remove view related triples
        fields = list(g.objects(None, RML['field'])) # list is need to avoid that some nested fields are skipped during the remove action in the loop. 
        for field in fields:
            g.remove((field, None, None))
        left_joins = g.objects(None, RML['leftJoin'])
        inner_joins = g.objects(None, RML['innerJoin'])
        for join in chain(left_joins, inner_joins):
            # the loop is needed to avoid that other, not join related join conditions, are removed
            join_conditions = g.objects(join, RML['joinCondition'])
            for join_condition in join_conditions:
                child_and_parent_maps = g.objects(join_condition, None)
                for child_and_parent_map in child_and_parent_maps:
                    g.remove((child_and_parent_map, None, None))
                g.remove((join_condition, None, None))
            g.remove((join, None, None))
        g.remove((None, RML['field'], None))

        # rewrite the logical view as JSON logical source
        for materialized_logical_view in self.materialized_logical_views:

            g.remove((materialized_logical_view, None, None))
            g.add((materialized_logical_view, RDF['type'], RML['LogicalSource']))
           # g.add((materialized_logical_view, RML['referenceFormulation'], RML['CSV']))
            g.add((materialized_logical_view, RML['referenceFormulation'], RML['JSONPath']))
            g.add((materialized_logical_view, RML['iterator'], Literal('$[*]')))           
            source_node = BNode()
            g.add((materialized_logical_view, RML['source'], source_node))
            g.add((source_node, RDF['type'], RML['Source']))
            g.add((source_node, RDF['type'], RML['RelativePathSource']))
            g.add((source_node, RML['root'], RML['MappingDirectory']))
            g.add(
                (source_node, RML['path'], Literal(self.materialized_logical_views[materialized_logical_view])))

        # remove other views, used as parent view (those views don't satisfy the rml-shape anymore)
        views = g.subjects(RML['viewOn'], None)
        for view in views:
            g.remove((view, None, None))

        # make tree shaped mapping to avoid removing double used triples
     #   g = make_tree_shaped_mapping(g)


        # make the references json compliant
        g_without_parent = Graph()
        for triple in g:
            g_without_parent.add(triple)
        g_without_parent.remove((None, RML['parentTriplesMap'], None))
        g_without_parent.remove((None, RML['parentMap'], None))

        for materialized_logical_view in self.materialized_logical_views:
            query_results = g_without_parent.query(all_reference_maps_per_ls(materialized_logical_view))
            for row in query_results:
                g.remove((row.ReferenceMap, RML['reference'], row.Reference))
                g.add((row.ReferenceMap, RML['reference'], Literal("$['" + row.Reference.value + "']")))
            query_results = g_without_parent.query(all_template_maps_per_ls(materialized_logical_view))
            for row in query_results:
                g.remove((row.TemplateMap, RML['template'], row.Template))
                new_template = row.Template.value.replace("{", "{$['")
                new_template = new_template.replace("}", "']}")
                g.add((row.TemplateMap, RML['template'], Literal(new_template)))


        # write new mapping file
        converted_mapping = os.path.join(self.output_dir, 'mapping_without_views.ttl')
        g.serialize(destination=converted_mapping, format="turtle", encoding='utf-8')
        print('done')

    def execute(self) -> None:
        """Convert the mapping file and materialize the views

        """
        g = Graph()
        g.parse(self.mapping)
        
        # Normalize the RML mapping to expanded form
        normalize_rml_kgc(g)
        
        self.algorithm1(g)
        self.rewrite_mapping(g)        
    


VERSION = '0.0.0'
EXIT_CODE_SUCCESS = 0
EXIT_CODE_UNKNOWN_COMMAND = -1
EXIT_CODE_NO_MAPPING = -2

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copyright by (c) '
                                                 'Els de Vleeschauwer '
                                                 '(2024), '
                                                 'available under the MIT '
                                                 'license',
                                     epilog='Please cite our paper if you '
                                            'make use of this tool')
    parser.add_argument('--version', action='version',
                        version=f'{parser.prog} {VERSION}')
    parser.add_argument('--mapping', dest='mapping',
                        help='The mapping file that needs to be converted ',
                        type=str)
    parser.add_argument('--output_dir', dest='output_dir', default='./',
                        help='Directory to which the output is saved, '
                             'default is "./"',
                        type=str)
    args = parser.parse_args()

    if not args.mapping:
        print(f'No mapping file provided. Provide mapping file after option "--mapping".', file=sys.stderr)
        sys.exit(EXIT_CODE_NO_MAPPING)
    else:
        convertor = ViewConvertor(args.mapping, args.output_dir)
        convertor.execute()
        sys.exit(EXIT_CODE_SUCCESS)
