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
    divise --> (-2, " | ", -1)
    prime --> (-1, " est premier")
-/

---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------


open nat
universe u

-- theorem two_step_induction {P : ℕ → Sort u} (H1 : P 0) (H2 : P 1)
--     (H3 : ∀ (n : ℕ) (IH1 : P n) (IH2 : P (succ n)), P (succ (succ n))) : Π (a : ℕ), P a
-- | 0               := H1
-- | 1               := H2
-- | (succ (succ n)) := H3 _ (two_step_induction _) (two_step_induction _)

open set

-----------------
namespace logique

lemma definition.iff {P Q : Prop} : (P ↔ Q) ↔ ((P → Q) ∧ (Q → P)) :=
/- dEAduction
PrettyName
    Equivalence logique
-/
begin
  exact iff_def,
end

lemma theorem.disjonction_eqv_implication (P Q: Prop) :
(P ∨ Q) ↔ ((not P) → Q)
:= 
/- dEAduction
PrettyName
    Disjonction sous forme d'implication
-/
begin
  tautology,
end

lemma theorem.induction {P: nat → Prop} (H0: P 0)
(H1: ∀ (n : ℕ) (IH1 : P n), P (n+1) ) :
∀n, P n
:=
begin
  todo
end 

end logique

---------------------
namespace definitions
/- dEAduction
PrettyName
    Définitions
-/

def even (a: ℤ) := ∃ b, a = 2*b 

def odd (a: ℤ) := ∃ b, a = 2*b + 1 

def divides (a b:ℤ) := ∃ c, b = a * c

lemma auxiliary_theorem.nat_even {a:ℕ} : (even a) ↔ ∃ b, a = 2*b :=
begin
  todo
end

lemma definition.even {a:ℤ} : (even a) ↔ ∃ b, a = 2*b :=
/- dEAduction
PrettyName
  Pair
ImplicitUse
  True
AuxiliaryDefinitions
  auxiliary_theorem.nat_even
-/
begin
  refl
end

lemma auxiliary_theorem.nat_odd {a:ℕ} : (odd a) ↔ ∃ b, a = 2*b :=
begin
  todo
end

lemma definition.odd {a:ℤ} : (odd a) ↔ ∃ b, a = 2*b + 1 :=
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

-- Does not work
-- lemma auxiliary_theorem.not_even_is_odd {a:ℤ} :
-- (not (odd a)) ↔ even a :=
-- begin
--     todo
-- end

lemma auxiliary_theorem.nat_not_even_is_odd {a:ℕ} :
(not (even a)) ↔ odd a :=
begin
  todo
end

lemma theorem.not_even_is_odd {a:ℤ} :
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


lemma definition.divides {a b : ℤ} : (divides a b) ↔ (∃ c, b = a * c) :=
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
-- namespace provisoirement_non_classes

-- lemma exercise.  :
--  :=
-- /- dEAduction
-- PrettyName
  
-- -/
-- begin
--   todo
-- end

-- TODO: preuves de cas similaire


-- end provisoirement_non_classes


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

lemma exercise.existe_pair : ∃a, (even a) :=
/- dEAduction
PrettyName
  Il existe un entier pair
-/
begin
  todo
end

lemma exercise.existe_impair : ∃a, (odd a) :=
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

-- lemma exercise.  :
--  :=
-- /- dEAduction
-- PrettyName
  
-- -/
-- begin
--   todo
-- end

-- TODO: formaliser :
--  tout entier impair est la différence de deux carrés

-- exo 1 page 42 
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


lemma exercise.divise_transitive (a b c : ℤ) :
(divides a b) ∧ (divides b c) → (divides a c) :=
/- dEAduction
PrettyName
  La divisibilité est transitive  
-/
begin
  todo
end

-- lemma exercise.  :
--  :=
-- /- dEAduction
-- PrettyName
  
-- -/
-- begin
--   todo
-- end

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
∀n, (even n) → (even (n^2)) :=
/- dEAduction
PrettyName
  Carré d'un nombre pair
Description
  Le carré d'un nombre pair est pair
-/
begin
  todo
end

-- lemma exercise.  :
--  :=
-- /- dEAduction
-- PrettyName
  
-- -/
-- begin
--   todo
-- end

end preuves_universelles

--------------------------------
namespace intervertion_quantificateurs
/- dEAduction
PrettyName
  Intervertion de quantificateurs
-/


-- exo 9 page 55
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

-- lemma exercise.  :
--  :=
-- /- dEAduction
-- PrettyName
  
-- -/
-- begin
--   todo
-- end

lemma exercise.multiple_de_quatre (n:ℕ) :
divides 4 (1+(-1)^n*(2*n-1)) :=
/- dEAduction
PrettyName
  (**) Des multiples de quatre
-/
begin
  todo
end

-- TODO: la réciproque (implication, univ, exist)

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
  Un nombre dont le carré est pair est pair.
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
  (à écrire)
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
Description
  (à écrire)
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
Description
  (à écrire)
-/
begin
  todo
end

-- Et aussi une preuve par cas, non ?
lemma exercise.somme_et_produit {a b : ℤ}:
(even (a*b) ∧ even (a+b)) → (even a ∧ even b)
:=
/- dEAduction
PrettyName
  Somme et produit
Description
  (à écrire)
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

-- TODO : irrationalite racine. On a besoin :
-- existence d'une fraction irréductible

-- lemma exercise. {a b : ℤ} :
--  :=
-- /- dEAduction
-- PrettyName

-- -/
-- begin
--   todo
-- end

-- Déplacer ? But intermédiaire, et carré pair
lemma exercise.inegalite (a b : ℤ) :
a^2 - 4*b ≠ 2 :=
/- dEAduction
PrettyName
  Non égal à deux
Description
  Par l'absurde, montrer d'abord que a doit être pair...
-/
begin
  todo
end


-- racine de 2 !

end preuve_par_absurde

-----------------------------
namespace equivalence_logique

-- TODO: ajouter theorem: non pair ssi impair,
-- puis l'enlever quand on le démontre plus tard par récurrence
lemma exercise.carre_pair {n : ℕ} : (even n) ↔ (even (n^2)) :=
/- dEAduction
PrettyName
  Pair ssi carré pair
Description
  Un nombre est pair si et seulement si son carré est pair.
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
-/
begin
    -- intro n, induction n with n H1,
    -- apply induction.simple_induction,
    -- apply induction.strong_induction,
    -- rotate, intros n HR1,
    -- targets_analysis,
    -- all_goals {hypo_analysis2 2},
    todo
end

lemma exercise.even_or_odd2 : ∀n: nat, (not (even n)) ↔ odd n :=
/- dEAduction
PrettyName
  Pair ou impair II
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

namespace autres_exercices

lemma exercise.mul_divides {a b c : ℤ} : divides a b → divides a (b*c) :=
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

lemma theorem.divides_one {a b : ℤ} :
a * b = 1 → (a=1 ∧ b=1) ∨ (a=-1 ∧ b=-1) :=
/- dEAduction
PrettyName
  Diviseurs de 1
-/
begin
  todo
end

lemma exercise.mutual_divisors {a b : ℤ} :
(divides a b and divides b a) → (a = b or a = -b) :=
/- dEAduction
PrettyName
  Diviseurs mutuels
-/
begin
  todo
  -- rintro ⟨H1 , H2⟩,
  -- cases H1 with d H1,
  -- cases H2 with d' H2,
  -- rw H1 at H2,
  -- by_cases a=0, rotate,
  -- have H2b : (d * d' =1),
  -- todo, todo, todo,
end

end autres_exercices
