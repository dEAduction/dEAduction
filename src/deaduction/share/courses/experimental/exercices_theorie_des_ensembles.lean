/-
This is a d∃∀duction file providing exercises for basic set theory. French version.
-/

-- Lean standard imports
import tactic
-- import data.real.basic


-- dEAduction tactics and theorems
-- structures2 and utils are vital
import structures2      -- hypo_analysis, targets_analysis
import utils            -- no_meta_vars
import push_neg_once    -- pushing negation just one step
-- import induction     -- theorem for the induction proof method
-- import compute_all   -- tactics for the compute buttons

-- dEAduction definitions
import set_definitions

-- Use classical logic
local attribute [instance] classical.prop_decidable

-------------------------
-- dEAduction METADATA --
-------------------------

/- dEAduction
Title
    Théorie des ensembles
Author
    Frédéric Le Roux
Institution
    Université de France
Description
    Ce cours correspond à un cours standard de théorie "élémentaire" des ensembles.
AvailableCompute
    None
-/

local attribute [instance] classical.prop_decidable

---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course
variables {X Y Z: Type}


open set

------------------
-- COURSE TITLE --
------------------
namespace theorie_des_ensembles
/- dEAduction
PrettyName
    Théorie des ensembles
-/

namespace generalites
/- dEAduction
PrettyName
    Généralités
-/

------------------------
-- COURSE DEFINITIONS --
------------------------
lemma definition.inclusion {A B : set X} : A ⊆ B ↔ ∀ {x:X}, (x ∈ A) → x ∈ B :=
/- dEAduction
ImplicitUse
    True
-/
begin
    exact iff.rfl,
end

lemma definition.egalite_deux_ensembles {A A' : set X} :
(A = A') ↔ ( ∀ x, x ∈ A ↔ x ∈ A' ) :=
/- dEAduction
PrettyName
    Egalité de deux ensembles
ImplicitUse
    True
-/
begin
     exact set.ext_iff
end

lemma definition.ensemble_vide
(A: set X) :
(A = ∅) ↔ ∀ x : X, x ∉ A
:=
begin
    exact eq_empty_iff_forall_not_mem,
end

-- lemma definition.ensemble_non_vide
-- (A: set X) :
-- (A ≠ ∅) ↔ ∃ x : X, x ∈ A
-- :=
-- begin
--     todo
-- end

lemma definition.ensemble_extension {X: Type}  {P : X → Prop} {x:X} :
 x ∈ {x | P x} ↔ P x
:=
/- dEAduction
PrettyName
    Ensemble en extension
-/
begin
    refl
end


lemma definition.double_inclusion (A A' : set X) :
A = A' ↔ (A ⊆ A' ∧ A' ⊆ A) :=
/- dEAduction
PrettyName
    Egalité de deux ensembles : double inclusion
ImplicitUse
    True
-/
begin
    exact set.subset.antisymm_iff
end

lemma exercise.inclusion_transitive
(A B C : set X) :
(A ⊆ B ∧ B ⊆ C) → A ⊆ C
:=
/- dEAduction
PrettyName
    Transitivité de l'inclusion
-/
begin
    todo
end


end generalites

---------------
-- SECTION 1 --
---------------
namespace unions_et_intersections
-- variables unions_et_intersections --
variables {A B C : set X}

-----------------
-- DEFINITIONS --
-----------------
namespace definitions
/- dEAduction
PrettyName
    Définitions
-/

lemma definition.intersection_deux_ensembles {A B : set X} {x : X} :
x ∈ A ∩ B ↔ ( x ∈ A ∧ x ∈ B) :=
/- dEAduction
PrettyName
    Intersection de deux ensembles
ImplicitUse
    True
-/
begin
    exact iff.rfl
end

lemma definition.intersection_quelconque_ensembles {I : index_set} {E : I → set X}  {x : X} :
(x ∈ set.Inter E) ↔ (∀ i:I, x ∈ E i) :=
/- dEAduction
PrettyName
    Intersection d'une famille quelconque d'ensembles
MatchPattern
    IFF(
    ∈(?0, SET_INTER+(?1) )
    ∀(TYPE, ?2, ∈(?0, APP(?1, ?2) ) ) 
    )
-/
begin
    exact set.mem_Inter
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
    exact iff.rfl
end

lemma definition.union_quelconque_ensembles {I : index_set} {E : I → set X}  {x : X} :
(x ∈ set.Union E) ↔ (∃ i:I, x ∈ E i) :=
/- dEAduction
PrettyName
    Union d'une famille quelconque d'ensembles
-/
begin
    exact set.mem_Union
end

end definitions

---------------
-- EXERCICES --
---------------
namespace exercices

lemma exercise.intersection_inclus_ensemble :
A ∩ B ⊆ A
:=
/- dEAduction
PrettyName
    Un ensemble contient son intersection avec un autre
-/
begin
    todo
end


lemma exercise.union_distributive_inter : A ∩ (B ∪ C)  = (A ∩ B) ∪ (A ∩ C) :=
/- dEAduction
PrettyName
    Intersection avec une union
Description
    L'intersection est distributive par rapport à l'union
AvailableLogic
    $ALL
AvailableProofs
    $ALL
AvailableDefinitions
    $UNTIL_NOW -union_quelconque_ensembles -intersection_quelconque_ensembles
AvailableTheorems
    double_inclusion
ExpectedVarsNumber
    X=3, A=1, B=1
-/
begin
    rw generalites.definition.egalite_deux_ensembles,
    intro x, split,
    intro H,
    cases H with H1 H2,
    cases H2 with H2a H2b,
    left,
    split,
    assumption, assumption,
    right, split, assumption, assumption, todo
end

-- NB: 'ExpectedVarsNumber' is not implemented yet
-- planned to be used for naming variables


lemma exercise.inter_distributive_union : A ∪ (B ∩ C)  = (A ∪ B) ∩ (A ∪ C) :=
/- dEAduction
PrettyName
    Union avec une intersection
Description
    L'union est distributive par rapport à l'intersection
AvailableDefinitions
    $UNTIL_NOW -union_quelconque_ensembles -intersection_quelconque_ensembles
-/
begin
    todo
end


end exercices

end unions_et_intersections


---------------
-- SECTION 2 --
---------------
namespace complementaire
/- dEAduction
PrettyName
    Complémentaire
-/


-- variables complementaire --
variables  {A B : set X}
variables {I : index_set} {E F : I → set X}
-- notation `∁`A := set.compl A

-----------------
-- DEFINITIONS --
-----------------
lemma definition.complement {A : set X} {x : X} : x ∈ set.compl A ↔ x ∉ A :=
/- dEAduction
PrettyName
    Complémentaire
-/
begin
    finish
end

---------------
-- EXERCICES --
---------------
lemma exercise.complement_complement : (set.compl (set.compl A)) = A :=
/- dEAduction
PrettyName
    Complémentaire du complémentaire
Description
    Tout ensemble est égal au complémentaire de son complémentaire
AvailableDefinitions
    $UNTIL_NOW -union_quelconque_ensembles -intersection_quelconque_ensembles
-/
begin
    todo
end

lemma exercise.complement_union_deux :
set.compl (A ∪ B) = (set.compl A) ∩ (set.compl B) :=
/- dEAduction
PrettyName
    Complémentaire d'union I
Description
    Le complémentaire de l'union de deux ensembles égale l'intersection des complémentaires
AvailableDefinitions
    $UNTIL_NOW -union_quelconque_ensembles -intersection_quelconque_ensembles
-/
begin
    todo
end

lemma exercise.complement_union_quelconque :
set.compl (set.Union (λ i, E i)) = set.Inter (λ i, set.compl (E i)) :=
/- dEAduction
PrettyName
    Complémentaire d'union II
Description
    Le complémentaire d'une réunion quelconque égale l'intersection des complémentaires
-/
begin
    todo
end


lemma exercise.inclusion_complement_I :
A ⊆ B → set.compl B ⊆ set.compl A
:=
/- dEAduction
PrettyName
    Le passage au complémentaire renverse les inclusions, implication
Description
    Si A est inclus dans B, alors le complémentaire de A contient le complémentaire de B
-/
begin
    todo
end

lemma exercise.inclusion_complement_II :
A ⊆ B ↔ set.compl B ⊆ set.compl A
:=
/- dEAduction
PrettyName
    Le passage au complémentaire renverse les inclusions, équivalence
Description
    Si A est inclus dans B, alors le complémentaire de A contient le complémentaire de B
-/
begin
    todo
end

/- Autres : différence-/

end complementaire



-- Ajouter :  4. relations ?

namespace produits_cartesiens
/- dEAduction
PrettyName
    Produits cartésiens
-/


-- Peut-on en faire une définition ?
lemma theorem.type_produit :
∀ z:X × Y, ∃ x:X, ∃ y:Y, z = (x,y)
:=
/- dEAduction
PrettyName
    Element d'un produit cartésien de deux ensembles
-/
begin
    todo
end


lemma definition.produit_de_parties {A : set X} {B : set Y}
{x:X} {y:Y} :
(x,y) ∈ set.prod A B ↔ x ∈ A ∧ y ∈ B
:=
/- dEAduction
PrettyName
    Produit cartésien de deux parties
-/
begin
    todo
end


lemma exercise.produit_avec_intersection
(A : set X) (B C : set Y) :
set.prod A (B ∩ C) = (set.prod A B) ∩ (set.prod A C)
:=
begin
    todo,
end


end produits_cartesiens
---------------
-- SECTION 3 --
---------------
namespace applications_I
/- dEAduction
PrettyName
    Applications et opérations ensemblistes
-/


-- variables applications --

variables  {A A': set X}
variables {f: X → Y} {B B': set Y}
-- variables {I : Type} {E : I → set X} {F : I → set Y}
variables {I : index_set} {E : set_family I X} {F : set_family I Y}
variables (g : Y → Z) (h : X → Z)

-- a-t-on besoin de ceci ?
-- lemma theorem.egalite_fonctions : f = f' ↔ ∀ x : X, f(x) = f'(x) :=
--  function.funext_iff


-----------------
-- DEFINITIONS --
-----------------
namespace definitions
/- dEAduction
PrettyName
    Définitions
-/

lemma definition.image_directe (y : Y) :  y ∈ f '' A ↔ ∃ x : X, x ∈ A ∧  f x = y :=
begin
    todo
end

lemma definition.image_reciproque (x:X) : x ∈ f  ⁻¹' B ↔ f(x) ∈ B :=
begin
    todo
end

lemma definition.composition {x:X}:
composition g f x = g (f x)
:=
begin
    todo,
end

lemma definition.egalite_fonctions (f' : X → Y) :
f = f' ↔ ∀ x, f x = f' x :=
/- dEAduction
PrettyName
    Egalité de deux fonctions
-/
begin
    exact function.funext_iff,
end


lemma definition.Identite (f₀: X → X) :
f₀ = Identite ↔ ∀ x, f₀ x = x :=
/- dEAduction
PrettyName
    Application identité
-/
begin
    apply definition.egalite_fonctions,
end

end definitions

---------------
-- EXERCICES --
---------------
namespace exercices
/- dEAduction
PrettyName
    Exercices
-/
open applications_I.definitions

lemma exercise.image_de_reciproque : f '' (f ⁻¹' B)  ⊆ B :=
/- dEAduction
PrettyName
    Image de l'image réciproque
-/
begin
    todo
end

lemma exercise.reciproque_de_image : A ⊆ f ⁻¹' (f '' A) :=
/- dEAduction
PrettyName
    Image réciproque de l'image
-/
begin
    todo
end

lemma exercise.image_reciproque_inter :  f ⁻¹'  (B∩B') = f ⁻¹'  (B) ∩ f ⁻¹'  (B') :=
/- dEAduction
PrettyName
    Image réciproque d'une intersection de deux ensembles
-/
begin
    todo
end

lemma  exercise.image_reciproque_union  : f ⁻¹' (B ∪ B') = f ⁻¹' B ∪ f ⁻¹' B'
:=
/- dEAduction
PrettyName
    Image réciproque d'une union de deux ensembles
-/
begin
    todo
end

-- set_option pp.width 100
lemma exercise.image_reciproque_inter_quelconque :
(f ⁻¹'  (set.Inter (F))) = set.Inter (λ i, f ⁻¹' (F i): set_family I X)
-- (f ⁻¹'  (set.Inter (λ i, F i))) = set.Inter (λ i, f ⁻¹' (F i))
:=
/- dEAduction
PrettyName
    Image réciproque d'une intersection quelconque
-/
begin
    todo
end

lemma exercise.image_reciproque_union_quelconque :
(f ⁻¹'  (set.Union (λ i, F i))) = set.Union (λ i, f ⁻¹' (F i))
:=
/- dEAduction
PrettyName
    Image réciproque d'une union quelconque
-/
begin
    todo
end

lemma exercise.image_inter_inclus_inter_images :
f '' (A∩A') ⊆ f '' (A) ∩ f '' (A')
:=
/- dEAduction
PrettyName
    Image d'une intersection
-/
begin
    todo
end


lemma exercise.reciproque_complementaire_I :
f ⁻¹' (set.compl B) ⊆ set.compl (f ⁻¹' B)
:=
/- dEAduction
PrettyName
    Image réciproque du complémentaire, inclusion
-/
begin
    todo
end

lemma exercise.reciproque_complementaire_II :
f ⁻¹' (set.compl B) = set.compl (f ⁻¹' B)
:=
/- dEAduction
PrettyName
    Image réciproque du complémentaire, égalité
-/
begin
    todo
end

lemma exercise.image_reciproque.composition
(C: set Z)
:
((composition g f) )⁻¹' C = f ⁻¹' (g ⁻¹' C)
:=
begin
    todo
end

end exercices
end applications_I

----------------
-- SUBSECTION --
----------------
namespace applications_II
/- dEAduction
PrettyName
    Injections et surjections
-/

-- variables injections_surjections --
variables (f: X → Y) (g : Y → Z) (h : X → Z)

-----------------
-- DEFINITIONS --
-----------------
namespace definitions
/- dEAduction
PrettyName
    Définitions
-/

lemma definition.injectivite :
injective f ↔ ∀ x y : X, (f x = f y → x = y)
:=
/- dEAduction
PrettyName
    Application injective
ImplicitUse
    True
-/
begin
    refl,
end

lemma definition.surjectivite :
surjective f ↔ ∀ y : Y, ∃ x : X, y = f x
:=
/- dEAduction
PrettyName
    Application surjective
ImplicitUse
    True
-/
begin
    refl,
end

-- A bouger, mais à enlever de tous les exos où ça ne sert pas !
lemma definition.existe_un_unique
(P : X → Prop) :
(∃! (λx,  P x)) ↔  (∃ x : X, (P x ∧ (∀ x' : X, P x' → x' = x)))
:=
/- dEAduction
PrettyName
    ∃! : existence et unicité
-/
begin
    todo
end

lemma definition.bijectivite_1 :
bijective f ↔ (injective f ∧ surjective f)
:=
/- dEAduction
PrettyName
    Application bijective (première définition)
-/
begin
    todo
end

lemma definition.bijectivite_2 :
bijective f ↔ ∀ y : Y, exists_unique (λ x, y = f x)
:=
/- dEAduction
PrettyName
    Application bijective (seconde définition)
-/
begin
    refl,
end

end definitions



---------------
-- EXERCICES --
---------------
namespace exercices
/- dEAduction
PrettyName
    Exercices
-/

open applications_II.definitions

lemma exercise.composition_injections
(H1 : injective f) (H2 : injective g)
:
injective (composition g f)
:=
/- dEAduction
PrettyName
    Composition d'injections
-/
begin
    todo
end

lemma exercise.composition_surjections
(H1 : surjective f) (H2 : surjective g) :
surjective (composition g f)
:=
/- dEAduction
PrettyName
    Composition de surjections
-/
begin
    todo
end

lemma exercise.injective_si_compo_injective
(H1 : injective (composition g f)) :
injective f
:=
/- dEAduction
PrettyName
    Injective si composition injective
-/
begin
    todo
end

lemma exercise.surjective_si_compo_surjective
(H1 : surjective (composition g f)) :
surjective g
:=
/- dEAduction
PrettyName
    Surjective si composition surjective
-/
begin
    todo
end

lemma exercise.injective_ssi_inverse_gauche : (injective f) ↔
∃ F: Y → X, (composition F f) = Identite :=
/- dEAduction
PrettyName
    (x) Injectivité et inverse à gauche
-/
begin
    todo
end

lemma exercise.surjective_ssi_inverse_droite : (surjective f) ↔
∃ F: Y → X, (composition f F) = Identite :=
/- dEAduction
PrettyName
    (*) Surjectivité et inverse à droite
-/
begin
    todo
end

lemma exercise.bijective_ssi_inverse :
(bijective f) ↔ ∃ g : Y → X,
composition g f = Identite ∧ composition f g  = Identite
:=
/- dEAduction
PrettyName
    (**) Bijectivité et existence d'une application réciproque
-/
begin
    todo
end

lemma exercise.unicite_inverse :
(bijective f) → exists_unique (λ g : Y → X,
composition g f = Identite)
:=
/- dEAduction
PrettyName
    (+) Unicité de la réciproque d'une application bijective
-/
begin
    todo
end



lemma exercise.Cantor (f : X → set X):
 ¬ surjective f
:=
/- dEAduction
PrettyName
    (+) Théorème de Cantor : il n'y a pas de surjection d'un ensemble vers l'ensemble de ses parties
-/
begin
    -- by_contradiction H14,
    -- let A := {x | x ∉ f x}, have H15 : A = {x | x ∉ f x}, refl,
    -- rw theorie_des_ensembles.applications_II.definitions.definition.surjectivite at H14,
    -- have H16 := H14 A,
    -- cases H16 with x H17,
    -- cases (classical.em (x ∈ A)) with H22 H23,
    -- {
    --     have H22b: x ∉ A,
    --     rw H15 at H22,
    --     rw generalites.definition.ensemble_extension at H22,
    --     rw H17, assumption,
    --     contradiction,
    -- },
    -- {
    --     have H22b: x ∈ A,
    --     rw H15 at H23,
    --     -- simp only[ensemble_extension] at H23,
    --     rw generalites.definition.ensemble_extension at H23,
    --     push_neg at H23,
    --     rw H17, assumption,
    --     contradiction
    -- }
    todo
end


end exercices

end applications_II

-----------------------------------
-----------------------------------
namespace exercices_supplementaires


-- relations : rel d'eq implique classes égales ou disjointes
-- les images réciproques des singletons forment une partition
-- bijective ssi inversible à g et d et inverses coincident


lemma exercise.exercice_ensembles_1
(A B : set X) :
A ⊆ B ↔ A ∩ B = A
:=
/- dEAduction
PrettyName
    Caractérisation de l'inclusion par l'intersection
-/
begin
    todo
end

lemma exercise.complement_intersection_2
(A B : set X):
set.compl (A ∩  B) = (set.compl A) ∪ (set.compl B)
:=
/- dEAduction
PrettyName
    Complémentaire d'une intersection
-/
begin
    todo
end


lemma exercise.exercice_ensembles_3
(A B : set X) :
A ∩ B = A ∪ B → A = B
:=
/- dEAduction
PrettyName
    Quand l'intersection égale l'union
-/
begin
    todo
end

lemma exercise.exercice_ensembles_4a
(A B C : set X) :
A ∩ B = A ∩ C ∧ (set.compl A) ∩ B = (set.compl A) ∩ C → B ⊆ C
:=
/- dEAduction
PrettyName
    Caractérisation par intersection avec A et son complémentaire, I
-/
begin
    todo
end

lemma exercise.exercice_ensembles_4b
(A B C : set X) :
A ∩ B = A ∩ C ∧ (set.compl A) ∩ B = (set.compl A) ∩ C → B = C
:=
/- dEAduction
PrettyName
    Caractérisaton par intersection avec A et son complémentaire, II
-/
begin
    todo
end


lemma exercise.exercice_ensembles_5
(A B C : set X) :
A ∩ B = A ∩ C ∧ A ∪ B = A ∪ C → B = C
:=
/- dEAduction
PrettyName
    Même union et même intersection
-/
begin
    todo
end

--def diff {X : Type} (A B : set X) := {x ∈ A | ¬ x ∈ B}
--notation A `\\` B := diff A B

-- def symmetric_difference {X : Type} (A B : set X) := (A ∪ B) \ (A ∩ B)
-- notation A `Δ` B := symmetric_difference A B

namespace difference_et_difference_symetrique
/- dEAduction
PrettyName
    Différence et différence symétrique
-/

namespace definitions
/- dEAduction
PrettyName
    Définitions
-/


lemma definition.difference
(A B : set X) (x : X) :
x ∈ (A \ B) ↔ x ∈ A ∧ x ∉ B
:=
/- dEAduction
PrettyName
    Différence de deux ensembles
-/
begin
    refl,
end


lemma definition.difference_symetrique
(A B : set X) :
(A Δ B) =  (A ∪ B) \ (A ∩ B)
:=
/- dEAduction
PrettyName
    Différence symétrique de deux ensembles
-/
begin
    refl,
end

end definitions


namespace exercices
/- dEAduction
PrettyName
    Exercices
-/

lemma exercise.difference_symetrique_1
(A B : set X) :
(A Δ B) = (A \ B) ∪ (B \ A)
:=
/- dEAduction
PrettyName
    Différence symétrique I
-/
begin
    todo
end


lemma exercise.difference_symetrique_2
(A B : set X) :
(A Δ B) = (B Δ A)
:=
/- dEAduction
PrettyName
    (*) Différence symétrique II
-/
begin
    todo
end


lemma exercise.difference_symetrique_3
(A B C : set X) :
((A Δ B) Δ C) = (A Δ (B Δ C))
:=
/- dEAduction
PrettyName
    (**) Différence symétrique III
-/
begin
    todo
end


lemma exercise.difference_symetrique_4 :
∃! (λE : set X, ∀ A : set X, (A Δ E) = A) :=
/- dEAduction
PrettyName
    (+) Différence symétrique VI
-/
begin
    todo
end


lemma exercise.difference_symetrique_5 (A : set X) :
exists_unique (λA' : set X, (A Δ A') = set.univ)
:=
/- dEAduction
PrettyName
    (+) Différence symétrique V
-/
begin
    todo
    -- use complement A, 
    -- norm_num,
end

lemma exercise.difference_symetrique_6
(A B : set X) :
(A Δ B) = ∅ ↔ A = B
:=
/- dEAduction
PrettyName
    (+) Différence symétrique VI
-/
begin
    todo
end

end exercices

end difference_et_difference_symetrique

-- applications
variable (f: X → Y)

namespace applications

lemma exercise.exercice_applications_1
(A B : set X) :
A ⊆ B → f '' A ⊆ f '' B
:=
/- dEAduction
PrettyName
    Image directe et inclusion
-/
begin
    todo
end

lemma exercise.exercice_applications_2
(A B : set X) :
f '' (A ∪ B)  = f '' A ∪ f '' B
:=
/- dEAduction
PrettyName
    Image d'une union
-/
begin
    todo
end

open applications_II.definitions
lemma exercise.exercice_factorisation_I
(g : Y → Z) (h: X → Z) :
(∃ f: X → Y, h = (composition g f)) ↔ h '' set.univ ⊆ g '' set.univ
:=
/- dEAduction
PrettyName
    (+) Factorisation I
-/
begin
    todo
end


lemma exercise.exercice_factorisation_II
(f : X → Y) (h: X → Z) :
(∃ g: Y → Z, h = (composition g f)) ↔ (∀ x y, (f x = f y → h x = h y))
:=
/- dEAduction
PrettyName
    (+) Factorisation II
-/
begin
    todo
end


-- TODO: ajouter exoset ficall.pdf exos (140 bijections) 141 142 146

lemma exercise.injectivite_surjecivite_1 (f: X → Y) (g: Y → Z)
(H1 : injective (composition g f)) (H2 : surjective f)
:
injective g
:=
/- dEAduction
PrettyName
    Injectivité et surjectivité I
-/
begin
    todo
end

lemma exercise.injectivite_surjecivite_2 (f: X → Y) (g: Y → Z)
(H1 : surjective (composition g f)) (H2 : injective g)
:
surjective f
:=
/- dEAduction
PrettyName
    Injectivité et surjectivité II
-/
begin
    todo
end



lemma exercise.injectivite_categorielle
(f: Y → Z):
(injective f) → (∀X: Type, ∀ g h : X → Y, (composition f g) = (composition f h) → g = h)
:=
/- dEAduction
PrettyName
    Injectivité catégorielle
-/
begin
    todo
end

lemma exercise.surjectivite_categorielle
(f: X → Y):
(surjective f) →  (∀Z: Type, ∀ g h : Y → Z, (composition g f ) = (composition h f ) → g = h)
:=
/- dEAduction
PrettyName
    Surjectivité catégorielle
-/
begin
    todo
end

end applications


end exercices_supplementaires

end theorie_des_ensembles

end course