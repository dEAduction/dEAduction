import data.set
import tactic
-- import data.nat.basic

-- dEAduction tactics
import structures2      -- hypo_analysis, targets_analysis
import utils            -- no_meta_vars
import user_notations   -- notations that can be used in deaduction UI for a new object
import push_neg_once    -- pushing negation just one step
-- import compute

-- dEAduction definitions
import set_definitions
-------------------------
-- dEAduction FIXME --
-------------------------
/-
- Union quelconque, à gérer (index set)
- les defs implicites ne marchent pas ?! intersection, ouvert, boule, etc.
(ex : découper "a dans A inter B" qui est dans le contexte)

-/

-------------------------
-- dEAduction METADATA --
-------------------------
/- dEAduction
Title
    Topologie
Author
    Garance Henrion et Frédéric Le Roux
Institution
    Université du monde
Description
    Premier essai de topologie
Display
  boule --> ("B", "(", -2, ",", -1, ")")
  dist  --> ("d", "(", -2, ",", -1, ")")
-/

local attribute [instance] classical.prop_decidable


------------
-- ESSAIS --
------------
open set

section course
-----------
-- DEBUT --
-----------



namespace logique

lemma definition.iff {P Q : Prop} : (P ↔ Q) ↔ ((P → Q) and (Q → P)) :=
/- dEAduction
PrettyName
    Equivalence logique
-/
begin
  exact iff_def,
end

lemma theorem.contraposition {P Q: Prop} : 
P → Q ↔ (non Q) → (non P) :=
begin
  tautology,
end

end logique


namespace theorie_des_ensembles
/- dEAduction
PrettyName
    Théorie des ensembles
-/

variables {X Y Z: Type}

lemma definition.inclusion {A B : set X} : A ⊆ B ↔ ∀ {x:X}, x ∈ A → x ∈ B :=
/- dEAduction
ImplicitUse
  True
-/
begin
    exact iff.rfl
end

lemma definition.egalite_deux_ensembles {A A' : set X} :
(A = A') ↔ ( ∀ x, x ∈ A ↔ x ∈ A' ) :=
/- dEAduction
PrettyName
    Egalité de deux ensembles
-/
begin
     exact set.ext_iff
end

-- Unfortunately split cannot work
lemma definition.double_inclusion {A A' : set X} :
A = A' ↔ (A ⊆ A' ∧ A' ⊆ A) :=
/- dEAduction
PrettyName
    Double inclusion
ImplicitUse
  True
-/
begin
    exact set.subset.antisymm_iff
end

lemma definition.ensemble_vide
{A: set X} :
(A = ∅) ↔ ∀ x : X, x ∉ A
:=
begin
    exact eq_empty_iff_forall_not_mem,
end

lemma definition.ensemble_non_vide
{A: set X} :
(A ≠ ∅) ↔ ∃ x : X, x ∈ A
:=
/- dEAduction
ImplicitUse
  True
-/
begin
    todo
end

-- FIXME: l'utilisation implicite ne fonctionne pas vraiment !
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

lemma definition.image_reciproque {B: set Y} {f: X → Y} (x:X) : x ∈ f  ⁻¹' B ↔ f(x) ∈ B :=
begin
    todo
end

lemma definition.surjective (f: X → Y):
surjective f ↔ ∀ y, ∃ x, f x = y
:=
begin
  todo
end

lemma theorem.image_reciproque_union (f: X → Y):
∀ B B' : set Y, f ⁻¹' ( B ∪ B') = f ⁻¹' (B) ∪ f ⁻¹' (B')
:=
/- dEAduction
PrettyName
  Image réciproque et union
-/
begin
  todo
end

lemma theorem.image_reciproque_inter (f: X → Y) :
∀ A' B' : set Y, f ⁻¹' ( A' ∩ B') = f ⁻¹' (A') ∩ f ⁻¹' (B')
:=
/- dEAduction
PrettyName
  Image réciproque et intersection
-/
begin
  todo
end

lemma exercise.image_reciproque_vide (f: X → Y):
f ⁻¹' (∅) = ∅
:=
/- dEAduction
PrettyName
  Image réciproque ensemble vide
-/
begin
  todo
end

lemma exercise.image_reciproque_univ (f: X → Y):
f ⁻¹' (univ) = univ
:=
/- dEAduction
PrettyName
  Image réciproque de l'ensemble d'arrivée
-/
begin
  todo
end

lemma exercise.image_reciproque_non_vide (f: X → Y) (H: surjective f)
(A: set Y):
(A ≠ ∅ → f ⁻¹' A ≠ ∅)
:=
/- dEAduction
PrettyName
  Image réciproque d'un ensemble non vide
-/
begin
  todo
end

-- example (f: X → Y) (H: surjective f)
-- (A: set Y):
-- (A ≠ ∅ → f ⁻¹' A ≠ ∅) :=
-- begin
-- intro H1,
-- have H := exercise.image_reciproque_non_vide _ _ _ H A H1,
-- end

def constant_ (f: X → Y) := ∃ y, ∀ x, f x = y

lemma definition.application_constante (f: X → Y) :
(constant_ f) ↔ ∃ y, ∀ x, f x = y
:=
begin
  refl
end


lemma exercise.composition_image_reciproque
(f: X→ Y) (g: Y → Z) (C: set Z) : 
(composition g f) ⁻¹' C = f ⁻¹' (g ⁻¹' C)
:=
/- dEAduction
PrettyName
    Image réciproque par une composition
-/
begin
    todo
end


end theorie_des_ensembles



class topologie (X : Type) :=
  (ouvert : (set X) → Prop)
  (vide_ : ouvert ∅)
  (intersec : ∀ s t,  ouvert s → ouvert t → ouvert (s ∩ t))
  --(union_ : ∀ S, (∀ t ∈ S, ouvert t) → ouvert (sUnion S))
  (union_top: ∀ {I : index_set} {O : I → set X}, (∀ i, ouvert (O i)) → ouvert (Union O))
  (total : ouvert univ)

open topologie

namespace definitions

def EspaceTopologique := Type 
variables {X Y : EspaceTopologique} [topologie X] [topologie Y]

-- Tentative de def de la topologie en tant qu'ensemble de parties:
-- def (T: set (set X)) := {(O: set X) | ouvert O} 

lemma theoreme.vide : (ouvert (∅ : set X)) := vide_ 

lemma theoreme.intersec : ∀ U V : set X, ouvert U → ouvert V → ouvert (U ∩ V)  := topologie.intersec

lemma theoreme.union : ∀ {I : index_set} {O : I → set X}, (∀ i, ouvert (O i)) → ouvert (Union O) := @union_top _ _ 

lemma theoreme.total : ouvert (univ : set X) := topologie.total



-- On a par définition qu'une intersection simple d'ouverts est un ouvert
-- On veut montrer qu'une intersection finie d'ouverts est un ouvert
--lemma theoreme.intersecfinie {h : topologie X} : 

-- variables {Y : EspaceTopologique} [topologie Y]

def continue (f : X → Y) :=
∀ S : set Y, ouvert S → ouvert (f ⁻¹' S)


lemma definition.continue {f : X → Y}: continue f ↔ 
∀ O : set Y, ouvert O → ouvert (f ⁻¹' O) :=
/- dEAduction
ImplicitUse
    True
-/
begin
  refl
end


def connexe (X : EspaceTopologique) [topologie X] := 
∀ U V : set X, ouvert U → ouvert V → U ∩ V = ∅ → U ∪ V = univ → U ≠ ∅ → V = ∅


lemma definition.connexe : connexe X ↔ 
(∀ U V : set X, (ouvert U ∧ ouvert V ∧ U ∩ V = ∅ ∧ U ∪ V = univ ∧ U ≠ ∅) → V = ∅)
:=
/- dEAduction
ImplicitUse
    True
-/
begin
  todo
end


inductive TypePair : Type
  | zero : TypePair
  | un : TypePair

instance pair_has_zero : has_zero TypePair := ⟨ TypePair.zero ⟩ 
instance pair_has_one : has_one TypePair := ⟨ TypePair.un ⟩ 

instance topologie_pair : topologie TypePair :=
{ ouvert := (λ O, true),
  vide_ :=
    begin
      todo 
    end,
  intersec :=
    begin
      todo 
    end,
  union_top :=
    begin
      todo 
    end,
  total :=
    begin
      todo 
    end,
}


end definitions

namespace exercices
open definitions
open theorie_des_ensembles

variables {X Y Z : EspaceTopologique} [topologie X] [topologie Y] [topologie Z]

lemma exercise.compo_continue (f : X → Y) (g : Y → Z) (H1 : continue f) (H2 : continue g):
continue (composition g f) :=
begin
  todo
end

lemma exercise.caract_connex : 
connexe X ↔ ∀ f : X → TypePair, continue f → constant_ f
:=
begin
  todo
end


lemma exercise.imageConnexe (f : X → Y) (H1 : continue f) (H2 : connexe X) (H3 : surjective f):
connexe Y :=
begin
  todo
end

def connexePartie {X : EspaceTopologique} [topologie X] (A : set X):= 
∀ U V : set X, ouvert U → ouvert V → A ∩ U ∩ V = ∅ → A ⊂ U ∪ V → A ∩ U ≠ ∅ → A ∩ V = ∅

lemma exercise.imageConnexePartie (f : X → Y) (h1 : continue f) (h2 : connexe X):
connexePartie (f '' univ) :=
begin
  todo
end



end exercices


end course



