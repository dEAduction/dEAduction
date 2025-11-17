/-
This is a d∃∀duction file providing True or False questions about injection, surjection, bijection for concrete applications.
-/

-- Lean standard imports

import data.set
import data.real.basic
import init
import tactic
import compute

-- dEAduction tactics
-- structures2 and utils are vital
import structures2      -- hypo_analysis, targets_analysis
import utils            -- no_meta_vars
import user_notations   -- notations that can be used in deaduction UI for a new object
import push_neg_once
import induction

-- dEAduction definitions
import set_definitions


-- Use classical logic
local attribute [instance] classical.prop_decidable


/- dEAduction
title = "Théorie des ensembles : applications - VRAI/FAUX sur les notions d'injectivité, surjectivité, bijectivité"
author = "Isabelle Dubois"
institution = "Université de Lorraine"
description = 'Ce cours correspond à un cours standard de théorie "élémentaire" des ensembles. Partie Applications.'
available_exercises = "NONE"
[settings]
logic.usr_jokers_available = false
logic.use_color_for_applied_properties = false
functionality.allow_induction = false
functionality.calculator_available = true
others.Lean_request_method = "normal"
-/


---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course
parameters {X Y Z: Type}
parameters {n p  m : ℕ}
parameters {k l  : int }

open set
open nat


namespace definitions
/- dEAduction
pretty_name = "Définitions : Injectivité, surjectivité, bijectivité"
-/

------------------------
-- COURSE DEFINITIONS --
------------------------


variables {f: X → Y} 



lemma definition.injectivite :
injective f ↔ ∀ x y : X, (f x = f y → x = y)
:=
/- dEAduction
pretty_name = "Application injective"
implicit_use = true
-/
begin
    refl,
end

lemma definition.surjectivite :
surjective f ↔ ∀ y : Y, ∃ x : X, y = f x
:=
/- dEAduction
pretty_name = "Application surjective"
implicit_use = true
-/
begin
    refl,
end




lemma definition.bijectivite_1 :
bijective f ↔ (injective f ∧ surjective f)
:=
/- dEAduction
pretty_name = "Application bijective (première définition)"
-/
begin
    todo
end

lemma definition.existe_un_unique
(P : X → Prop) :
(∃! (λx,  P x)) ↔  (∃ x : X, (P x ∧ (∀ x' : X, P x' → x' = x)))
:=
/- dEAduction
pretty_name = "∃! : existence et unicité"
-/
begin
    todo
end

lemma definition.bijectivite_2 :
bijective f ↔ ∀ y : Y, exists_unique (λ x, y = f x)
:=
/- dEAduction
pretty_name = "Application bijective (seconde définition)"
-/
begin
    refl,
end



end definitions


namespace injectivite_surjectivite_bijectivite
/- dEAduction
pretty_name = "VRAI/FAUX : Injectivité, surjectivité, bijectivité d'une application"
-/

open definitions


---------------
-- EXERCICES --
---------------




lemma exercise.inj_nplus1  :
injective (λ (n:ℕ) , n+1)
:=
/- dEAduction
description = "La fonction f : ℕ → ℕ, f(n) = n+1, est-elle injective ?"
pretty_name = "Injectivité de f(n) = n+1 - Entiers naturels"
open_question = true
-/
begin
    todo
end

lemma exercise.surj_nplus1  :
surjective (λ (n:ℕ) , n+1)
:=
/- dEAduction
description = "La fonction f : ℕ → ℕ, f(n) = n+1, est-elle surjective ?"
pretty_name = "Surjectivité de f(n) = n+1 - Entiers naturels"
open_question = true
-/
begin
    todo
end

lemma exercise.bij_nplus1 :
bijective (λ (n:ℕ) , n+1)
:=
/- dEAduction
description = "La fonction f : ℕ → ℕ, f(x) = n+1, est-elle bijective ?"
pretty_name = "Bijectivité de f(n) = n+1 - Entiers naturels"
open_question = true
-/
begin
    todo
end

lemma exercise.inj_kplus1  :
injective (λ (k :ℤ) , k+1)
:=
/- dEAduction
description = "La fonction f : ℤ → ℤ, f(k) = k+1, est-elle injective ?"
pretty_name = "Injectivité de f(k) = k+1 - Entiers relatifs"
open_question = true
-/
begin
    todo
end

lemma exercise.surj_kplus1  :
surjective (λ (k :ℤ) , k+1)
:=
/- dEAduction
description = "La fonction f : ℤ → ℤ, f(k) = k+1, est-elle surjective ?"
pretty_name = "Surjectivité de f(k) = k+1 - Entiers relatifs"
open_question = true
-/
begin
    todo
end

lemma exercise.bij_kplus1 :
bijective (λ (k :ℤ) , k+1)
:=
/- dEAduction
description = "La fonction f : ℤ → ℤ, f(k) = k+1, est-elle bijective ?"
pretty_name = "Bijectivité de f(k) = k+1 - Entiers relatifs"
open_question = true
-/
begin
    todo
end

lemma exercise.inj_2k  :
injective (λ (k :ℤ) , 2*k +3)
:=
/- dEAduction
description = "La fonction f : ℤ → ℤ, f(k) = 2*k+3, est-elle injective ?"
pretty_name = "Injectivité de f(k) = 2*k +3 - Entiers relatifs"
open_question = true
-/
begin
    todo
end

lemma exercise.surj_2k  :
surjective (λ (k :ℤ) , 2*k +3 )
:=
/- dEAduction
description = "La fonction f : ℤ → ℤ, f(k) = 2*k +3 , est-elle surjective ?"
pretty_name = "Surjectivité de f(k) = 2*k+3 - Entiers relatifs"
open_question = true
-/
begin
    todo
end

lemma exercise.bij_2k :
bijective (λ (k :ℤ) , 2*k +3 )
:=
/- dEAduction
description = "La fonction f : ℤ → ℤ, f(k) = 2*k +3, est-elle bijective ?"
pretty_name = "Bijectivité de f(k) = 2*k+3 - Entiers relatifs"
open_question = true
-/
begin
    todo
end

lemma exercise.inj_pol  :
injective (λ (x : ℝ ) , 2*x^2 +3)
:=
/- dEAduction
description = "La fonction f : ℝ  → ℝ , f(x) = 2*x^2 +3, est-elle injective ?"
pretty_name = "Injectivité de  f(x) = 2*x^2 +3 - Réels"
open_question = true
-/
begin
    todo
end

lemma exercise.surj_pol  :
surjective (λ (x : ℝ ) , 2*x^2 +3)
:=
/- dEAduction
description = "La fonction f : ℝ  → ℝ , f(x) = 2*x^2 +3, est-elle surjective ?"
pretty_name = "Surjectivité de  f(x) = 2*x^2 +3 - Réels"
open_question = true
-/
begin
    todo
end

lemma exercise.bij_pol  :
bijective (λ (x : ℝ ) , 2*x^2 +3)
:=
/- dEAduction
description = "La fonction f : ℝ  → ℝ , f(x) = 2*x^2 +3, est-elle bijective ?"
pretty_name = "Bijectivité de  f(x) = 2*x^2 +3 - Réels"
open_question = true
-/
begin
    todo
end


end injectivite_surjectivite_bijectivite


end course