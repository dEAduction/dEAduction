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
Title
    Arithmétique
Author
    Frédéric Le Roux, Thomas Richard
Institution
    Université du monde
Description
    Premier essai d'arithmétique
Display
    prime --> (-1, " est premier")
    puissancede2 --> (-1, " est une puissance de 2")
Settings
    functionality.calculator_available --> true
    others.Lean_request_method --> "normal"
-/

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
PrettyName
    Définitions
-/

variables {IntegerSubGroup:Type} [has_add IntegerSubGroup] 
[has_one IntegerSubGroup] [has_mul IntegerSubGroup] 

-- def even (a: ℤ) := ∃ b, a = 2*b 

def even (a: IntegerSubGroup) := ∃ (b: IntegerSubGroup), a = 2*b 

def odd (a: IntegerSubGroup) := ∃ (b: IntegerSubGroup), a = 2*b + 1 

def divides (a b: IntegerSubGroup) := ∃ c, b = a * c

-- lemma auxiliary_theorem.nat_even {a:ℕ} : (even a) ↔ ∃ b, a = 2*b :=
-- begin
--   todo
-- end
-- AuxiliaryDefinitions
--   auxiliary_theorem.nat_even

lemma definition.even {a: IntegerSubGroup} : (even a) ↔ ∃ (b: IntegerSubGroup), a = 2*b :=
/- dEAduction
PrettyName
  Pair
ImplicitUse
  True
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
PrettyName
  Impair
ImplicitUse
  True
AuxiliaryDefinitions
  auxiliary_theorem.nat_odd
-/
begin
  refl
end


-- NB: the following is obviously false for general type u...
axiom AX: IntegerSubGroup = ℕ ∨ IntegerSubGroup = ℤ
lemma theorem.not_even_is_odd {a: IntegerSubGroup} :
(not (even a)) ↔ odd a :=
/- dEAduction
PrettyName
  Pair et impair
AuxiliaryDefinitions
  auxiliary_theorem.nat_not_even_is_odd
-/
begin
  todo
end


lemma theorem.signe_parite_pair  :
∀ n:ℕ, ((even n) → ((-1:ℤ)^n = 1 ))
:= 
/- dEAduction
PrettyName
   (-1) puissance pair
-/
begin
   todo
end

lemma theorem.signe_parite_impair  :
∀ n:ℕ, ((odd n) → ((-1:ℤ)^n = -1 ))
:= 
/- dEAduction
PrettyName
   (-1) puissance impair
-/
begin
   todo
end


lemma definition.divides {a b : IntegerSubGroup} : (divides a b) ↔ (∃ (c: IntegerSubGroup), b = a * c) :=
/- dEAduction
PrettyName
  Divise
ImplicitUse
  True
-/
begin
  refl
end

def puissancede2 (a :ℕ) := ∃ b : ℕ, a = 2^b

lemma definition.puissancede2 {a:ℕ} : (puissancede2 a) ↔ ∃ b:ℕ, a = 2^b :=
/- dEAduction
PrettyName
  Puissance de 2
ImplicitUse
  True
-/
begin
  refl
end


-- Nb premier
lemma definition.prime {p: ℕ} : (prime p) ↔ (∀ n:ℕ, divides n p → (n=1 or n=p)) :=
/- dEAduction
PrettyName
  Nombre premier
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
  - Contrapposée
  - Absurde
-/

--------------------------------
namespace preuve_d_existence
/- dEAduction
PrettyName
  Preuves d'existence
-/

lemma exercise.quatorze : even (14:ℤ) :=
/- dEAduction
PrettyName
  Quatorze est pair
-/
begin
  todo
end

lemma exercise.existe_pair : ∃(a:ℤ), (even a) :=
/- dEAduction
PrettyName
  Il existe un entier pair
-/
begin
  todo
end

lemma exercise.existe_impair : ∃(a:ℤ), (odd a) :=
/- dEAduction
PrettyName
  Il existe un entier impair
-/
begin
  todo
end

lemma exercise.divise : divides 7 42 :=
/- dEAduction
PrettyName
  Sept divise quarante-deux.
-/
begin
  todo
end

lemma exercise.nombre_8  :
(even 8) ∧ (puissancede2 8)
 :=
/- dEAduction
PrettyName
 8 est pair et une puissance de 2 
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
PrettyName
  Carré d'un nombre pair
Description
  Le carré d'un nombre pair est pair
-/
begin
  todo
end

variables {IntegerSubGroup:Type} [has_add IntegerSubGroup] 
[has_one IntegerSubGroup] [has_mul IntegerSubGroup] 

lemma exercise.divise_transitive (a b c : IntegerSubGroup) :
(divides a b) ∧ (divides b c) → (divides a c) :=
/- dEAduction
PrettyName
  La divisibilité est transitive  
-/
begin
  todo
end

lemma exercise.produit_pairs (n m:ℤ) :
(even n ∧ even m) → even (n*m) :=
/- dEAduction
PrettyName
  Pair fois pair
-/
begin
  todo
end

lemma exercise.produit_impairs (n m:ℤ) :
(odd n ∧ odd m) → odd (n*m) :=
/- dEAduction
PrettyName
  Impair fois impair
-/
begin
  todo
end

end implications


--------------------------------
namespace preuves_universelles
/- dEAduction
PrettyName
  Preuves d'énoncés universels
-/

lemma exercise.carre_pair1 :
∀{n:ℤ}, (even n) → (even (n^2)) :=
/- dEAduction
PrettyName
  Carré d'un nombre pair
Description
  Le carré d'un nombre pair est pair
-/
begin
  todo
end

lemma exercise.mul_divides  : ∀ {a b c : ℤ}, divides a b → divides a (b*c) :=
/- dEAduction
PrettyName
  Diviseurs d'un multiple
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

--------------------------------
namespace intervertion_quantificateurs
/- dEAduction
PrettyName
  Intervertion de quantificateurs
-/

lemma exercise.pour_tout_il_existe   :
∀ n:ℤ, ∃  m:ℤ, m=n+5
:=
/- dEAduction
PrettyName
 Pour tout suivi de Il existe 
OpenQuestion
 True
-/
begin
  todo
end


-- exo 10 page 55
lemma exercise.il_existe_pour_tout :
 ∃  m:ℤ, ∀ n:ℤ, m=n+5
 :=
/- dEAduction
PrettyName
 Il existe suivi de Pour tout
OpenQuestion
 True
-/
begin
  todo
end

end intervertion_quantificateurs

--------------------------------
namespace preuve_par_cas

lemma exercise.multiple_de_quatre (n:ℕ) :
divides 4 (1+((-1:ℤ))^n*(2*n-1)) :=
/- dEAduction
PrettyName
  Des multiples de quatre
-/
begin
  todo
end

lemma exercise.impair (n: ℤ) :
odd (5*n^2 + 3*n + 7) :=
/- dEAduction
PrettyName
  Tous impairs!
-/
begin
  todo
end

end preuve_par_cas



--------------------------------
namespace preuves_par_contrapposee
/- dEAduction
PrettyName
  Preuves par contrapposée
-/

lemma exercise.pair_impair {n : ℤ} :
(even (n^2 - 6*n + 5)) → (odd n) :=
/- dEAduction
PrettyName
  Pair et impair
Description
  Essayer la preuve directe... puis la contrapposée !
-/
begin
  todo
end

lemma exercise.carre_pair {n : ℤ} : (even (n^2)) → (even n) :=
/- dEAduction
PrettyName
  Carré pair implique pair
Description
  Tout nombre dont le carré est pair est pair.
-/
begin
  todo
end

lemma exercise.carre_impair {n : ℤ} : (odd (n^2)) → (odd n) :=
/- dEAduction
PrettyName
  Carré impair implique impair
Description
  Un nombre dont le carré est impair est impair.
-/
begin
  todo
end

lemma exercise.parite3 {a b : ℤ} :
(odd (a^2*(b^2-2*b))) → (odd a ∧ odd b) :=
/- dEAduction
PrettyName
  Parité III
Description
  Tous impairs
-/
begin
  todo
end

lemma exercise.divise1 {a b c : ℤ}:
(not (divides a (b*c))) → not (divides a b)
:=
/- dEAduction
PrettyName
  Divise I
-/
begin
  todo
end

lemma exercise.divise2 {a : ℤ}:
(not (divides 4 (a^2) )) → (odd a)
:=
/- dEAduction
PrettyName
  Impair si divise pas
-/
begin
  todo
end

lemma exercise.somme_et_produit {a b : ℤ}:
(even (a*b) ∧ even (a+b)) → (even a ∧ even b)
:=
/- dEAduction
PrettyName
  Somme et produit
Description
  Ici, la contrapposée va nous conduire à une preuve par cas.
-/
begin
  todo
end

end preuves_par_contrapposee

--------------------------
namespace preuve_par_absurde
/- dEAduction
PrettyName
  Preuve par l'absurde
-/

lemma exercise.inegalite (a b : ℤ) :
a^2 - 4*b ≠ 2 :=
/- dEAduction
PrettyName
  Non égal à deux
Description
  Par l'absurde, montrer d'abord que a² doit être pair, en introduisant un but intermédiaire.
-/
begin
  todo
end

end preuve_par_absurde


-----------------------------
namespace equivalence_logique

lemma exercise.carre_pair {n : ℤ} : (even n) ↔ (even (n^2)) :=
/- dEAduction
PrettyName
  Pair ssi carré pair
Description
  Un nombre est pair si et seulement si son carré est pair.
-/
begin
  todo
end

lemma exercise.difference_carres {n : ℤ} : (odd n) ↔ (∃m, n=(m+1)^2 - m^2) :=
/- dEAduction
PrettyName
  Différence de deux carrés consécutifs
Description
  Un nombre peut s'écrire comme une différence de deux carrés consécutifs
  si et seulement si il est impair.
-/
begin
  todo
end

end equivalence_logique


-------------------------------
namespace preuve_par_recurrence
/- dEAduction
PrettyName
  Preuve par récurrence
-/

-- TODO: sommes quelconques, 
-- binome de Newton ou relation dans le triangle de Pascal

lemma exercise.even_or_odd : ∀n: nat, (even n or odd n) :=
/- dEAduction
PrettyName
  Pair ou impair I
AvailableTheorem
  ALL -not_even_is_odd
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
PrettyName
  Pair ou impair II
AvailableTheorem
  ALL -not_even_is_odd
-/
begin
    todo
end

end preuve_par_recurrence


namespace contre_exemples
/- dEAduction
PrettyName
  Contre-exemples
-/
lemma exercise.prime :
not(∀n: nat, prime (n^2 - n + 11)) :=
/- dEAduction
PrettyName
  Premier ?
-/
begin
    todo
end

end contre_exemples

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
