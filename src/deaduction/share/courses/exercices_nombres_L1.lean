/-
This is a d∃∀duction file providing first exercises about quantifiers and numbers.
French version.
-/

import data.set
import data.real.basic
import tactic

-- dEAduction tactics
import structures2      -- hypo_analysis, targets_analysis
import utils            -- no_meta_vars
import user_notations   -- notations that can be used in deaduction UI for a new object
import compute          -- tactics for computation, used by the Goal! button

-- dEAduction definitions
-- import set_definitions


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
Description
    Ce fichier contient quelques exercices de base
    impliquant des quantificateurs et des inégalités.
    Certains buts sont vrais et d'autres faux :
    avant de commencer l'exercice,
    vous choisirez ce que vous voulez prouver,
    le but ou sa négation.
OpenQuestion
    True
AvailableExercises
    NONE
AvailableLogic
    ALL -not
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
    todo
end

lemma exercise.zero_ou_un_2 : ∀ n:ℕ, (n = 0 or n = 1)
:=
/- dEAduction
PrettyName
    Zéro ou un ou ?...
-/
begin
    todo
end


lemma exercise.plus_petit : ∃ m:ℕ, ∀ n:ℕ, m ≤ n
:=
/- dEAduction
PrettyName
    Plus petit que tous
-/
begin
    todo
end


lemma exercise.vraiment_plus_petit : ∃ m:ℤ, ∀ n:ℤ, m ≤ n
:=
/- dEAduction
PrettyName
    Plus petit que tous...
-/
begin
    todo
end


lemma exercise.egalite : ∀ n:ℕ, ∃ m:ℕ, m=n
:=
/- dEAduction
PrettyName
    Tous égaux
-/
begin
    todo
end


lemma exercise.egalite_2 :
∃ m:ℕ, ∀ n:ℕ, m=n
:=
/- dEAduction
PrettyName
    Egaux à tous !
-/
begin
    todo
end


lemma exercise.tres_petit :
∀ a ≥ (0:ℝ), ∀ ε ≥ (0:ℝ), (a ≤ ε → a = 0)
:=
/- dEAduction
PrettyName
    Très petit
-/
begin
    todo
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
    todo
end



lemma exercise.tres_petit_3 :
∀ a ≥ (0:ℝ), ((∀ ε > (0:ℝ), a ≤ ε) → a = 0)
:=
/- dEAduction
PrettyName
    Trop compliqué !
-/
begin
    todo
end


lemma exercise.entre_deux_entiers :
∀x:ℤ, ∀y:ℤ, (x<y → (∃z:ℤ, x < z and z < y))
:=
/- dEAduction
PrettyName
    Entre deux entiers
-/
begin
    todo
end


lemma exercise.entre_deux_reels :
∀x:ℝ, ∀y:ℝ, (x<y → (∃z:ℝ, x < z and z < y))
:=
/- dEAduction
PrettyName
    Entre deux réels
-/
begin
    todo
end

end exercices

end Logique_et_nombres_reels

end course