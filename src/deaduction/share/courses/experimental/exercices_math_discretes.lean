--import data.set
import tactic

-- dEAduction tactics
-- structures2 and utils are vital
import structures2      -- hypo_analysis, targets_analysis
import utils            -- no_meta_vars
import push_neg_once

-- dEAduction definitions
import set_definitions

-- General principles :
-- Type should be defined as parameters, in order to be implicit everywhere
-- other parameters are implicit in definitions, i.e. defined using '{}' (e.g. {A : set X} )
-- but explicit everywhere else, i.e. defined using '()' (e.g. (A : set X) )
-- each definition must be an iff statement (since it will be called with 'rw' or 'symp_rw')

---------------------
-- Course metadata --
---------------------
-- logic names ['and', 'or', 'negate', 'implicate', 'iff', 'forall', 'exists', 'equal', 'map']
-- proofs names ['use_proof_methods', 'new_object']
-- proof methods names ['cbr', 'contrapose', 'absurdum', 'sorry']
-- magic names ['compute', 'assumption']



/- dEAduction
Title
    exercices de mathématiques discretes.
Author
    Alice Laroche
Institution
    Sorbonne Université
AvailableCompute
    NONE
Description
    Exercices d'un cours de maths discrètes à Sorbonne Université.
    Les numéros de questions font référence à la feuille de TD.
-/

namespace set

-- def disjoint {X : Type} (A B : set X) : Prop := A ∩ B = ∅

def partition {X :Type} (A : set (set X)) := (∀A₁ ∈ A , A₁ ≠ ∅) ∧ (∀A₁ A₂ ∈ A, (A₁ ∩ A₂ = ∅) ∨ A₁ = A₂) ∧ (∀x, ∃A₁ ∈ A, x ∈ A₁)

end set

namespace relation

def inv {X Y : Type} (R : set (X × Y)) : set (Y × X)
| (x, y) := (y, x) ∈ R

def product {X Y Z : Type} (R : set (X × Y)) (R' : set (Y × Z)) : set (X × Z)
| (x, y) := ∃z, (x, z) ∈ R ∧ (z, y) ∈ R'

def identite {X: Type} : set (X × X)
| (x, y) := x = y

def reflexive {X : Type} (R : set (X × X)) := ∀x, (x, x) ∈ R

def transitive {X : Type} (R: set (X × X)) := ∀x y z, (x, y) ∈ R ∧ (y, z) ∈ R → (x, z) ∈ R

def symetrique {X : Type} (R : set (X × X)) := ∀x y, (x, y) ∈ R → (y, x) ∈ R

def antisymetrique {X : Type} (R : set (X × X)) := ∀x y, (x, y) ∈ R ∧ (y, x) ∈ R → x = y

def relation_equivalence {X : Type} (R : set (X × X)) := reflexive R ∧ transitive R ∧ symetrique R

def relation_ordre {X : Type} (R : set (X × X)) := reflexive R ∧ transitive R ∧ antisymetrique R

def classe_equivalence {X : Type} (R : set (X × X)) (H1 : relation_equivalence R) (e : X) : set X
| e' :=  (e, e')  ∈ R


def deterministe {X Y : Type} (R : set (X × Y)) := ∀x y z, (x, y) ∈ R ∧ (x, z) ∈ R → y = z 

def total_gauche {X Y : Type} (R : set (X × Y)) := ∀x, ∃y, (x, y) ∈ R 

def application {X Y : Type} (R : set (X × Y)) := deterministe R ∧ total_gauche R

def injective {X Y : Type} (R : set (X × Y)) := ∀x y z, (x, z) ∈ R ∧ (y, z) ∈ R → x = y

def surjective {X Y : Type} (R : set (X × Y)) := ∀y, ∃x, (x, y) ∈ R

def application_injective {X Y : Type} (R : set (X × Y)) := application R ∧ injective R

def application_surjective {X Y : Type} (R : set (X × Y)) := application R ∧ surjective R

def application_bijective {X Y : Type} (R : set (X × Y)) := application R ∧ injective R ∧ surjective R

def image {X Y : Type} (R : set (X × Y)) (x : X) (y : Y) := (x, y) ∈ R 

end relation


local attribute [instance] classical.prop_decidable

---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course
variables {X Y Z: Type}

open set
open relation

notation [parsing_only] R `.` S := relation.product R S

notation R `⁻¹`  := relation.inv R
notation R `dot` S := relation.product R S


------------------
-- COURSE TITLE --
------------------
namespace math_discretes
/- dEAduction
PrettyName
    Mathématiques discrètes
-/

namespace generalites
/- dEAduction
PrettyName
    Généralités
-/

------------------------
-- COURSE DEFINITIONS --
------------------------
lemma definition.inclusion {A B : set X} : A ⊆ B ↔ ∀ {x:X}, x ∈ A → x ∈ B :=
/- dEAduction
PrettyName
    Inclusion
ImplicitUse
    True    
-/
begin
    todo,
end

lemma definition.egalite_deux_ensembles {A A' : set X} :
(A = A') ↔ ( ∀ x, x ∈ A ↔ x ∈ A' ) :=
/- dEAduction
PrettyName
    Egalité de deux ensembles
ImplicitUse
    False
-/
begin
    exact set.ext_iff,
end

-- lemma definition.inegalite_deux_ensembles {A A' : set X} :
-- (A ≠ A') ↔ ( ∃x, (x ∈ A ∧ x ∉ A') ∨ (x ∈ A' ∧ x ∉ A)) :=
-- /- dEAduction
-- PrettyName
--     Inégalité de deux ensembles
-- -/
-- begin
--     todo,
-- end

lemma definition.ensemble_vide
(A: set X) :
(A = ∅) ↔ ∀ x : X, x ∉ A
:=
begin
    exact eq_empty_iff_forall_not_mem,
end

lemma definition.ensemble_extension {X: Type}  {P : X → Prop} {x:X} :
 x ∈ {x | P x} ↔ P x
:=
/- dEAduction
PrettyName
    Ensemble en extension
-/
begin
    refl,
end

lemma definition.singleton {X : Type} {x y : X}: x ∈ ({y} : set X) ↔ x = y
:=
/- dEAduction
PrettyName
    Singleton
-/
begin
    exact mem_singleton_iff,
end

lemma definition.double_inclusion (A A' : set X) :
A = A' ↔ (A ⊆ A' ∧ A' ⊆ A) :=
/- dEAduction
PrettyName
    Double inclusion
ImplicitUse
    True
-/
begin
    exact set.subset.antisymm_iff,
end

lemma definition.ensemble_partie (A A' : set X) :
A' ∈ 𝒫(A) ↔  A' ⊆ A
:= 
/- dEAduction
PrettyName
    Ensemble des parties
-/
begin
    refl,
end

end generalites


namespace union_intersection
/- dEAduction
PrettyName
    Unions et intersections
-/

------------------------
-- COURSE DEFINITIONS --
------------------------

lemma definition.intersection_deux_ensembles {A B : set X} {x : X} :
x ∈ A ∩ B ↔ ( x ∈ A ∧ x ∈ B) :=
/- dEAduction
PrettyName
    Intersection de deux ensembles
ImplicitUse
    True
-/
begin
    exact iff.rfl,
end

lemma definition.intersection_union (A B C : set X) :
A ∩ (B ∪ C) = (A ∩ B) ∪ (A ∩ C) :=
/- dEAduction
PrettyName
   Intersection avec une union
ImplicitUse
    True
-/
begin
  exact set.inter_distrib_left A B C,
end

lemma definition.partition 
 {P : set (set X)} : 
 partition P ↔ (∀A₁ ∈ P , A₁ ≠ ∅) ∧ (∀A₁ A₂ ∈ P, (A₁ ∩ A₂ = ∅) ∨ A₁ = A₂) ∧ (∀x, ∃A₁ ∈ P, x ∈ A₁)
:=
/- dEAduction
PrettyName
   Partition
-/
begin
    todo
end
-- lemma definition.intersection_videI (A : set X) :
-- A ∩ ∅ = ∅ :=
-- /- dEAduction
-- PrettyName
--     Intersection avec l'ensemble vide I 
-- ImplicitUse
--     False
-- -/
-- begin
--     exact inter_empty A,
-- end

-- lemma definition.intersection_videII (A : set X) :
-- ∅ ∩ A = ∅ :=
-- /- dEAduction
-- PrettyName
--     Intersection avec l'ensemble vide II
-- ImplicitUse
--     False
-- -/
-- begin
--     exact empty_inter A,
-- end

-- lemma definition.union_deux_ensembles  {A : set X} {B : set X} {x : X} :
-- x ∈ A ∪ B ↔ ( x ∈ A ∨ x ∈ B) :=
-- /- dEAduction
-- PrettyName
--     Union de deux ensembles
-- ImplicitUse
--     True
-- -/
-- begin
--     exact iff.rfl,
-- end

-- lemma definition.union_intersection (A B C : set X) :
-- A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C) :=
-- /- dEAduction
-- PrettyName
--    Union avec une intersection
-- ImplicitUse
--     False
-- -/
-- begin
--   exact set.union_distrib_left A B C,
-- end

-- lemma definition.union_videI (A : set X) :
-- A ∪ ∅ = A :=
-- /- dEAduction
-- PrettyName
--     Union avec l'ensemble vide I
-- ImplicitUse
--     False
-- -/
-- begin
--     exact union_empty A,
-- end

-- lemma definition.union_videII (A : set X) :
-- ∅ ∪ A = A :=
-- /- dEAduction
-- PrettyName
--     Union avec l'ensemble vide II
-- ImplicitUse
--     False
-- -/
-- begin
--     exact empty_union A,
-- end

end union_intersection

namespace complementaire
/- dEAduction
PrettyName
    Complémentaire
-/

------------------------
-- COURSE DEFINITIONS --
------------------------

lemma definition.complement {A : set X} {x : X} : x ∈ set.compl A ↔ not (x ∈ A) :=
/- dEAduction
PrettyName
    Complementaire
ImplicitUse
    False
-/
begin
    -- split, intro H, targets_analysis,
    finish,
end

lemma definition.difference {A A' : set X} {x : X} : x ∈ set.diff A A' ↔ x ∈ A ∧ x ∉ A' :=
/- dEAduction
PrettyName
    Différence
ImplicitUse
    False
-/
begin
    finish,
end
-- lemma definition.complement_complement {A : set X} : (set.compl (set.compl A)) = A :=
-- /- dEAduction
-- PrettyName
--     Complementaire du complementaire
-- ImplicitUse
--     False
-- -/
-- begin
--     exact compl_compl',
-- end

-- lemma definition.complement_intersection {A B : set X} :
-- set.compl (A ∩ B) = (set.compl A) ∪ (set.compl B) :=
-- /- dEAduction
-- PrettyName
--     Complementaire d'une intersection
-- ImplicitUse
--     False
-- -/
-- begin
--     exact compl_inter A B,
-- end

-- lemma definition.intersection_complement {A : set X} :
-- A ∩ set.compl (A) = ∅ :=
-- /- dEAduction
-- PrettyName
--     Intersection avec le complémentaire
-- ImplicitUse
--     False
-- -/
-- begin
--     exact inter_compl_self A,
-- end

-- lemma definition.complement_union {A B : set X} :
-- set.compl (A ∪ B) = (set.compl A) ∩ (set.compl B) :=
-- /- dEAduction
-- PrettyName
--     Complementaire d'une union
-- ImplicitUse
--     False
-- -/
-- begin
--     exact compl_union A B,
-- end

-- lemma definition.union_complement {A : set X} :
-- A ∪ set.compl (A) = univ :=
-- /- dEAduction
-- PrettyName
--     Union avec le complémentaire
-- ImplicitUse
--     False
-- -/
-- begin
--     exact union_compl_self A,
-- end

end complementaire

namespace produits_cartesiens
/- dEAduction
PrettyName
    Produits cartésiens
-/

-- lemma definition.type_produit :
-- ∀ z:X × Y, ∃ x:X, ∃ y:Y, z = (x,y) :=
-- /- dEAduction
-- PrettyName
--     Element d'un produit cartésien de deux ensembles
-- -/
-- begin
--     todo
-- end


lemma definition.produit_de_parties {A : set X} {B : set Y} {a: X × Y}:
a ∈ set.prod A B ↔ ∃x ∈ A, ∃y ∈ B, a= (x,y) :=
/- dEAduction
PrettyName
    Produit cartésien de deux parties
-/
begin
    todo
end

end produits_cartesiens

namespace relations
/- dEAduction
PrettyName
    Relations
-/

------------------------
-- COURSE DEFINITIONS --
------------------------

lemma definition.inv {R : set (X × Y)} {x : X} {y : Y} :
(y,x) ∈ (inv R) ↔ (x,y) ∈ R :=
/- dEAduction
PrettyName
    Inverse d'une relation
-/
begin
    refl,
end

lemma definition.prod {R : set (X × Y)} {S : set (Y × Z)} {x : X} {z : Z} :
(x,z) ∈ (product R S) ↔ ∃y, (x,y) ∈ R ∧ (y,z) ∈ S :=
/- dEAduction
PrettyName
    Produit de deux relations
ImplicitUse
    True
-/
begin
    refl,
end

lemma definition.id {x : X} {y : X} :
(x,y) ∈ (identite : set (X × X))  ↔ x = y :=
/- dEAduction
PrettyName
    Relation identité
-/
begin
    refl,
end

lemma theorem.id :
∀ x:X,  (x,x) ∈ (identite : set (X × X)) :=
/- dEAduction
PrettyName
    Relation identité
-/
begin
    intro x, rw definition.id,
end

lemma definition.reflexive {R : set (X × X)} :
reflexive R ↔ ∀x, (x, x) ∈ R :=
/- dEAduction
PrettyName
    Réflexivité
ImplicitUse
    True
-/
begin
    refl,
end

lemma definition.transitive {R : set (X × X)} :
transitive R ↔ ∀x y z, (x, y) ∈ R ∧ (y, z) ∈ R → (x, z) ∈ R :=
/- dEAduction
PrettyName
    Transitivité
ImplicitUse
    True
-/
begin
    refl,
end

lemma definition.symetrique {R : set (X × X)} :
symetrique R ↔ ∀x y, (x, y) ∈ R → (y, x) ∈ R:=
/- dEAduction
PrettyName
    Symétrie
ImplicitUse
    True
-/
begin
    refl,
end

lemma definition.antisymetrique {R : set (X × X)} :
antisymetrique R ↔ ∀x y, (x, y) ∈ R ∧ (y, x) ∈ R → x = y :=
/- dEAduction
PrettyName
    Antisymétrie
-/
begin
    refl,
end

lemma definition.equivalence {R : set (X × X)} :
relation_equivalence R ↔ reflexive R ∧ transitive R ∧ symetrique R :=
/- dEAduction
PrettyName
    Relation d'équivalence
ImplicitUse
    True
-/
begin
    refl,
end

lemma definition.ordre {R : set (X × X)} :
relation_ordre R ↔ reflexive R ∧ transitive R ∧ antisymetrique R :=
/- dEAduction
PrettyName
    Relation d'ordre
-/
begin
    refl,
end

lemma definition.classe_equivalence {x y : X} {R : set (X × X)} {H1 : relation_equivalence R}:
y ∈ classe_equivalence R H1 x ↔ (x, y) ∈ R :=
/- dEAduction
PrettyName
    Classe d'équivalence
-/
begin
    refl,
end 
end relations

-- namespace applications

-- lemma definition.deterministe {X Y : Type} (R : set (X × Y)) 
-- : deterministe R ↔ ∀x y z, (x, y) ∈ R ∧ (x, z) ∈ R → y = z :=
-- /- dEAduction
-- PrettyName
--     Relation déterministe
-- -/
-- begin
--     refl,
-- end

-- lemma definition.total_gauche {X Y : Type} (R : set (X × Y)) :
-- total_gauche R ↔ ∀x, ∃y, (x, y) ∈ R :=
-- /- dEAduction
-- PrettyName
--     Relation totale
-- -/
-- begin
--     refl,
-- end

-- lemma definition.application {X Y : Type} (R : set (X × Y)) :
-- application R ↔ deterministe R ∧ total_gauche R :=
-- /- dEAduction
-- PrettyName
--      Relation et application
-- -/
-- begin
--     refl,
-- end

-- lemma definition.relation_injective {X Y : Type} (R : set (X × Y)) :
-- relation.injective R ↔ ∀x y z, (x, z) ∈ R ∧ (y, z) ∈ R → x = y :=
-- /- dEAduction
-- PrettyName
--     Relation injective
-- -/
-- begin
--     refl,
-- end

-- lemma definition.relation_surjective {X Y : Type} (R : set (X × Y)) :
-- relation.surjective R ↔ ∀y, ∃x, (x, y) ∈ R :=
-- /- dEAduction
-- PrettyName
--     Relation surjective
-- -/
-- begin
--     refl,
-- end

-- lemma definition.application_injective {X Y : Type} (R : set (X × Y)) :
-- application_injective R ↔ application R ∧ relation.injective R :=
-- /- dEAduction
-- PrettyName
--     Application injective
-- -/
-- begin
--     refl,
-- end

-- lemma definition.application_surjective {X Y : Type} (R : set (X × Y)) :
-- application_surjective R ↔ application R ∧ relation.surjective R :=
-- /- dEAduction
-- PrettyName
--     Application surjective
-- -/
-- begin
--     refl,
-- end

-- lemma definition.application_bijective {X Y : Type} (R : set (X × Y)) :
-- application_bijective R ↔ application R ∧ relation.injective R ∧ relation.surjective R :=
-- /- dEAduction
-- PrettyName
--     Application bijective
-- -/
-- begin
--     refl,
-- end

-- lemma definition.image {X Y : Type} (R : set (X × Y)) (x : X) (y : Y) : 
-- image R x y ↔ (x, y) ∈ R :=
-- /- dEAduction
-- PrettyName
--     Image d'une relation
-- -/
-- begin
--     refl,
-- end

-- end applications

---------------
-- EXERCICES --
---------------
namespace exercices 
/- dEAduction
PrettyName
    Exercices
-/

variables  {A B C : set X}

namespace exercice2
/- dEAduction
PrettyName
    Exercice 2
-/

lemma exercise.question1 :
(A ∩ compl (A ∩ B)) = (A ∩ compl B) :=
/- dEAduction
PrettyName
    Question 1
-/
begin
    todo,
end

lemma exercise.question2 :
A ∩ B = A ∩ C → A ∩ compl B = A ∩ compl C :=
/- dEAduction
PrettyName
    Question 2
-/
begin
    todo,
end

lemma exercise.question3 :
A ∩ B = A ∩ C ↔ A ∩ (compl B) = A ∩ (compl C) :=
/- dEAduction
PrettyName
    Question 3
Description
    Deduire de la question précedente l'équivalence des deux énoncés.
-/
begin
    todo,
end

lemma exercise.question4 :
A ∪ B ⊆ A ∪ C ∧ A ∩ B ⊆ A ∩ C → B ⊆ C :=
/- dEAduction
PrettyName
    Question 4
-/
begin
    todo,
end

lemma exercise.question5 : 
set.prod A (B ∪ C) = set.prod A B ∪ set.prod A C :=
/- dEAduction
PrettyName
    Question 5
-/ 
begin
    -- rw generalites.definition.double_inclusion, split,
    -- intros x Hx,
    -- hypo_analysis,
    todo,
end

-- lemma exercise.question61 :
-- 𝒫(A ∪ B) = 𝒫(A) ∪ 𝒫(B) ∨ ¬𝒫(A ∪ B) = 𝒫(A) ∪ 𝒫(B) :=  
-- /- dEAduction
-- PrettyName
--     Question 6.1
-- OpenQuestion
--     True
-- -/
-- begin
--     todo,
-- end

lemma exercise.question62 :
𝒫(A ∩ B) = 𝒫(A) ∩ 𝒫(B) :=  
/- dEAduction
PrettyName
    Question 6.2
-/
begin
    todo,
end

--𝒫(E ∪ {x}) = 𝒫(E) ∪ {A' | ∃A ∈ 𝒫(E), A' = A ∪ {x}} :=
lemma exercise.question7 (F : Type) (E : set F) (x : F) (h : x ∉ E) :
𝒫(E ∪ {x}) = 𝒫(E) ∪ {A' | ∃A ⊆ E, A' = A ∪ {x}} :=
/- dEAduction
PrettyName
    Question 7
-/
begin
    todo,
end

end exercice2

namespace exercice5
/- dEAduction
PrettyName
    Exercice 5
-/

lemma exercise.question2_produit_inverse (X Y Z : Type) (R : set (X × Y)) (S : set (Y × Z)) :
 (R dot S) ⁻¹ = ((S ⁻¹) dot (R ⁻¹)) :=
 /- dEAduction
PrettyName
    Question 2
-/
begin
    todo,
end
end exercice5

namespace exercice6
/- dEAduction
PrettyName
    Exercice 6
-/

lemma exercise.question1 (X: Type) (R : set (X × X)) :
reflexive R ↔ identite ⊆ R :=
/- dEAduction
PrettyName
    Question 1
-/
begin
    todo,
end

lemma exercise.question2 (X: Type) (R : set (X × X)) :
symetrique R ↔ R = inv R  :=
/- dEAduction
PrettyName
    Question 2
-/
begin
    todo,
end

lemma exercise.question3 (X: Type) (R : set (X × X)) :
antisymetrique R ↔ (R ∩ (inv R)) ⊆ identite :=
/- dEAduction
PrettyName
    Question 3
-/
begin
    todo,
end

lemma exercise.question4 (X: Type) (R : set (X × X)) :
transitive R ↔ (product R R) ⊆ R :=
/- dEAduction
PrettyName
    Question 4
-/
begin
    todo,
end

lemma exercise.question5 (X: Type) (R : set (X × X)) :
reflexive R → R ⊆ (R dot R) ∧ reflexive (R dot R) :=
/- dEAduction
PrettyName
    Question 5
-/
begin
    todo,
end

lemma exercise.question6 (X: Type) (R : set (X × X)) :
symetrique R → (R ⁻¹ dot R) = (R dot R ⁻¹) :=
/- dEAduction
PrettyName
    Question 6
-/
begin
    todo,
end

lemma exercise.question7 (X: Type) (R : set (X × X)) :
transitive R → transitive (R dot R) :=
/- dEAduction
PrettyName
    Question 7
-/
begin
    todo,
end
end exercice6

namespace exercice8
/- dEAduction
PrettyName
    Exercice 8
-/

lemma exercise.question1 (A : Type) (R : set (A × A)) (H1 : relation_equivalence R) :
∀a, a ∈ classe_equivalence R H1 a :=
/- dEAduction
PrettyName
    Question 1
-/
begin
    todo,
end

lemma exercise.question2 (A : Type) (R : set (A × A)) (H1 : relation_equivalence R) (a b : A) :
classe_equivalence R H1 a = classe_equivalence R H1 b ↔ (a,b) ∈ R :=
/- dEAduction
PrettyName
    Question 2
-/
begin
    todo,
end

lemma exercise.question3 (A : Type) (R : set (A × A)) (H1 : relation_equivalence R) (a b : A) :
classe_equivalence R H1 a ≠ classe_equivalence R H1 b → classe_equivalence R H1 a ∩ classe_equivalence R H1 b = ∅ :=
/- dEAduction
PrettyName
    Question 3
-/
begin
    todo,
end

lemma exercise.question5 (A : Type) (R : set (A × A)) (H1 : relation_equivalence R) :
partition {A₁ | ∃x, A₁ = classe_equivalence R H1 x} :=
/- dEAduction
PrettyName
    Question 5
-/
begin
    todo,
end

end exercice8

-- namespace exercice15
-- /- dEAduction
-- PrettyName
--     Exercice 15
-- -/

-- -- TODO: intégrer les defs pour applications (composition, id, bijective)
-- lemma exercise.question (X : Type) (f : X → X) :
-- ((composition f f) = id : X → X) → bijective f:=
-- /- dEAduction
-- PrettyName
--     Question 1
-- -/
-- begin
--     todo,
-- end
-- end exercice15

namespace exercice22
/- dEAduction
PrettyName
    Exercice 22
-/

lemma exercise.question1 (X Y : Type) (f : X → Y) (R : set (X × X)) (H1 : ∀x x', (x, x') ∈ R ↔ f x = f x') :
relation_equivalence R :=
/- dEAduction
PrettyName
    Question 1
-/
begin
    todo,
end

lemma exercise.question3 (X Y : Type) (f : X → Y) (R : set (X × X)) (H1 : ∀x x', (x, x') ∈ R ↔ f x = f x')
(H2: relation_equivalence R) :
∀x y, x ∈ classe_equivalence R H2 y → classe_equivalence R H2 x = classe_equivalence R H2 y :=
/- dEAduction
PrettyName
    Question 3
-/
begin
    todo,
end

-- lemma exercise.question41 (E F : Type) (f : set (E × F)) (H1 : application f) 
-- (Rf : set (E × E)) (h2 : ∀x y, (x,y) ∈ Rf ↔ (∃z, image f x z ∧ image f y z)) (h3 : relation_equivalence Rf)
-- (h4 : ¬relation.injective Rf) (h5 : ¬relation.surjective Rf)
-- (S : set (E × (set E))) (h6 : ∀x y, relation.image S x y ↔ y = classe_equivalence Rf h3 x) :
-- relation.injective S ∨ ¬relation.injective S :=
-- /- dEAduction
-- PrettyName
--     ** Question 4.1
-- -/
-- begin
--     todo,
-- end

-- lemma exercise.question42 (E F : Type) (f : set (E × F)) (H1 : application f) 
-- (Rf : set (E × E)) (h2 : ∀x y, (x,y) ∈ Rf ↔ (∃z, image f x z ∧ image f y z)) (h3 : relation_equivalence Rf)
-- (h4 : ¬relation.injective Rf) (h5 : ¬relation.surjective Rf)
-- (S : set (E × (set E))) (h6 : ∀x y, relation.image S x y ↔ y = classe_equivalence Rf h3 x) :
-- relation.surjective S ∨ ¬relation.surjective S :=
-- /- dEAduction
-- PrettyName
--     ** Question 4.2
-- -/
-- begin
--     todo,
-- end

-- lemma exercise.question5 (E F : Type) (f : set (E × F)) (H1 : application f) 
-- (Rf : set (E × E)) (h2 : ∀x y, (x,y) ∈ Rf ↔ (∃z, image f x z ∧ image f y z)) (h3 : relation_equivalence Rf)
-- (h4 : ¬relation.injective Rf) (h5 : ¬relation.surjective Rf)
-- (f' : set ((set E) × F)) (h6 : ∀X y, (X, y) ∈ f' ↔ ∃x ∈ X, relation.image f x y) :
-- application f' :=
-- /- dEAduction
-- PrettyName
--     ** Question 5
-- -/
-- begin
--     todo,
-- end

-- lemma exercise.question61 (E F : Type) (f : set (E × F)) (H1 : application f) 
-- (Rf : set (E × E)) (h2 : ∀x y, (x,y) ∈ Rf ↔ (∃z, image f x z ∧ image f y z)) (h3 : relation_equivalence Rf)
-- (h4 : ¬relation.injective Rf) (h5 : ¬relation.surjective Rf)
-- (f' : set ((set E) × F)) (h6 : ∀X y, (X, y) ∈ f' ↔ ∃x ∈ X, relation.image f x y) :
-- relation.injective f' ∨ ¬ relation.injective f' :=
-- /- dEAduction
-- PrettyName
--     ** Question 6.1
-- -/
-- begin
--     todo,
-- end

-- lemma exercise.question62 (E F : Type) (f : set (E × F)) (H1 : application f) 
-- (Rf : set (E × E)) (h2 : ∀x y, (x,y) ∈ Rf ↔ (∃z, image f x z ∧ image f y z)) (h3 : relation_equivalence Rf)
-- (h4 : ¬relation.injective Rf) (h5 : ¬relation.surjective Rf)
-- (f' : set ((set E) × F)) (h6 : ∀X y, (X, y) ∈ f' ↔ ∃x ∈ X, relation.image f x y) :
-- relation.injective f' ∨ ¬ relation.injective f' :=
-- /- dEAduction
-- PrettyName
--     ** Question 6.2
-- -/
-- begin
--     todo,
-- end


end exercice22

end exercices


end math_discretes
end course

