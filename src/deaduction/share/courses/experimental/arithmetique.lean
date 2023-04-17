/-
This is a d∃∀duction file providing exercises for sets and maps. French version.
-/

import data.set
import tactic
import data.nat.basic

-- dEAduction tactics
import structures2      -- hypo_analysis, targets_analysis
import utils            -- no_meta_vars
import user_notations   -- notations that can be used in deaduction UI for a new object
import push_neg_once    -- pushing negation just one step
import compute

-- dEAduction definitions
import set_definitions

-------------------------
-- dEAduction METADATA --
-------------------------
/- dEAduction
Title
    Arithmétique
Author
    Frédéric Le Roux, Thomas Richard
Institution
    Université du monde
Description
    Premier essai d'arithmétique
Display
    divise --> (-2, " DIVISE ", -1)
    delta --> (-2, "∆", -1)
-/

local attribute [instance] classical.prop_decidable
---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------

section course

open nat
universe u

theorem two_step_induction {P : ℕ → Sort u} (H1 : P 0) (H2 : P 1)
    (H3 : ∀ (n : ℕ) (IH1 : P n) (IH2 : P (succ n)), P (succ (succ n))) : Π (a : ℕ), P a
| 0               := H1
| 1               := H2
| (succ (succ n)) := H3 _ (two_step_induction _) (two_step_induction _)

open set

------------------
-- COURSE TITLE --
------------------
namespace definitions
/- dEAduction
PrettyName
    Définitions
-/


def pair (a: ℤ) := ∃ b, a = 2*b 

def divise (a b:ℤ) := ∃ c, b = a * c

 


lemma definition.pair {a:ℤ} : (pair a) ↔ ∃ b, a = 2*b :=
/- dEAduction
ImplicitUse
  True
-/
begin
  refl
end

lemma definition.divise {a b : ℤ} : (divise a b) ↔ (∃ c, b = a * c) :=
/- dEAduction
ImplicitUse
  True
-/
begin
  refl
end

lemma exercise.mul_divise {a b c : ℤ} : divise a b → divise a (b*c) :=
begin
  todo
  -- intro H2,
  -- cases H2 with k,
  -- use (k*c),
  -- rw H2_h,
  -- cc, -- ring
end

lemma exercise.divisent_egal {a b : ℤ} :
(divise a b and divise b a) → (a = b or a = -b) :=
begin
  rintro ⟨H1 , H2⟩,
  cases H1 with d H1,
  cases H2 with d' H2,
  rw H1 at H2,
  by_cases a=0, rotate,
  have H2b : (d * d' =1),
  
end




end definitions

end course



