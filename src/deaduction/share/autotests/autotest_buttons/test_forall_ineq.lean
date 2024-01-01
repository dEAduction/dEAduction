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
PrettyName
  Limite d'une suite
ImplicitUse
  True
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
AutoTest
    iff 0 success=Equivalence_séparée_en_deux_implications,
    implies success=Propriété_H1_ajoutée_au_contexte,
    forall success=Objet_ε_ajouté_au_contexte,
    @P1 definition.limit success=Définition_appliquée_à_H1,
    @O3 @P1 forall success=Propriété_H3_ajoutée_au_contexte,
    @P3 exists success=Nouvel_objet_n_vérifiant_la_propriété_H4,
    @O4 exists success=Il_reste_à_démontrer_que_n_convient,
    forall success=Objet_n'_ajouté_au_contexte,
    @O5 @P3 forall success=Propriété_H6_ajoutée_au_contexte,
    assumption success=But_en_cours_atteint,
    implies success=Propriété_H7_ajoutée_au_contexte,
    forall success=Objet_ε_ajouté_au_contexte,
    @P1 forall [ ε/2 ] success=Propriété_H10_ajoutée_au_contexte,
    @P4 exists success=Nouvel_objet_n_vérifiant_la_propriété_H11,
    @O4 exists success=Il_reste_à_démontrer_que_n_convient,
    forall success=Objet_n'_ajouté_au_contexte,
    @O5 @P4 forall success=Propriété_H13_ajoutée_au_contexte,
    assumption success=La_preuve_est_terminée_!
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