/-
This is a d∃∀duction file providing True or False questions about injection, surjection, bijection for concrete applications.
-/

-- Lean standard imports

import data.set
import data.real.basic
import init
import tactic

-- dEAduction tactics
import deaduction_all_tactics


-- Use classical logic
local attribute [instance] classical.prop_decidable


/- dEAduction
Title
    VRAI/FAUX : Injectivité, surjectivité, bijectivité
Author
    Isabelle Dubois 
Institution
    Université de Lorraine
Description
    Ce cours correspond à un cours standard de théorie "élémentaire" des ensembles. Partie Applications.
AvailableExercises
	NONE
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
PrettyName
    Définitions : Injectivité, surjectivité, bijectivité
-/

------------------------
-- COURSE DEFINITIONS --
------------------------


variables {f: X → Y} 



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



end definitions


namespace injectivite_surjectivite_bijectivite
/- dEAduction
PrettyName
    VRAI/FAUX : Injectivité, surjectivité, bijectivité d'une application
-/

open definitions


---------------
-- EXERCICES --
---------------




lemma exercise.inj_nplus1  :
injective (λ (n:ℕ) , n+1)
:=
/- dEAduction
Description
   La fonction f : ℕ → ℕ, f(n) = n+1, est-elle injective ?
PrettyName
    Injectivité de f(n) = n+1 - Entiers naturels
OpenQuestion
	True
-/
begin
    todo
end

lemma exercise.surj_nplus1  :
surjective (λ (n:ℕ) , n+1)
:=
/- dEAduction
Description
   La fonction f : ℕ → ℕ, f(n) = n+1, est-elle surjective ?
PrettyName
    Surjectivité de f(n) = n+1 - Entiers naturels
OpenQuestion
	True
-/
begin
    todo
end

lemma exercise.bij_nplus1 :
bijective (λ (n:ℕ) , n+1)
:=
/- dEAduction
Description
   La fonction f : ℕ → ℕ, f(x) = n+1, est-elle bijective ?
PrettyName
    Bijectivité de f(n) = n+1 - Entiers naturels
OpenQuestion
	True
-/
begin
    todo
end

lemma exercise.inj_kplus1  :
injective (λ (k :ℤ) , k+1)
:=
/- dEAduction
Description
   La fonction f : ℤ → ℤ, f(k) = k+1, est-elle injective ?
PrettyName
    Injectivité de f(k) = k+1 - Entiers relatifs
OpenQuestion
	True
-/
begin
    todo
end

lemma exercise.surj_kplus1  :
surjective (λ (k :ℤ) , k+1)
:=
/- dEAduction
Description
   La fonction f : ℤ → ℤ, f(k) = k+1, est-elle surjective ?
PrettyName
    Surjectivité de f(k) = k+1 - Entiers relatifs
OpenQuestion
	True
-/
begin
    todo
end

lemma exercise.bij_kplus1 :
bijective (λ (k :ℤ) , k+1)
:=
/- dEAduction
Description
   La fonction f : ℤ → ℤ, f(k) = k+1, est-elle bijective ?
PrettyName
    Bijectivité de f(k) = k+1 - Entiers relatifs
OpenQuestion
	True
-/
begin
    todo
end

lemma exercise.inj_2k  :
injective (λ (k :ℤ) , 2*k +3)
:=
/- dEAduction
Description
   La fonction f : ℤ → ℤ, f(k) = 2*k+3, est-elle injective ?
PrettyName
    Injectivité de f(k) = 2*k +3 - Entiers relatifs
OpenQuestion
	True
-/
begin
    todo
end

lemma exercise.surj_2k  :
surjective (λ (k :ℤ) , 2*k +3 )
:=
/- dEAduction
Description
   La fonction f : ℤ → ℤ, f(k) = 2*k +3 , est-elle surjective ?
PrettyName
    Surjectivité de f(k) = 2*k+3 - Entiers relatifs
OpenQuestion
	True
-/
begin
    todo
end

lemma exercise.bij_2k :
bijective (λ (k :ℤ) , 2*k +3 )
:=
/- dEAduction
Description
   La fonction f : ℤ → ℤ, f(k) = 2*k +3, est-elle bijective ?
PrettyName
    Bijectivité de f(k) = 2*k+3 - Entiers relatifs
OpenQuestion
	True
-/
begin
    todo
end

lemma exercise.inj_pol  :
injective (λ (x : ℝ ) , 2*x^2 +3)
:=
/- dEAduction
Description
   La fonction f : ℝ  → ℝ , f(x) = 2*x^2 +3, est-elle injective ?
PrettyName
    Injectivité de  f(x) = 2*x^2 +3 - Réels
OpenQuestion
	True
-/
begin
    todo
end

lemma exercise.surj_pol  :
surjective (λ (x : ℝ ) , 2*x^2 +3)
:=
/- dEAduction
Description
   La fonction f : ℝ  → ℝ , f(x) = 2*x^2 +3, est-elle surjective ?
PrettyName
    Surjectivité de  f(x) = 2*x^2 +3 - Réels
OpenQuestion
	True
-/
begin
    todo
end

lemma exercise.bij_pol  :
bijective (λ (x : ℝ ) , 2*x^2 +3)
:=
/- dEAduction
Description
   La fonction f : ℝ  → ℝ , f(x) = 2*x^2 +3, est-elle bijective ?
PrettyName
    Bijectivité de  f(x) = 2*x^2 +3 - Réels
OpenQuestion
	True
-/
begin
    todo
end


end injectivite_surjectivite_bijectivite


end course
