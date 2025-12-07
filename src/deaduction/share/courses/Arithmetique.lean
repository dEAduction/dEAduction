/-
This is a d∃∀duction file providing exercises for sets and maps. French version.
-/

-- Standard Lean import
import data.set
import tactic
import data.nat.basic

-- dEAduction tactics
import deaduction_all_tactics

-- dEAduction definitions
import set_definitions

-- Use classical logic
local attribute [instance] classical.prop_decidable

-------------------------
-- dEAduction METADATA --
-------------------------
/- dEAduction
title = "Arithmétique"
author = "Frédéric Le Roux"
institution = "Université du monde"
description = "Premier essai d'arithmétique"
[settings]
logic.usr_jokers_available = false
logic.use_color_for_applied_properties = false
functionality.allow_induction = true
functionality.calculator_available = true
others.Lean_request_method = "normal"
-/


-- Old:
-- [display]
-- prime = [-1, " est premier"]
-- puissancede2 = [-1, " est une puissance de 2"]
-- multiple = [-2, " est multiple de ", -1]

---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------


open nat
-- universe u

-- theorem two_step_induction {P : ℕ → Sort u} (H1 : P 0) (H2 : P 1)
--     (H3 : ∀ (n : ℕ) (IH1 : P n) (IH2 : P (succ n)), P (succ (succ n))) : Π (a : ℕ), P a
-- | 0               := H1
-- | 1               := H2
-- | (succ (succ n)) := H3 _ (two_step_induction _) (two_step_induction _)

open set

-- -----------------
-- namespace logique

-- lemma definition.iff {P Q : Prop} : (P ↔ Q) ↔ ((P → Q) ∧ (Q → P)) :=
-- /- dEAduction
-- PrettyName
--     Equivalence logique
-- -/
-- begin
--   exact iff_def,
-- end

-- lemma theorem.disjonction_eqv_implication (P Q: Prop) :
-- (P ∨ Q) ↔ ((not P) → Q)
-- := 
-- /- dEAduction
-- PrettyName
--     Disjonction sous forme d'implication
-- -/
-- begin
--   tautology,
-- end

-- lemma theorem.induction {P: nat → Prop} (H0: P 0)
-- (H1: ∀ (n : ℕ) (IH1 : P n), P (n+1) ) :
-- ∀n, P n
-- :=
-- begin
--   todo
-- end 

-- end logique

---------------------
namespace definitions
/- dEAduction
pretty_name = "Définitions"
-/

variables {IntegerSubGroup:Type} [has_add IntegerSubGroup] 
[has_one IntegerSubGroup] [has_mul IntegerSubGroup] 

-- def even (a: ℤ) := ∃ b, a = 2*b 

def even (a: IntegerSubGroup) := ∃ (b: IntegerSubGroup), a = 2*b 

def odd (a: IntegerSubGroup) := ∃ (b: IntegerSubGroup), a = 2*b + 1 

def divides (a b: IntegerSubGroup) := ∃ c, b = a * c

def multiple (a b: IntegerSubGroup) := ∃ c, a = b * c

-- lemma auxiliary_theorem.nat_even {a:ℕ} : (even a) ↔ ∃ b, a = 2*b :=
-- begin
--   todo
-- end
-- AuxiliaryDefinitions
--   auxiliary_theorem.nat_even

lemma definition.even {a: IntegerSubGroup} : (even a) ↔ ∃ (b: IntegerSubGroup), a = 2*b :=
/- dEAduction
pretty_name = "Pair"
implicit_use = true
-/
begin
  refl
end

-- lemma auxiliary_theorem.nat_odd {a: IntegerSubGroup} : (odd a) ↔ ∃ b, a = 2*b + 1:=
-- begin
--   todo
-- end

lemma definition.odd {a: IntegerSubGroup} : (odd a) ↔ ∃ (b: IntegerSubGroup), a = 2*b + 1 :=
/- dEAduction
pretty_name = "Impair"
implicit_use = true
auxiliary_definitions = "auxiliary_theorem.nat_odd"
-/
begin
  refl
end


-- NB: the following is obviously false for general type u...
axiom AX: IntegerSubGroup = ℕ ∨ IntegerSubGroup = ℤ
lemma theorem.not_even_is_odd {a: IntegerSubGroup} :
(not (even a)) ↔ odd a :=
/- dEAduction
pretty_name = "Pair et impair"
auxiliary_definitions = "auxiliary_theorem.nat_not_even_is_odd"
-/
begin
  todo
end


lemma theorem.signe_parite_pair  :
∀ n:ℕ, ((even n) → ((-1:ℤ)^n = 1 ))
:= 
/- dEAduction
pretty_name = "(-1) puissance pair"
-/
begin
   todo
end

lemma theorem.signe_parite_impair  :
∀ n:ℕ, ((odd n) → ((-1:ℤ)^n = -1 ))
:= 
/- dEAduction
pretty_name = "(-1) puissance impair"
-/
begin
   todo
end


lemma definition.divides {a b : IntegerSubGroup} : (divides a b) ↔ (∃ c: IntegerSubGroup, b = a * c) :=
/- dEAduction
pretty_name = "Divise"
implicit_use = true
-/
begin
  refl
end

lemma definition.multiple {a b : IntegerSubGroup} : (multiple a b) ↔ (∃ c, a = b * c) :=
/- dEAduction
pretty_name = "Multiple"
implicit_use = true
-/
begin
  refl
end

def puissancede2 (a :ℕ) := ∃ b : ℕ, a = 2^b

lemma definition.puissancede2 {a:ℕ} : (puissancede2 a) ↔ ∃ b:ℕ, a = 2^b :=
/- dEAduction
pretty_name = "Puissance de 2"
implicit_use = true
-/
begin
  refl
end


-- Nb premier
lemma definition.prime {p: ℕ} : (prime p) ↔ (p≥ 2 ∧ (∀ n:ℕ, divides n p → (n=1 or n=p))) :=
/- dEAduction
pretty_name = "Nombre premier"
-/
begin
  todo
end


end definitions

open definitions

/- PLAN

I - construction des symboles logiques

  - ∃ 
  - →
  - ∀
  - ↔  
  - ∧
  - ∨

II - Utilisation des symboles
  - ∧
  - ∃
  - → 
  - ∀

II - Types de preuves
  - Par cas ; utilisation du ∨ ; wlog
  - Contraposée
  - Absurde
-/

--------------------------------
namespace preuve_d_existence
/- dEAduction
pretty_name = "Preuves d'existence"
-/

lemma exercise.quatorze : even (14:ℤ) :=
/- dEAduction
pretty_name = "Quatorze est pair"
-/
begin
  todo
end

lemma exercise.existe_pair : ∃(a:ℤ), (even a) :=
/- dEAduction
pretty_name = "Il existe un entier pair"
-/
begin
  todo
end

lemma exercise.existe_impair : ∃(a:ℤ), (odd a) :=
/- dEAduction
pretty_name = "Il existe un entier impair"
-/
begin
  todo
end

lemma exercise.divise : divides 7 42 :=
/- dEAduction
pretty_name = "Sept divise quarante-deux."
-/
begin
  todo
end

lemma exercise.nombre_8  :
(even 8) ∧ (puissancede2 8)
 :=
/- dEAduction
pretty_name = "8 est pair et une puissance de 2"
-/
begin
  todo
end

end preuve_d_existence



--------------------------------
namespace implications

lemma exercise.carre_pair1 (n: ℤ) :
(even n) → (even (n^2)) :=
/- dEAduction
pretty_name = "Carré d'un nombre pair"
description = "Le carré d'un nombre pair est pair"
-/
begin
  todo
end

variables {IntegerSubGroup:Type} [has_add IntegerSubGroup] 
[has_one IntegerSubGroup] [has_mul IntegerSubGroup] 

lemma exercise.divise_transitive (a b c : IntegerSubGroup) :
(divides a b) ∧ (divides b c) → (divides a c) :=
/- dEAduction
pretty_name = "La divisibilité est transitive"
-/
begin
  todo
end

lemma exercise.produit_impairs (n m:ℤ) :
(odd n ∧ odd m) → odd (n*m) :=
/- dEAduction
pretty_name = "Impair fois impair"
-/
begin
  todo
end

end implications


--------------------------------
namespace preuves_universelles
/- dEAduction
pretty_name = "Enoncés universels"
-/

lemma exercise.carre_pair1 :
∀{n:ℤ}, (even n) → (even (n^2)) :=
/- dEAduction
pretty_name = "Carré d'un nombre pair"
description = "Le carré d'un nombre pair est pair"
-/
begin
  todo
end

lemma exercise.mul_divides  : ∀ {a b c : ℤ}, divides a b → divides a (b*c) :=
/- dEAduction
pretty_name = "Diviseurs d'un multiple"
-/
begin
  todo
  -- intro H2,
  -- cases H2 with k,
  -- use (k*c),
  -- rw H2_h,
  -- cc, -- ring
end

end preuves_universelles

-----------------------------
namespace equivalence_logique_1
/- dEAduction
pretty_name = "Equivalence logique I"
-/

lemma exercise.difference_carres {n : ℤ} : (odd n) ↔ (∃m, n=(m+1)^2 - m^2) :=
/- dEAduction
pretty_name = "Différence de deux carrés consécutifs"
description = """
Un nombre peut s'écrire comme une différence de deux carrés consécutifs
si et seulement si il est impair.
"""
-/
begin
  todo
end

end equivalence_logique_1



--------------------------------
namespace preuve_par_cas

lemma exercise.produit_pair (n m:ℤ) :
(even n or even m) → even (n*m) :=
/- dEAduction
pretty_name = "Pair fois un entier"
-/
begin
  todo
end


lemma exercise.multiple_de_quatre (n:ℕ) :
divides 4 (1+((-1:ℤ))^n*(2*n-1)) :=
/- dEAduction
pretty_name = "Des multiples de quatre"
-/
begin
  todo
end

lemma exercise.impair (n: ℤ) :
odd (5*n^2 + 3*n + 7) :=
/- dEAduction
pretty_name = "Tous impairs!"
-/
begin
  todo
end

end preuve_par_cas



--------------------------------
namespace preuves_par_contraposee
/- dEAduction
pretty_name = "Preuves par contraposée"
-/

lemma exercise.pair_impair {n : ℤ} :
(even (n^2 - 6*n + 5)) → (odd n) :=
/- dEAduction
pretty_name = "Pair et impair"
description = "Essayer la preuve directe... puis la contraposée !"
-/
begin
  todo
end

lemma exercise.carre_pair {n : ℤ} : (even (n^2)) → (even n) :=
/- dEAduction
pretty_name = "Carré pair implique pair"
description = "Tout nombre dont le carré est pair est pair."
-/
begin
  todo
end

lemma exercise.carre_impair {n : ℤ} : (odd (n^2)) → (odd n) :=
/- dEAduction
pretty_name = "Carré impair implique impair"
description = "Un nombre dont le carré est impair est impair."
-/
begin
  todo
end

lemma exercise.somme_et_produit {a b : ℤ}:
(even (a*b) ∧ even (a+b)) → (even a ∧ even b)
:=
/- dEAduction
pretty_name = "Somme et produit"
description = "Ici, la contraposée va nous conduire à une preuve par cas."
-/
begin
  todo
end

lemma exercise.parite3 {a b : ℤ} :
(odd (a^2*(b^2-2*b))) → (odd a ∧ odd b) :=
/- dEAduction
pretty_name = "Parité III"
description = "Tous impairs"
-/
begin
  todo
end

lemma exercise.divise1 {a b c : ℤ}:
(not (divides a (b*c))) → not (divides a b)
:=
/- dEAduction
pretty_name = "Divise I"
-/
begin
  todo
end

lemma exercise.divise2 {a : ℤ}:
(not (divides 4 (a^2) )) → (odd a)
:=
/- dEAduction
pretty_name = "Impair si divise pas"
-/
begin
  todo
end

end preuves_par_contraposee

-----------------------------
namespace equivalence_logique_2
/- dEAduction
pretty_name = "Equivalence logique II"
-/

lemma exercise.carre_pair {n : ℤ} : (even n) ↔ (even (n^2)) :=
/- dEAduction
pretty_name = "Pair ssi carré pair"
description = """
Un nombre est pair si et seulement si son carré est pair.
Pensez à utiliser les exercices précédents..."""
-/
begin
  todo
end

end equivalence_logique_2

--------------------------
namespace preuve_par_absurde
/- dEAduction
pretty_name = "Preuve par l'absurde"
-/

lemma exercise.inegalite (a b : ℤ) :
a^2 - 4*b ≠ 2 :=
/- dEAduction
pretty_name = "Non égal à deux"
description = "Par l'absurde, montrer d'abord que a² doit être pair, en introduisant un but intermédiaire."
-/
begin
--   by_contradiction H_0,
-- push_neg_once at H_0, trace "EFFECTIVE CODE n°19.1",
-- have H_1: (even (a ^ 2)),
-- use ((1: @int) + ((2: @int) * b)),
-- solve1 {trace "EFFECTIVE CODE n°47.1", compute_n 10 }, trace "EFFECTIVE CODE n°43.3", trace "EFFECTIVE CODE n°41.3",
-- have H_2 := preuves_par_contraposee.exercise.carre_pair H_1, trace "EFFECTIVE CODE n°62.0",
-- rw definitions.definition.even at H_2,
-- cases H_2 with c H_3,
-- rw H_3 at H_0,
-- have H_4: (divides (4) 2),
-- rw definitions.definition.divides,
-- use (c*c-b),  --> Fail because Lean is looking for a natural number.
  todo,
end

end preuve_par_absurde

-------------------------------
namespace preuve_par_recurrence
/- dEAduction
pretty_name = "Preuve par récurrence"
-/

-- TODO: sommes quelconques, 
-- binome de Newton ou relation dans le triangle de Pascal

lemma exercise.even_or_odd : ∀n: nat, (even n or odd n) :=
/- dEAduction
pretty_name = "Pair ou impair I"
available_theorem = "ALL -not_even_is_odd"
-/
begin
  -- apply induction.simple_induction, rotate,
  -- intro n,
  -- intro H1,
  -- cases H1 with H2 H3,
  -- right,
  -- rw definitions.definition.even at H2,
  -- cases H2 with b H5,
  -- rw H5,
  -- use (b),
  -- norm_num,
    todo
end

lemma exercise.even_or_odd2 : ∀n: nat, (not (even n)) ↔ odd n :=
/- dEAduction
pretty_name = "Pair ou impair II"
available_theorem = "ALL -not_even_is_odd"
-/
begin
    todo
end

end preuve_par_recurrence




namespace contre_exemples
/- dEAduction
pretty_name = "Contre-exemples"
-/
lemma exercise.prime :
not(∀n: nat, prime (n^2 - n + 11)) :=
/- dEAduction
pretty_name = "Premier ?"
-/
begin
    todo
end

end contre_exemples


--------------------------------
namespace intervertion_quantificateurs
/- dEAduction
pretty_name = "Intervertion de quantificateurs"
-/

lemma exercise.pour_tout_il_existe   :
∀ n:ℤ, ∃  m:ℤ, m=n+5
:=
/- dEAduction
pretty_name = "Pour tout suivi de Il existe"
open_question = true
-/
begin
  todo
end


-- exo 10 page 55
lemma exercise.il_existe_pour_tout :
 ∃  m:ℤ, ∀ n:ℤ, m=n+5
 :=
/- dEAduction
pretty_name = "Il existe suivi de Pour tout"
open_question = true
-/
begin
  todo
end

end intervertion_quantificateurs

namespace Multiples
/- dEAduction
pretty_name = "Multiples ?"
description = "Tout nombre qui est multiple de 2 et de 3 est multiple de 5"
-/

lemma exercise.multiples :
∀a b: ℤ, (multiple a 2 and multiple b 3) → multiple (a+b) 5 :=
/- dEAduction
pretty_name = "Propriétés existentielles : multiples et somme"
description = """
VRAI ou FAUX : la somme d'un multiple de 2 et d'un mulitple de 3
est un multiple de 5.
Utilisez une propriété existentielle avec le bouton "Utiliser ∃".
"""
open_question = true
[settings]
functionality.automatic_use_of_exists = true
-/
begin
  todo,
end

end Multiples

-- namespace autres_exercices


-- lemma theorem.divides_one {a b : ℤ} :
-- a * b = 1 → (a=1 ∧ b=1) ∨ (a=-1 ∧ b=-1) :=
-- /- dEAduction
-- PrettyName
--   Diviseurs de 1
-- -/
-- begin
--   todo
-- end


-- -- The following needs to be able to simplify a = a*b when a != 0
-- lemma exercise.mutual_divisors {a b : ℤ} :
-- (divides a b and divides b a) → (a = b or a = -b) :=
-- /- dEAduction
-- PrettyName
--   Diviseurs mutuels
-- -/
-- begin
--   todo
--   -- rintro ⟨H1 , H2⟩,
--   -- cases H1 with d H1,
--   -- cases H2 with d' H2,
--   -- rw H1 at H2,
--   -- by_cases a=0, rotate,
--   -- have H2b : (d * d' =1),
--   -- todo, todo, todo,
-- end
-- end autres_exercices