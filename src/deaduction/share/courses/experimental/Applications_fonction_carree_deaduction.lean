/-
Feuille d'exercice pour travailler les applications sur les ensembles - Exemples concrets avec la fonction carrée
-/

import data.set
import data.real.basic
import init


import tactic

-- dEAduction tactics
import deaduction_all_tactics
-- import compute
-- import structures2      -- hypo_analysis, targets_analysis
-- import utils            -- no_meta_vars
-- import user_notations   -- notations that can be used in deaduction UI for a new object
-- import push_neg_once


-- dEAduction definitions
import set_definitions

-- General principles :
-- Type should be defined as parameters, in order to be implicit everywhere
-- other parameters are implicit in definitions, i.e. defined using '{}' (e.g. {A : set X} )
-- but explicit everywhere else, i.e. defined using '()' (e.g. (A : set X) )
-- each definition must be an iff statement or an equality
-- (since it will be called with 'rw' or 'symp_rw')

-------------------------
-- dEAduction METADATA --
-------------------------
-- logic names ['and', 'or', 'negate', 'implicate', 'iff', 'forall', 'exists']
-- proofs names ['use_proof_methods', 'new_object', 'apply', 'assumption']
-- magic names ['compute']
-- proof methods names ['cbr', 'contrapose', 'absurdum', 'sorry']

/- dEAduction
Title
    Théorie des ensembles : applications - FONCTION CARREE sur ℝ
Author
    Isabelle Dubois 
Institution
    Université de Lorraine
Description
    Ce cours correspond à un cours standard de théorie "élémentaire" des ensembles. Partie Applications.
    
    Il propose de travailler les différentes notions avec l'aide de la fonction
    carrée définie sur ℝ.
    
AvailableExercises
	NONE
-/

/- RESTES
    sqrt --> ( "racine (",-1, ")")
Display
    segment --> ( "[",-2, " , ", -1, "]")
AvailableDefinitions
    ALL -sqrt
-/

local attribute [instance] classical.prop_decidable

---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course
variables {X Y Z: Type}
variables { n : nat}

open set
open nat

-- noncomputable theory

def segment (a b : ℝ) := {x | a ≤ x ∧ x ≤ b}

notation `[`a `, ` b `]` := segment a b

namespace generalites
/- dEAduction
PrettyName
    Généralités
-/

------------------------
-- COURSE DEFINITIONS --
------------------------

variables  {A A': set X}
variables {f: X → Y} {B B': set Y}

variables (g : Y → Z) (h : X → Z)

namespace generalites_ensembles
/- dEAduction
PrettyName
    Généralités sur les ensembles
-/

lemma definition.inclusion {A B : set X} : A ⊆ B ↔ ∀ {x:X}, x ∈ A → x ∈ B :=
/- dEAduction
ImplicitUse
    True
-/
begin
    todo
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
     todo
end
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

lemma theorem.double_inclusion (A A' : set X) :
A = A' ↔ (A ⊆ A' ∧ A' ⊆ A) 
:=
/- dEAduction
PrettyName
    Egalité de deux ensembles : double inclusion
-/
begin
    todo
end


lemma definition.ensemble_vide
(A: set X) :
(A = ∅) ↔ ∀ x : X, x ∉ A
:=
begin
    todo
end

lemma definition.ensemble_extension {X: Type}  {P : X → Prop} {x:X} :
 x ∈ {x | P x} ↔ P x
:=
/- dEAduction
PrettyName
    Ensemble défini en extension
-/
begin
    todo
end

lemma auxiliary_definition.singleton
{x x_0: X} :
(x ∈ ((singleton x_0): set X)) ↔ (x=x_0)
:=
begin
    refl,
end

lemma definition.singleton {X : Type} {x y : X}: x ∈ ({y} : set X) ↔ x = y
:=
/- dEAduction
PrettyName
    Ensemble singleton
AuxiliaryDefinitions
  generalites.generalites_ensembles.auxiliary_definition.singleton
-/
begin
    todo
end


lemma auxiliary_definition.paire
{x x_0 x_1: X} :
(x ∈ ((pair x_0 x_1): set X)) ↔ (x=x_0 ∨ x=x_1)
:=
begin
    refl,
end

lemma definition.paire {X : Type} {x y z : X}: z ∈ ({x, y} : set X) ↔ (z=x ∨ z = y)
:=
/- dEAduction
PrettyName
    Ensemble paire d'éléments
AuxiliaryDefinitions
  generalites.generalites_ensembles.auxiliary_definition.paire
-/
begin
    todo
end





end generalites_ensembles

namespace generalites_applications
/- dEAduction
PrettyName
    Généralités sur les applications
-/


lemma definition.image_directe (y : Y) : y ∈ f '' A ↔ ∃ x : X, x ∈ A ∧  f x = y :=
begin
    todo
end

lemma definition.image_reciproque (x:X) : x ∈ f  ⁻¹' B ↔ f(x) ∈ B :=
begin
    todo
end






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

end generalites_applications

end generalites

---------------
-- SECTION 1 --
---------------
namespace proprietes_fonction_carree
/- dEAduction
PrettyName
    Propriétés de la fonction carrée sur ℝ
-/
-- Ancien titre : Images directes et réciproques, in/sur/bi/jectivité
open generalites


variables  {A A': set X}
variables {B B': set Y}
--  {f: X → Y} 
variables (g : Y → Z) (h : X → Z)


---------------
-- EXERCICES --
---------------
@[simp] axiom carrefois :  ∀ x:ℝ, x^2= x*x 


lemma exercise.image_directe_0 ( f : ℝ → ℝ ) { B : set ℝ}  (H : ∀ x:ℝ, f x = x^2 ) (H2 : B  =  {x:ℝ |  0 ≤ x} ) :
∀ A : set ℝ  , (f '' A ) ⊆ B
:=
/- dEAduction
PrettyName
    L'image directe d'un ensemble est inclus dans ℝ_+
-/
begin
    todo
end


lemma exercise.image_directe_singleton  (a : ℝ) ( f : ℝ → ℝ ) (H : ∀ x:ℝ, f x = x^2 ) :
∃ b : ℝ, f '' ( { a} ) =  { b}
:=
/- dEAduction
PrettyName
    L'image directe d'un singleton est un singleton
-/
begin
    todo
end

lemma exercise.image_directe_paire ( f : ℝ → ℝ ) (a : ℝ)  (H : ∀ x:ℝ, f x = x^2 ) :
∃ b : ℝ, f '' ( { -a, a} ) =  { b}
:=
/- dEAduction
PrettyName
    L'image directe d'une paire peut être un singleton
-/
begin
    todo
end



lemma exercise.image_reciproque_singleton1 ( f : ℝ → ℝ ) (H : ∀ x:ℝ, f x = x^2 ) :
∃ a : ℝ, ∃ b : ℝ, f  ⁻¹'  ( { a} ) =  { b}
:=
/- dEAduction
PrettyName
    L'image réciproque d'un singleton peut être un singleton
-/
begin
    todo
end

lemma exercise.image_reciproque_singleton2 ( f : ℝ → ℝ ) (H : ∀ x:ℝ, f x = x^2 ) :
∃ a : ℝ, ∃ b : ℝ, ∃ c ≠ b, { b, c} ⊆ f  ⁻¹'  ( { a} ) 
:=
/- dEAduction
PrettyName
    L'image réciproque d'un singleton peut contenir deux éléments
-/
begin
    todo
end

lemma exercise.image_reciproque_singleton3 ( f : ℝ → ℝ ) (H : ∀ x:ℝ, f x = x^2 ) :
∃ a : ℝ, f  ⁻¹'  ( { a} ) =  ∅
:=
/- dEAduction
PrettyName
    L'image réciproque d'un singleton peut être vide
-/
begin
    todo
end

constant sqrt : ℝ → ℝ 

lemma definition.sqrt {x y:ℝ}:
 ( y = (sqrt x) ) ↔ ( ( 0 ≤ x) and ( 0 ≤ y) and y^2 = x )
:=
/- dEAduction
PrettyName
    Racine carrée
-/
begin
   todo
end


axiom sqrt_reel :  ∀ x:ℝ, (( 0 ≤ x) → (sqrt x) ∈ ( univ : set ℝ) )

lemma theorem.sqrt_reel :
 ∀  x:ℝ, (( 0 ≤ x) → (sqrt x) ∈ ( univ : set ℝ)  )
:= 
/- dEAduction
PrettyName
    Racine carrée est un réel
-/
begin
   todo
end


axiom sqrt_au_carre : ∀ x:ℝ, (( 0 ≤ x) → ( (sqrt x)^2 = x ))


axiom sqrt_positif : ∀ x:ℝ, (( 0 ≤ x) → (0 ≤ sqrt x ))

lemma theorem.sqrt_positif  :
∀ x:ℝ, ( ( 0 ≤  x ) →  (0 ≤  sqrt x )  )
:= 
/- dEAduction
PrettyName
   Racine carrée est positive
-/
begin
   todo
end


lemma theorem.sqrt_au_carre :
∀ x:ℝ, (( 0 ≤ x) → ( (sqrt x)^2 = x ))
:= 
/- dEAduction
PrettyName
   Racine carrée mise au carré
-/
begin
  todo
end



lemma exercise.image_directe_R ( f : ℝ → ℝ ) ( B : set ℝ ) (H1 : ∀ x:ℝ, f x = x^2 )  (H2 : B= {x:ℝ |  0 ≤ x}) :
f '' ( univ ) =  B
:=
/- dEAduction
Description
    L'image directe de ℝ est ℝ_+. Conseils : se servir de la double inclusion pour l'égalité d'ensemble, et d'un exercice précédent mis à disposition.
    
    A disposition : la fonction sqrt carrée, sous la forme sqrt (x), si 0 ≤ x.
PrettyName
    L'image directe de ℝ est ℝ_+ 
    
AvailableExercises
	image_directe_0
-/
begin
    todo
end

axiom sqrt_croissance : ∀ x:ℝ, ( (0 ≤ x) → ( ∀ y:ℝ, (( x ≤ y) → (sqrt x ≤ sqrt y ))) )

axiom sqrt_carres :
 ∀ x:ℝ, ( (0 ≤ x) → sqrt ( x^2 ) = x )

lemma theorem.sqrt_carres  :
  ∀ x:ℝ, ( (0 ≤ x) → sqrt ( x^2 ) = x )
:= 
/- dEAduction
PrettyName
    Racine carrée d'un carré parfait
    
-/
begin
   todo
end


lemma theorem.sqrt_croissance  :
 ∀ x:ℝ, ( (0 ≤ x) → ( ∀ y:ℝ, (( x ≤ y) → (sqrt x ≤ sqrt y ))) )
:= 
/- dEAduction
PrettyName
    Racine carrée est croissante
-/
begin
   todo
end

lemma definition.segment {x:ℝ} (a b : ℝ) :
 x ∈ segment a b ↔ ( a ≤ x ∧ x ≤ b )
:= 
/- dEAduction
PrettyName
    Segment réel
ImplicitUse
    True
-/
begin
    todo
end

@[simp] axiom sqrt4 :  sqrt 4 = 2
@[simp] axiom sqrt1 :  sqrt 1 = 1
@[simp] axiom sqrt0 :  sqrt 0 = 0


lemma exercise.image_directe_segment ( f : ℝ → ℝ ) (H : ∀ x:ℝ, f x = x^2 )  :
∃ a : ℝ, ∃ b: ℝ, f '' ( [ (-2) , 1] ) =  [ a , b]
:=
/- dEAduction
Description
    Quelle est l'image directe du segment [-2;1] ?
    
    A disposition : la fonction sqrt carrée, sous la forme sqrt (x), si 0 ≤ x.
PrettyName
    Quelle est l'image directe du segment [-2;1] ?


-/
begin
    todo
end

lemma exercise.image_reciproque_segment ( f : ℝ → ℝ ) (H : ∀ x:ℝ, f x = x^2 )  :
∃ a : ℝ, ∃ b: ℝ,  f  ⁻¹'  ( [ (-2) , 1] ) =  [ a , b]
:=
/- dEAduction
Description
    Quelle est l'image réciproque  du segment [-2;1] ?
    
    A disposition : la fonction sqrt carrée, sous la forme sqrt (x), si 0 ≤ x.
PrettyName
    Quelle est l'image réciproque  du segment [-2;1] ?
-/
begin
    todo
end


lemma exercise.surjectivite   :
(surjective (λ (x: ℝ) , x^2) )
:=
/- dEAduction
PrettyName
    La fonction f :  ℝ → ℝ, f(x) = x², est-elle surjective ?
OpenQuestion
	True
-/
begin
    todo
end

lemma exercise.injectivite  :
 (injective (λ (x: ℝ) , x^2) )
:=
/- dEAduction
PrettyName
    La fonction f :  ℝ → ℝ, f(x) = x², est-elle injective ?

OpenQuestion
	True
-/
begin
    todo
end



lemma exercise.bijectivite    :
 (bijective (λ (x: ℝ) , x^2) )
:=
/- dEAduction
PrettyName
    La fonction f :  ℝ → ℝ, f(x) = x², est-elle bijective ?
    
    On peut essayer les deux définitions équivalentes à disposition
    

OpenQuestion
	True
-/
begin
    todo
end



end proprietes_fonction_carree


end course


