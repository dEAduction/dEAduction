import data.set
import tactic

-- dEAduction imports
import logics
import definitions
import structures

local attribute [instance] classical.prop_decidable

-----------------
-- Course Data --
-----------------
/- dEAduction
CourseTitle
    Théorie des Ensembles
Author
    Camille Nous
Date
    08/2020
University
    Some French University
CourseId
    1MA999
-/

------------------
-- COURSE TITLE --
------------------
namespace theorie_des_ensembles
/- dEAduction
PrettyName
    Théorie des ensembles
-/

-- global variable --
variable {X : Type}

------------------------
-- COURSE DEFINITIONS --
------------------------
lemma definition.inclusion (A B : set X) : A ⊆ B ↔ ∀ {{x:X}}, x ∈ A → x ∈ B :=
iff.rfl

lemma definition.egalite_deux_ensembles {A A' : set X} : (A = A') ↔ ( ∀ x, x ∈ A ↔ x ∈ A' ) :=
/- dEAduction
PrettyName
    Egalité de deux ensembles
-/
by exact set.ext_iff

lemma theorem.double_inclusion {A A' : set X} : (A ⊆ A' ∧ A' ⊆ A) → A = A' :=
/- dEAduction
PrettyName
    Double inclusion
-/
begin
    exact set.subset.antisymm_iff.mpr
end






---------------
-- SECTION 1 --
---------------
namespace unions_et_intersections
-- variables unions_et_intersections --
variables {A B C : set X}

-----------------
-- DEFINITIONS --
-----------------
lemma definition.intersection_deux_ensembles (A B : set X) (x : X) :  x ∈ A ∩ B ↔ ( x ∈ A ∧ x ∈ B) :=
iff.rfl
/- dEAduction
PrettyName
    Intersection de deux ensembles
-/

lemma definition.intersection_quelconque_ensembles (I : Type) (O : I → set X)  (x : X) : (x ∈ set.Inter O) ↔ (∀ i:I, x ∈ O i) :=
set.mem_Inter
/- dEAduction
PrettyName
    Intersection d'une famille d'ensembles quelconque
-/

lemma definition.union_deux_ensembles  (A : set X) (B : set X) (x : X) :  x ∈ A ∪ B ↔ ( x ∈ A ∨ x ∈ B) :=
iff.rfl
/- dEAduction
PrettyName
    Union de deux ensembles
-/

lemma definition.union_quelconque_ensembles (I : Type) (O : I → set X)  (x : X) : (x ∈ set.Union O) ↔ (∃ i:I, x ∈ O i) :=
set.mem_Union
/- dEAduction
PrettyName
    Union d'une famille d'ensembles quelconque
-/


---------------
-- EXERCICES --
---------------
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

lemma exercise.inter_distributive_union : A ∪ (B ∩ C)  = (A ∪ B) ∩ (A ∪ C) :=
/- dEAduction
PrettyName
    L'union est distributive par rapport à l'intersection
-/
begin
    sorry
end

end unions_et_intersections






---------------
-- SECTION 2 --
---------------
namespace complementaire
-- variables complementaire --
variables  {A B : set X}
variables {I : Type} {E F : I → set X}
notation `∁`A := set.compl A

-----------------
-- DEFINITIONS --
-----------------
lemma definition.complement {A : set X} {x : X} : x ∈ set.compl A ↔ x ∉ A :=
/- dEAduction
PrettyName
    Complémentaire
-/
by finish

--lemma definition.difference_d_ensembles {A B : set X} {x : X} : x ∈ B \ A ↔ (x ∈ B ∧ x ∉ A) :=
-- iff.rfl


---------------
-- EXERCICES --
---------------
lemma exercise.complement_complement : (set.compl (set.compl A)) =A :=
/- dEAduction
PrettyName
    Complémentaire du complémentaire
Description
    Tout ensemble est égal au complémentaire de son complémentaire
-/
begin
    sorry
end

lemma exercise.complement_union_deux : set.compl (A ∪ B) = (set.compl A) ∩ (set.compl B) :=
/- dEAduction
PrettyName
    Complémentaire d'union I
Description
    Le complémentaire de l'union de deux ensembles égale l'intersection des complémentaires
-/
begin
    sorry
end

-- set_option pp.all true
lemma exercise.complement_union_quelconque  (H : ∀ i, F i = set.compl (E i)) : set.compl (set.Union E) = set.Inter F :=
/- dEAduction
PrettyName
    Complémentaire d'union II
Description
    Le complémentaire d'une réunion quelconque égale l'intersection des complémentaires
-/
begin
    sorry
end

lemma exercise.inclusion_complement :
A ⊆ B → set.compl B ⊆ set.compl A
:=
/- dEAduction
PrettyName
    Le passage au complémentaire renverse les inclusions
Description
    Si A est inclus dans B, alors le complémentaire de A contient le complémentaire de B
-/
begin
    sorry
end

/- Autres : différence-/

end complementaire



-- Ajouter : 3. produit cartésien, 4. relations ?
-- comment définit-on un produit cartésien d'ensembles ?



---------------
-- SECTION 3 --
---------------
namespace applications
-- variables applications --
notation f `⟮` A `⟯` := f '' A
notation f `⁻¹⟮` A `⟯` := f  ⁻¹' A

variables  {A A': set X}
variables {Y: Type} {f: X → Y} {B B': set Y}
variables {I : Type} {E : I → set X} {F : I → set Y}

-- a-t-on besoin de ceci ?
-- lemma theorem.egalite_fonctions : f = f' ↔ ∀ x : X, f(x) = f'(x) :=
--  function.funext_iff


-----------------
-- DEFINITIONS --
-----------------
lemma definition.image_directe (y : Y) : y ∈ f '' A ↔ ∃ x : X, x ∈ A ∧  f x = y :=
/- dEAduction -/
begin
    unfold set.image,
    sorry
end

lemma definition.image_reciproque (x:X) : x ∈ f  ⁻¹' B ↔ f(x) ∈ B :=
/- dEAduction -/
begin
    sorry
end


---------------
-- EXERCICES --
---------------
lemma exercise.image_de_reciproque : f '' (f ⁻¹' B)  ⊆ B :=
/- dEAduction -/
begin
  sorry
end

lemma exercise.reciproque_de_image : A ⊆ f ⁻¹' (f '' A) :=
/- dEAduction -/
begin
    sorry
end

lemma exercise.image_reciproque_inter :  f ⁻¹'  (B∩B') = f ⁻¹'  (B) ∩ f ⁻¹'  (B') :=
/- dEAduction -/
begin
    sorry
end

lemma  exercise.image_reciproque_union  : f ⁻¹' (B ∪ B') = f ⁻¹' B ∪ f ⁻¹' B'
:=
/- dEAduction -/
begin
    sorry
end

lemma exercise.image_reciproque_inter_quelconque (H : ∀ i:I,  (E i = f ⁻¹' (F i))) :
(f ⁻¹'  (set.Inter F)) = set.Inter E
:=
/- dEAduction -/
begin
    sorry
end

/- Idem union quelconques -/

lemma exercise.image_inter_inclus_inter_images :
f '' (A∩A') ⊆ f '' (A) ∩ f '' (A')
:=
begin
    sorry
end

lemma exercise.reciproque_complementaire :
f ⁻¹' (set.compl B) = set.compl (f ⁻¹' B)
:=
begin
    sorry
end


----------------
-- SUBSECTION --
----------------
namespace injections_surjections
/- dEAduction
PrettyName
    injections et surjections
-/


-- variables injections_usrjections --
variables {Z : Type} {g : Y → Z} {h : X → Z}
def injective (f₀ : X → Y) := ∀ x y : X, (f₀ x = f₀ y → x = y)
def surjective (f₀ : X → Y) := ∀ y : Y, ∃ x : X, f₀ x = y
def composition (g₀ : Y → Z) (f₀ : X → Y) := λx:X, g₀ (f₀ x)
#print injective

-----------------
-- DEFINITIONS --
-----------------
lemma definition.injectivite :
injective f ↔ ∀ x y : X, (f x = f y → x = y)
:=
/- dEAduction -/
begin
    unfold injective,
end

lemma definition.surjectivite :
surjective f ↔ ∀ y : Y, ∃ x : X, f x = y
:=
/- dEAduction -/
begin
    unfold surjective,
end

lemma definition.composition :
h = composition g f ↔ ∀ x : X, h x = g (f x)
:=
begin
    unfold composition,
    sorry
end


---------------
-- EXERCICES --
---------------
lemma exercise.composition_injections (H0 : h = composition g f)
(H1 : injective f) (H2 : injective g) :
injective h
:=
/- dEAduction -/
begin
    sorry
end

lemma exercise.composition_surjections (H0 : h = composition g f)
(H1 : surjective f) (H2 : surjective g) :
surjective h
:=
/- dEAduction -/
begin
    sorry
end

lemma exercise.injective_si_coompo_injective (H0 : h = composition g f)
(H1 : injective h) :
injective f
:=
/- dEAduction -/
begin
    sorry
end

lemma exercise.surjective_si_coompo_surjective (H0 : h = composition g f)
(H1 : surjective h) :
surjective g
:=
/- dEAduction -/
begin
    sorry
end


end injections_surjections

end applications

end theorie_des_ensembles