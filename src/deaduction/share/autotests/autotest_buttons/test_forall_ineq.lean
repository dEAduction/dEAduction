/-
This is a d∃∀duction file providing exercises about limits and continuity.
-/

-- Lean standard imports
import tactic
import data.real.basic

-- dEAduction tactics
-- structures2 and utils are vital
import deaduction_all_tactics
-- import structures2      -- hypo_analysis, targets_analysis
-- import utils            -- no_meta_vars
-- import compute_all      -- Tactics for the compute buttons
-- import push_neg_once    -- Pushing negation just one step
-- import induction        -- Induction theorems

-- dEAduction definitions
import set_definitions
import real_definitions

-- Use classical logic
local attribute [instance] classical.prop_decidable

definition limit (u : ℕ → ℝ) (l : ℝ) : Prop :=
∀ ε > 0, ∃ N, ∀ n ≥ N, | u n - l | < ε

section definitions

lemma definition.limit 
{u : ℕ → ℝ} {l : ℝ} :
(limit u l) ↔ 
∀ ε > 0, ∃ N, ∀ n ≥ N, | u n - l | < ε
:= 
/- dEAduction
pretty_name = "Limite d'une suite"
implicit_use = true
-/
begin
  -- hypo_analysis,
  refl
end


end definitions

section course 

lemma exercise.test_but_compute
(u v l l' e: ℝ)
(H: |u + v - (l+l') | < e/2 + e/2):
|(u-l) + (v-l')| < e
:=
begin
  todo
end

lemma exercise.test_triangular
(u v l l' e: ℝ) 
(H: |u - l| +|v -l'| < e):
|(u-l) + (v-l')| < e
:=
begin
  todo
end



lemma exercise.test_for_all_ineq
(u : ℕ → ℝ) (l : ℝ) :
(limit u l) ↔ 
∀ ε > 0, ∃ N, ∀ n ≥ N, | u n - l | ≤ ε
:=
/- dEAduction
[[auto_test]]
button = "iff"
user_input = [
    0,
]
success_msg = "Equivalence séparée en deux implications"
[[auto_test]]
button = "implies"
success_msg = "Propriété H1 ajoutée au contexte"
[[auto_test]]
button = "forall"
success_msg = "Objet ε ajouté au contexte"
[[auto_test]]
selection = [ "@P1" ]
statement = "definition.limit"
success_msg = "Définition appliquée à H1"
[[auto_test]]
selection = [ "@O3", "@P1" ]
button = "use_forall"
success_msg = "Propriété H3 ajoutée au contexte"
[[auto_test]]
selection = [ "@P3" ]
button = "use_exists"
success_msg = "Nouvel objet n vérifiant la propriété H4"
[[auto_test]]
selection = [ "@O4" ]
button = "prove_exists"
success_msg = "Il reste à démontrer que n convient"
[[auto_test]]
button = "forall"
success_msg = "Objet n' ajouté au contexte"
[[auto_test]]
selection = [ "@O5", "@P3" ]
button = "forall"
success_msg = "Propriété H6 ajoutée au contexte"
[[auto_test]]
button = "assumption"
success_msg = "But en cours atteint"
[[auto_test]]
button = "implies"
success_msg = "Propriété H7 ajoutée au contexte"
[[auto_test]]
button = "forall"
success_msg = "Objet ε ajouté au contexte"
[[auto_test]]
selection = [ "@P1" ]
button = "forall"
user_input = [
    [
        "ε/2",
    ],
]
success_msg = "Propriété H10 ajoutée au contexte"
[[auto_test]]
selection = [ "@P4" ]
button = "use_exists"
success_msg = "Nouvel objet n vérifiant la propriété H11"
[[auto_test]]
selection = [ "@O4" ]
button = "prove_exists"
success_msg = "Il reste à démontrer que n convient"
[[auto_test]]
button = "forall"
success_msg = "Objet n' ajouté au contexte"
[[auto_test]]
selection = [ "@O5", "@P4" ]
button = "forall"
success_msg = "Propriété H13 ajoutée au contexte"
[[auto_test]]
button = "assumption"
success_msg = "La preuve est terminée !"
-/
begin
  split,
  intro H1,
  intro ε, intro H2,
  rw limit at H1,
  have H3 := H1 ε H2,
  cases H3 with n H4,
  use n,
  intro n', intro H5,
  have H6 := H4 n' H5,
  -- solve1 {linarith},
  todo,
  todo,
end



end course