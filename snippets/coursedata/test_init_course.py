from deaduction.pylib.coursedata import parser_course


def test_lean_course_grammar_statement():
    test_definition1 = """lemma definition.inclusion (A B : set X) : A ⊆ B ↔ ∀ {{x:X}}, x ∈ A → x ∈ B :="""
    test_definition2 = """lemma definition.inclusion 
    (A B : set X) : 
A ⊆ B ↔ ∀ {{x:X}}, x ∈ A → x ∈ B :="""
    test_exercise1 = """
lemma exercise.union_distributive_inter : A ∩ (B ∪ C)  = (A ∩ B) ∪ (A ∩ C) := 
/- dEAduction
PrettyName
    Intersection d'une union
Description
    L'intersection est distributive par rapport à l'union
Tools->Logic
    $ALL -negate
Tools->ProofTechniques
    $ALL -contradiction
Tools->Definitions
    $UNTIL_NOW -union_quelconque_ensembles -intersection_quelconque_ensembles
Tools->Theorems
    double_inclusion
ExpectedVarsNumber
    X=3, A=1, B=1
-/

begin
    sorry
end
"""
    test_exercise2 = """"""
    my_tree = parser_course.lean_course_grammar.parse(test_definition1)
    my_tree = parser_course.lean_course_grammar.parse(test_definition2)
    my_tree = parser_course.lean_course_grammar.parse(test_exercise1)
    my_tree = parser_course.lean_course_grammar.parse(test_exercise1)






# def test_exercice_test():
#     path = Path('/Users/leroux/Documents/PROGRAMMATION/LEAN/LEAN_TRAVAIL/dEAduction-lean/src/snippets')
#     ex_file = 'exercises_test.lean'
#     my_course = Course.from_lean_file(path, ex_file)
#     assert my_course == Course(exercises_list=[Exercise(active_definitions=['union', 'intersection_deux'], active_logic=['∀', '∃', '→', '↔', 'ET', 'OU', 'NON', 'Absurde', 'Contraposée', 'Par_cas', 'Contradiction', 'Toto'], active_magic=None, active_theorems=['double_inclusion', 'Riemann_hypothesis'], description="L'intersection est distributive par rapport à l'union et ça continue sur la ligne suivante", expected_number_var={'X': 3, 'A': 1, 'B': 1}, Lean_line_number=49, lean_name='exercise.union_distributive_inter', lean_statement='A ∩ (B ∪ C) = (A ∩ B) ∪ (A ∩ C) ', lean_variables='(X : Type) (A B C : set X)', section='set_theory.unions_and_intersections', title="Intersection d'unions"), Exercise(active_definitions=['ALL'], active_logic=['∀', '∃', '→', '↔', 'ET', 'OU', 'NON', 'Absurde', 'Contraposée', 'Choix'], active_magic=None, active_theorems=['double_inclusion', 'Riemann_hypothesis'], description="L'union est distributive par rapport à l'intersection", expected_number_var={'X': 3, 'A': 1, 'B': 1}, Lean_line_number=67, lean_name='exercise.inter_distributive_union', lean_statement=': A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C) ', lean_variables='', section='set_theory.unions_and_intersections', title="Union d'intersections"), Exercise(active_definitions=['ALL'], active_logic=['∀', '∃', '→', '↔', 'ET', 'OU', 'NON', 'Absurde', 'Contraposée', 'Choix'], active_magic=None, active_theorems=['double_inclusion', 'Riemann_hypothesis'], description='Tout ensemble est égal au complémentaire de son complémentaire et réciproquement.', expected_number_var={'X': 3, 'A': 1, 'B': 1}, Lean_line_number=94, lean_name='exercise.complement_complement', lean_statement=': - - A =A ', lean_variables='', section='set_theory.complements', title='Complémentaire du complémentaire')], sections_dict={'set_theory': 'Set Theory', 'set_theory.unions_and_intersections': 'Unions and intersections', 'set_theory.complements': 'complements'}, sections_list=['set_theory', 'set_theory.unions_and_intersections', 'set_theory.complements'])
