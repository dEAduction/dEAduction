-- import data.set
import tactic
import data.real.basic



-- dEAduction imports
import structures2
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


namespace Inegalites
/- dEAduction
PrettyName
    Logique et nombres réels
-/

lemma exercise.inegalite_1 (a:ℝ) (H1: 0 ≠ a) (H2 : 0 ≤ a) : 0 < a
:=
begin
    sorry
end

lemma exercise.inegalite_2 (a:ℝ) (H1: 0 ≠ a) (H2 : 0 ≤ a) : a > 0
:=
begin
    sorry
end

lemma exercise.inegalite_3 (a:ℝ) (H1: 0 ≠ a) (H2 : a ≥ 0) : 0 < a
:=
begin
    sorry
end

lemma exercise.inegalite_4 (a:ℝ) (H1: 0 ≠ a) (H2 : a ≥ 0) : a > 0
:=
begin
    sorry
end



lemma exercise.inegalite_1b (a:ℝ) (H1: a ≠ 0) (H2 : 0 ≤ a) : 0 < a
:=
begin
    sorry
end

lemma exercise.inegalite_2b (a:ℝ) (H1: a ≠ 0) (H2 : 0 ≤ a) : a > 0
:=
begin
    sorry
end

lemma exercise.inegalite_3b (a:ℝ) (H1: a ≠ 0) (H2 : a ≥ 0) : 0 < a
:=
begin
    sorry
end

lemma exercise.inegalite_4b (a:ℝ) (H1: a ≠ 0) (H2 : a ≥ 0) : a > 0
:=
begin
    sorry
end



lemma exercise.inegalite_div (a b :ℝ) (H1: a ≠ 0) (H2 : a ≥ 0)
(H3 : b >0) :
a/32 > 0
and a/32 ≥ 0
and 0.12 * a > 0
and a*b > 0
and a/b > 0
and a/b ≥ 0
:=
begin
    sorry
end


lemma exercise.inegalite_div2 (a b :ℝ) (H1: a > 0)
(H3 : b >0) :
a/32 > 0
and a/32 ≥ 0
and 0.12 * a > 0
and a*b > 0
and a/b > 0
and a/b ≥ 0
:=
begin
    sorry
end












end Inegalites

end course