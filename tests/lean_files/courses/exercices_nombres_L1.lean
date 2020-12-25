-- import data.set
import tactic
import data.real.basic



-- dEAduction imports
import structures2
import compute

-- General principles :
-- Type should be defined as parameters, in order to be implicit everywhere
-- other parameters are implicit in definitions, i.e. defined using '{}' (e.g. {A : set X} )
-- but explicit everywhere else, i.e. defined using '()' (e.g. (A : set X) )
-- each definition must be an iff statement (since it will be called with 'rw' or 'symp_rw')



---------------------
-- Course metadata --
---------------------
-- logic names ['and', 'or', 'negate', 'implicate', 'iff', 'forall', 'exists']
-- proofs names ['use_proof_methods', 'new_object', 'apply', 'assumption']
-- magic names ['compute']
-- proof methods names ['cbr', 'contrapose', 'absurdum', 'sorry']
-- Note for Python devs:
--      Any supplementary metadata will be put in the 'info' dict of each exo

/- dEAduction
Author
    Frédéric Le Roux
Institution
    Université de France
Title
    Logique et inégalités
OpenQuestion
    True
AvailableExercises
    NONE
AvailableLogic
    ALL -negate
-/

-- If OpenQuestion is True, DEAduction will ask the user if she wants to
-- prove the statement or its negation, and set the variable
-- NegateStatement accordingly
-- If NegateStatement is True, then the statement will be replaced by its
-- negation
-- AvailableExercises is set to None so that no exercise statement can be applied
-- by the user. Recommended with OpenQuestions set to True!








local attribute [instance] classical.prop_decidable

---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course

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


namespace Logique_et_nombres_reels
/- dEAduction
PrettyName
    Logique et nombres réels
-/

namespace negation
/- dEAduction
PrettyName
    Enoncés de négation
-/

lemma theorem.negation_et {P Q : Prop} :
( not (P and Q) ) ↔ ( (not P) or (not Q) )
:=
/- dEAduction
PrettyName
    Négation du 'et'
-/
begin
    exact not_and_distrib
end

lemma theorem.negation_ou {P Q : Prop} :
( not (P or Q) ) ↔ ( (not P) and (not Q) )
:=
/- dEAduction
PrettyName
    Négation du 'ou'
-/
begin
    exact not_or_distrib
end

lemma theorem.negation_non {P : Prop} :
( not not P ) ↔  P
:=
/- dEAduction
PrettyName
    Négation du 'non'
-/
begin
    exact not_not
end


lemma theorem.negation_implique {P Q : Prop} :
( not (P → Q) ) ↔  ( P and (not Q) )
:=
/- dEAduction
PrettyName
    Négation d'une implication
-/
begin
    exact not_imp,
end


lemma theorem.negation_existe  {X : Sort*} {P : X → Prop} :
( ( not ∃ (x:X), P x  ) ↔ ∀ x:X, not P x )
:=
/- dEAduction
PrettyName
    Négation de '∃X, P(x)'
-/
begin
    exact not_exists,
end



lemma theorem.negation_pour_tout {X : Sort*} {P : X → Prop} :
( not (∀x, P x ) ) ↔ ∃x, not P x
:=
/- dEAduction
PrettyName
    Négation de '∀x, P(x)'
-/
begin
    exact not_forall
end


lemma theorem.negation_inegalite_stricte {X : Type} (x y : X) [linear_order X]:
( not (x < y) ) ↔ y ≤ x
:=
/- dEAduction
PrettyName
    Négation de 'x < y'
-/
begin
    exact not_lt
end


lemma theorem.negation_inegalite_large {X : Type} (x y : X) [linear_order X]:
( not (x ≤ y) ) ↔ y < x
:=
/- dEAduction
PrettyName
    Négation de 'x ≤ y'
-/
begin
    exact not_le
end




end negation

namespace exercices
/- dEAduction
PrettyName
    Exercices
-/



lemma exercise.zero_ou_un : ∀ n:ℕ, (n ≠ 0 or n ≠ 1)
:=
/- dEAduction
PrettyName
    Pas zéro ou pas un
-/
begin
    sorry
end

lemma exercise.zero_ou_un_2 : ∀ n:ℕ, (n = 0 or n = 1)
:=
/- dEAduction
PrettyName
    Zéro ou un ou ?...
-/
begin
    sorry
end


lemma exercise.plus_petit : ∃ m:ℕ, ∀ n:ℕ, m ≤ n
:=
/- dEAduction
PrettyName
    Plus petit que tous
-/
begin
    sorry
end


lemma exercise.vraiment_plus_petit : ∃ m:ℤ,
∀ n:ℤ,
m ≤ n
:=
/- dEAduction
PrettyName
    Plus petit que tous...
-/
begin
    sorry
end


lemma exercise.egalite : ∀ n:ℕ, ∃ m:ℕ, m=n
:=
/- dEAduction
PrettyName
    Tous égaux
-/
begin
    sorry
end


lemma exercise.egalite_2 :
∃ m:ℕ, ∀ n:ℕ, m=n
:=
/- dEAduction
PrettyName
    Egaux à tous !
-/
begin
    sorry
end


lemma exercise.tres_petit :
∀ a ≥ (0:ℝ), ∀ ε ≥ (0:ℝ), (a ≤ ε → a = 0)
:=
/- dEAduction
PrettyName
    Très petit
-/
begin
    sorry
end


lemma exercise.tres_petit_2 :
∀ a ≥ (0:ℝ), ((∀ ε ≥ (0:ℝ), a ≤ ε) → a = 0)
:=
/- dEAduction
PrettyName
    Ca se complique
SimplificationCompute
    $ALL
-/
begin
    sorry
end



lemma exercise.tres_petit_3 :
∀ a ≥ (0:ℝ), ((∀ ε > (0:ℝ), a ≤ ε) → a = 0)
:=
/- dEAduction
PrettyName
    Trop compliqué !
-/
begin
    sorry
end


lemma exercise.entre_deux_entiers :
∀x:ℤ, ∀y:ℤ, (x<y → (∃z:ℤ, x < z and z < y))
:=
/- dEAduction
PrettyName
    Entre deux entiers
-/
begin
    sorry
end


lemma exercise.entre_deux_reels :
∀x:ℝ, ∀y:ℝ, (x<y → (∃z:ℝ, x < z and z < y))
:=
/- dEAduction
PrettyName
    Entre deux réels
-/
begin
    sorry
end

end exercices

end Logique_et_nombres_reels

end course