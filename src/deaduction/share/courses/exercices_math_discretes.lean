--import data.set
import tactic

-- dEAduction imports
import utils
import structures2

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
    exercises de mathématiques discretes.
Author
    Alice Laroche
Institution
    
AvailableMagic
    ALL
Description
    
-/

namespace set

def disjoint {X : Type} (A B : set X) : Prop := A ∩ B = ∅

def partition {X :Type} (A : set (set X)) := (∀A₁ ∈ A , A₁ ≠ ∅) ∧ (∀A₁ A₂ ∈ A,disjoint A₁ A₂ ∨ A₁ = A₂) ∧ (∀x, ∃A₁ ∈ A, x ∈ A₁)

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

def classe_equivalence {X : Type} (R : set (X × X)) (h1 : relation_equivalence R) (e : X) : set X
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
parameters {X Y Z: Type}

notation [parsing_only] P ` and ` Q := P ∧ Q
notation [parsing_only]  P ` or ` Q := P ∨ Q
notation [parsing_only]  ` not ` P := ¬ P
notation [parsing_only]  P ` implies ` Q := P → Q
notation [parsing_only]  P ` iff ` Q := P ↔ Q

notation [parsing_only]  x ` in ` A := x ∈ A
notation [parsing_only]  A ` cap ` B := A ∩ B
notation [parsing_only]  A ` cup ` B := A ∪ B
notation [parsing_only]  A ` subset ` B := A ⊆ B
notation [parsing_only]  `emptyset` := ∅

notation [parsing_only] P ` et ` Q := P ∧ Q
notation [parsing_only]  P ` ou ` Q := P ∨ Q
notation [parsing_only]  ` non ` P := ¬ P
notation [parsing_only]  P ` implique ` Q := P → Q
notation [parsing_only]  P ` ssi ` Q := P ↔ Q

notation [parsing_only]  x ` dans ` A := x ∈ A
notation [parsing_only]  x ` appartient ` A := x ∈ A
notation [parsing_only]  A ` inter ` B := A ∩ B
notation [parsing_only]  A ` intersection ` B := A ∩ B
notation [parsing_only]  A ` union ` B := A ∪ B
notation [parsing_only]  A ` inclus ` B := A ⊆ B
notation [parsing_only]  `vide` := ∅

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
-/
begin
    todo,
end

lemma definition.egalite_deux_ensembles {A A' : set X} :
(A = A') ↔ ( ∀ x, x ∈ A ↔ x ∈ A' ) :=
/- dEAduction
PrettyName
    Egalité de deux ensembles
-/
begin
    exact set.ext_iff,
end

lemma definition.inegalite_deux_ensembles {A A' : set X} :
(A ≠ A') ↔ ( ∃x, (x ∈ A ∧ x ∉ A') ∨ (x ∈ A' ∧ x ∉ A)) :=
/- dEAduction
PrettyName
    Inégalité de deux ensembles
-/
begin
    todo,
end

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

lemma definition.ensemble_partie (A : set X) :
𝒫(A) = {X | X ⊆ A}
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
    False
-/
begin
  exact set.inter_distrib_left A B C,
end

lemma definition.intersection_videI (A : set X) :
A ∩ ∅ = ∅ :=
/- dEAduction
PrettyName
    Intersection avec l'ensemble vide I 
ImplicitUse
    False
-/
begin
    exact inter_empty A,
end

lemma definition.intersection_videII (A : set X) :
∅ ∩ A = ∅ :=
/- dEAduction
PrettyName
    Intersection avec l'ensemble vide II
ImplicitUse
    False
-/
begin
    exact empty_inter A,
end

lemma definition.union_deux_ensembles  {A : set X} {B : set X} {x : X} :
x ∈ A ∪ B ↔ ( x ∈ A ∨ x ∈ B) :=
/- dEAduction
PrettyName
    Union de deux ensembles
ImplicitUse
    True
-/
begin
    exact iff.rfl,
end

lemma definition.union_intersection (A B C : set X) :
A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C) :=
/- dEAduction
PrettyName
   Union avec une intersection
ImplicitUse
    False
-/
begin
  exact set.union_distrib_left A B C,
end

lemma definition.union_videI (A : set X) :
A ∪ ∅ = A :=
/- dEAduction
PrettyName
    Union avec l'ensemble vide I
ImplicitUse
    False
-/
begin
    exact union_empty A,
end

lemma definition.union_videII (A : set X) :
∅ ∪ A = A :=
/- dEAduction
PrettyName
    Union avec l'ensemble vide II
ImplicitUse
    False
-/
begin
    exact empty_union A,
end

end union_intersection

namespace complementaire
/- dEAduction
PrettyName
    Complémentaire
-/

------------------------
-- COURSE DEFINITIONS --
------------------------

lemma definition.complement {A : set X} {x : X} : x ∈ set.compl A ↔ x ∉ A :=
/- dEAduction
PrettyName
    Complementaire
ImplicitUse
    False
-/
begin
    finish,
end

lemma definition.complement_complement {A : set X} : (set.compl (set.compl A)) = A :=
/- dEAduction
PrettyName
    Complementaire du complementaire
ImplicitUse
    False
-/
begin
    exact compl_compl',
end

lemma definition.complement_intersection {A B : set X} :
set.compl (A ∩ B) = (set.compl A) ∪ (set.compl B) :=
/- dEAduction
PrettyName
    Complementaire d'une intersection
ImplicitUse
    False
-/
begin
    exact compl_inter A B,
end

lemma definition.intersection_complement {A : set X} :
A ∩ set.compl (A) = ∅ :=
/- dEAduction
PrettyName
    Intersection avec le complémentaire
ImplicitUse
    False
-/
begin
    exact inter_compl_self A,
end

lemma definition.complement_union {A B : set X} :
set.compl (A ∪ B) = (set.compl A) ∩ (set.compl B) :=
/- dEAduction
PrettyName
    Complementaire d'une union
ImplicitUse
    False
-/
begin
    exact compl_union A B,
end

lemma definition.union_complement {A : set X} :
A ∪ set.compl (A) = univ :=
/- dEAduction
PrettyName
    Union avec le complémentaire
ImplicitUse
    False
-/
begin
    exact union_compl_self A,
end

end complementaire

namespace produits_cartesiens
/- dEAduction
PrettyName
    Produits cartésiens
-/

lemma definition.type_produit :
∀ z:X × Y, ∃ x:X, ∃ y:Y, z = (x,y) :=
/- dEAduction
PrettyName
    Element d'un produit cartésien de deux ensembles
-/
begin
    todo
end


lemma definition.produit_de_parties {A : set X} {B : set Y} {x:X} {y:Y} :
(x,y) ∈ set.prod A B ↔ x ∈ A ∧ y ∈ B :=
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

lemma definition.reflexive {R : set (X × X)} :
reflexive R ↔ ∀x, (x, x) ∈ R :=
/- dEAduction
PrettyName
    Réflexivité
-/
begin
    refl,
end

lemma definition.transitive {R : set (X × X)} :
transitive R ↔ ∀x y z, (x, y) ∈ R ∧ (y, z) ∈ R → (x, z) ∈ R :=
/- dEAduction
PrettyName
    Transitivité
-/
begin
    refl,
end

lemma definition.symetrique {R : set (X × X)} :
symetrique R ↔ ∀x y, (x, y) ∈ R → (y, x) ∈ R:=
/- dEAduction
PrettyName
    Symétrie
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

lemma definition.classe_equivalence {x y : X} {R : set (X × X)} {h1 : relation_equivalence R}:
y ∈ classe_equivalence R h1 x ↔ (x, y) ∈ R :=
/- dEAduction
PrettyName
    Classe d'équivalence
-/
begin
    refl,
end 
end relations

namespace fonctions

lemma definition.deterministe {X Y : Type} (R : set (X × Y)) 
: deterministe R ↔ ∀x y z, (x, y) ∈ R ∧ (x, z) ∈ R → y = z :=
/- dEAduction
PrettyName
    Fonction déterministe
-/
begin
    refl,
end

lemma definition.total_gauche {X Y : Type} (R : set (X × Y)) :
total_gauche R ↔ ∀x, ∃y, (x, y) ∈ R :=
/- dEAduction
PrettyName
    Fonction totale
-/
begin
    refl,
end

lemma definition.application {X Y : Type} (R : set (X × Y)) :
application R ↔ deterministe R ∧ total_gauche R :=
/- dEAduction
PrettyName
     Application
-/
begin
    refl,
end

lemma definition.injective {X Y : Type} (R : set (X × Y)) :
relation.injective R ↔ ∀x y z, (x, z) ∈ R ∧ (y, z) ∈ R → x = y :=
/- dEAduction
PrettyName
    Fonction injective
-/
begin
    refl,
end

lemma definition.surjective {X Y : Type} (R : set (X × Y)) :
relation.surjective R ↔ ∀y, ∃x, (x, y) ∈ R :=
/- dEAduction
PrettyName
    Fonction surjective
-/
begin
    refl,
end

lemma definition.application_injective {X Y : Type} (R : set (X × Y)) :
application_injective R ↔ application R ∧ relation.injective R :=
/- dEAduction
PrettyName
    Application injective
-/
begin
    refl,
end

lemma definition.application_surjective {X Y : Type} (R : set (X × Y)) :
application_surjective R ↔ application R ∧ relation.surjective R :=
/- dEAduction
PrettyName
    Application surjective
-/
begin
    refl,
end

lemma definition.application_bijective {X Y : Type} (R : set (X × Y)) :
application_bijective R ↔ application R ∧ relation.injective R ∧ relation.surjective R :=
/- dEAduction
PrettyName
    Application bijective
-/
begin
    refl,
end

lemma definition.image {X Y : Type} (R : set (X × Y)) (x : X) (y : Y) : 
image R x y ↔ (x, y) ∈ R :=
/- dEAduction
PrettyName
    Image d'une fonction
-/
begin
    refl,
end

end fonctions

namespace exercises 
/- dEAduction
PrettyName
    Exercises
-/

variables  {A B C : set X}

namespace exercise2
/- dEAduction
PrettyName
    Exercise 2
-/

lemma exercise.question1 :
(A ∩ compl (A ∩ B)) = (A ∩ compl B) :=
/- dEAduction
PrettyName
    Question 1
Description
    Soient A et B deux parties de X. Montrer que l'intersection de A et du complémentaire de l'intersection de A et B est égal a l'intersection de A et du complémentaire de B
-/
begin
    todo,
end

lemma exercise.question2 :
A ∩ B = A ∩ C -> A ∩ compl B = A ∩ compl C:=
/- dEAduction
PrettyName
    Question 2
Description
    Soient A, B et C trois parties de X. Que si l'intersection de A et B est égale à l'intersection de A et C, alors l'intersection de A et du complémentaire de B est égale a l'intersection de A et du complementaire de C
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
Description
    Soient A, B, C trois parties de E. Montrer que si l'union de A et B est incluse dans l'union de A et C et A et que l'intersection de A et B est incluse dans l'intersection de A et C alors B est inclue dans C
-/
begin
    todo,
end

lemma exercise.question5 : 
set.prod A (B ∪ C) = set.prod A B ∪ set.prod A C :=
/- dEAduction
PrettyName
    Question 5
Description
    Le produit de A et de l'union de B et C est égale à l'union du produit de A et B et du produit de A et C
-/ 
begin
    todo,
end

lemma exercise.question61 :
𝒫(A ∪ B) = 𝒫(A) ∪ 𝒫(B) ∨ ¬𝒫(A ∪ B) = 𝒫(A) ∪ 𝒫(B) :=  
/- dEAduction
PrettyName
    Question 6.1
Description
    L'ensemble des partie de l'union de A et B est il egale a l'union des partie de A et des parties de B ou non ?
-/
begin
    todo,
end

lemma exercise.question62 :
𝒫(A ∩ B) = 𝒫(A) ∩ 𝒫(B) ∨ ¬𝒫(A ∩ B) = 𝒫(A) ∩ 𝒫(B) :=  
/- dEAduction
PrettyName
    Question 6.2
Description
    L'ensemble des partie de l'intersection de A et B est il egale a l'intersection des partie de A et des parties de B ou non ?
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
Description
    placeholder
-/
begin
    todo,
end

end exercise2

namespace exercise5
/- dEAduction
PrettyName
    Exercice 5
-/

lemma exercise.question2_produit_inverse (X Y Z : Type) (R : set (X × Y)) (S : set (Y × Z)) :
 (R dot S) ⁻¹ = ((S ⁻¹) dot (R ⁻¹)) :=
 /- dEAduction
PrettyName
    Question 2
Description
    placeholder
-/
begin
  targets_analysis,
    todo,
end
end exercise5

namespace exercise6
/- dEAduction
PrettyName
    Exercice 6
-/

lemma exercise.question1 (X: Type) (R : set (X × X)) :
reflexive R ↔ identite ⊆ R :=
/- dEAduction
PrettyName
    Question 1
Description
    placeholder
-/
begin
    todo,
end

lemma exercise.question2 (X: Type) (R : set (X × X)) :
symetrique R ↔ R = inv R  :=
/- dEAduction
PrettyName
    Question 2
Description
    placeholder
-/
begin
    todo,
end

lemma exercise.question3 (X: Type) (R : set (X × X)) :
antisymetrique R ↔ (R ∩ (inv R)) ⊆ identite :=
/- dEAduction
PrettyName
    Question 3
Description
    placeholder
-/
begin
    todo,
end

lemma exercise.question4 (X: Type) (R : set (X × X)) :
transitive R ↔ (product R R) ⊆ R :=
/- dEAduction
PrettyName
    Question 4
Description
    placeholder
-/
begin
    todo,
end

lemma exercise.question5 (X: Type) (R : set (X × X)) :
reflexive R → R ⊆ (R dot R) ∧ reflexive (R dot R) :=
/- dEAduction
PrettyName
    Question 5
Description
    placeholder
-/
begin
    todo,
end

lemma exercise.question6 (X: Type) (R : set (X × X)) :
symetrique R → (R ⁻¹ dot R) = (R dot R ⁻¹) :=
/- dEAduction
PrettyName
    Question 6
Description
    placeholder
-/
begin
    todo,
end

lemma exercise.question7 (X: Type) (R : set (X × X)) :
transitive R → transitive (R dot R) :=
/- dEAduction
PrettyName
    Question 7
Description
    placeholder
-/
begin
    todo,
end
end exercise6

namespace exercise8
/- dEAduction
PrettyName
    Exercice 8
-/

lemma exercise.question1 (A : Type) (R : set (A × A)) (h1 : relation_equivalence R) :
∀a, a ∈ classe_equivalence R h1 a :=
/- dEAduction
PrettyName
    Question 1
Description
    placeholder
-/
begin
    todo,
end

lemma exercise.question2 (A : Type) (R : set (A × A)) (h1 : relation_equivalence R) (a b : A) :
classe_equivalence R h1 a = classe_equivalence R h1 b ↔ (a,b) ∈ R :=
/- dEAduction
PrettyName
    Question 2
Description
    placeholder
-/
begin
    todo,
end

lemma exercise.question3 (A : Type) (R : set (A × A)) (h1 : relation_equivalence R) (a b : A) :
classe_equivalence R h1 a ≠ classe_equivalence R h1 b → classe_equivalence R h1 a ∩ classe_equivalence R h1 b = ∅ :=
/- dEAduction
PrettyName
    Question 3
Description
    placeholder
-/
begin
    todo,
end

lemma exercise.question4 (A : Type) (R : set (A × A)) (h1 : relation_equivalence R) (a b : A) :
classe_equivalence R h1 a ≠ classe_equivalence R h1 b → set.disjoint (classe_equivalence R h1 a) (classe_equivalence R h1 b) :=
/- dEAduction
PrettyName
    Question 4
Description
    placeholder
-/
begin
    todo,
end

lemma exercise.question5 (A : Type) (R : set (A × A)) (h1 : relation_equivalence R) :
partition {A₁ | ∃x, A₁ = classe_equivalence R h1 x} :=
/- dEAduction
PrettyName
    Question 5
Description
    placeholder
-/
begin
    todo,
end

end exercise8

namespace exercice15
/- dEAduction
PrettyName
    Exercice 10
-/

lemma exercise.question (A : Type) (f : set (A × A)) (h1 : application f) :
(∀x : A, ∃y : A, image f x y ∧ image f y x) → application_bijective f:=
/- dEAduction
PrettyName
    Question 1
Description
    placeholder
-/
begin
    todo,
end
end exercice15

namespace exercice22
/- dEAduction
PrettyName
    Exercice 22
-/

lemma exercise.question1 (E F : Type) (f : set (E × F)) (h1 : application f) (Rf : set (E × E)) (h2 : ∀x y, (x,y) ∈ Rf ↔ (∃z, image f x z ∧ image f y z)) :
relation_equivalence Rf :=
/- dEAduction
PrettyName
    Question 1
Description
    placeholder
-/
begin
    todo,
end

lemma exercise.question3 (E F : Type) (f : set (E × F)) (h1 : application f) 
(Rf : set (E × E)) (h2 : ∀x y, (x,y) ∈ Rf ↔ (∃z, image f x z ∧ image f y z)) (h3 : relation_equivalence Rf):
∀x y, x ∈ classe_equivalence Rf h3 y → classe_equivalence Rf h3 x = classe_equivalence Rf h3 y :=
/- dEAduction
PrettyName
    Question 3
Description
    placeholder
-/
begin
    todo,
end

lemma exercise.question41 (E F : Type) (f : set (E × F)) (h1 : application f) 
(Rf : set (E × E)) (h2 : ∀x y, (x,y) ∈ Rf ↔ (∃z, image f x z ∧ image f y z)) (h3 : relation_equivalence Rf)
(h4 : ¬relation.injective Rf) (h5 : ¬relation.surjective Rf)
(S : set (E × (set E))) (h6 : ∀x y, relation.image S x y ↔ y = classe_equivalence Rf h3 x) :
relation.injective S ∨ ¬relation.injective S :=
/- dEAduction
PrettyName
    Question 4.1
Description
    placeholder
-/
begin
    todo,
end

lemma exercise.question42 (E F : Type) (f : set (E × F)) (h1 : application f) 
(Rf : set (E × E)) (h2 : ∀x y, (x,y) ∈ Rf ↔ (∃z, image f x z ∧ image f y z)) (h3 : relation_equivalence Rf)
(h4 : ¬relation.injective Rf) (h5 : ¬relation.surjective Rf)
(S : set (E × (set E))) (h6 : ∀x y, relation.image S x y ↔ y = classe_equivalence Rf h3 x) :
relation.surjective S ∨ ¬relation.surjective S :=
/- dEAduction
PrettyName
    Question 4.2
Description
    placeholder
-/
begin
    todo,
end

lemma exercise.question5 (E F : Type) (f : set (E × F)) (h1 : application f) 
(Rf : set (E × E)) (h2 : ∀x y, (x,y) ∈ Rf ↔ (∃z, image f x z ∧ image f y z)) (h3 : relation_equivalence Rf)
(h4 : ¬relation.injective Rf) (h5 : ¬relation.surjective Rf)
(f' : set ((set E) × F)) (h6 : ∀X y, (X, y) ∈ f' ↔ ∃x ∈ X, relation.image f x y) :
application f' :=
/- dEAduction
PrettyName
    Question 5
Description
    placeholder
-/
begin
    todo,
end

lemma exercise.question61 (E F : Type) (f : set (E × F)) (h1 : application f) 
(Rf : set (E × E)) (h2 : ∀x y, (x,y) ∈ Rf ↔ (∃z, image f x z ∧ image f y z)) (h3 : relation_equivalence Rf)
(h4 : ¬relation.injective Rf) (h5 : ¬relation.surjective Rf)
(f' : set ((set E) × F)) (h6 : ∀X y, (X, y) ∈ f' ↔ ∃x ∈ X, relation.image f x y) :
relation.injective f' ∨ ¬ relation.injective f' :=
/- dEAduction
PrettyName
    Question 6.1
Description
    placeholder
-/
begin
    todo,
end

lemma exercise.question62 (E F : Type) (f : set (E × F)) (h1 : application f) 
(Rf : set (E × E)) (h2 : ∀x y, (x,y) ∈ Rf ↔ (∃z, image f x z ∧ image f y z)) (h3 : relation_equivalence Rf)
(h4 : ¬relation.injective Rf) (h5 : ¬relation.surjective Rf)
(f' : set ((set E) × F)) (h6 : ∀X y, (X, y) ∈ f' ↔ ∃x ∈ X, relation.image f x y) :
relation.injective f' ∨ ¬ relation.injective f' :=
/- dEAduction
PrettyName
    Question 6.2
Description
    placeholder
-/
begin
    todo,
end


end exercice22

end exercises


end math_discretes
end course

