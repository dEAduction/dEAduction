-- import data.set
import tactic
import data.real.basic



-- dEAduction imports
import structures2
-- import notations_definitions
-- import compute

-- General principles :
-- Type should be defined as parameters, in order to be implicit everywhere
-- other parameters are implicit in definitions, i.e. defined using '{}' (e.g. {A : set X} )
-- but explicit everywhere else, i.e. defined using '()' (e.g. (A : set X) )
-- each definition must be an iff statement (since it will be called with 'rw' or 'symp_rw')



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


open set


namespace Logique_et_nombres_reels
/- dEAduction
PrettyName
    Logique et nombres réels
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

lemma exercise.zero_ou_un_2 : not (∀ n:ℕ, (n = 0 or n = 1))
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


lemma exercise.vraiment_plus_petit : not (∃ m:ℤ, ∀ n:ℤ, m ≤ n)
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
not ( ∃ m:ℕ, ∀ n:ℕ, m=n )
:=
/- dEAduction
PrettyName
    Egaux à tous !
-/
begin
    sorry
end


lemma exercise.tres_petit :
not ( ∀ a ≥ (0:ℝ), ∀ ε ≥ (0:ℝ), (a ≤ ε → a = 0) )
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
not (∀x:ℤ, ∀y:ℤ, (x<y → (∃z:ℤ, x < z and z < y)))
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


end Logique_et_nombres_reels

end course