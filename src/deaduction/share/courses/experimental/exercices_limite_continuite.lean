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

-------------------------
-- dEAduction METADATA --
-------------------------
/- dEAduction
Title
    Limite et continuité
Author
    Frédéric Le Roux
Institution
    Université du monde
Description
    Des exercices sur les limites des suites
    et la continuité des fonctions 
-/


/-- Lots of definitions -/
definition limit (u : ℕ → ℝ) (l : ℝ) : Prop :=
∀ ε > 0, ∃ N, ∀ n ≥ N, | u n - l | < ε

definition converging_seq (u : ℕ → ℝ) : Prop :=
∃ l, limit u l

definition limit_plus_infinity (u : ℕ → ℝ) : Prop :=
∀ M:ℝ, ∃ N:ℕ, ∀ n ≥ N, u n ≥ M

definition increasing_seq (u : ℕ → ℝ) : Prop :=
∀ p q , p ≤ q → u p ≤ u q

definition bounded_above (u : ℕ → ℝ) : Prop :=
∃ M:ℝ, ∀ n, u n ≤ M

definition bounded_below (u : ℕ → ℝ) : Prop :=
∃ m:ℝ, ∀ n, u n ≥ m

definition bounded_sequence (u : ℕ → ℝ) : Prop :=
∃ M>0, ∀ n, | u n | ≤ M

definition even (n:ℕ) : Prop := ∃ n', n=2 * n'

definition limit_function (f : ℝ → ℝ) (a : ℝ) (l : ℝ) : Prop :=
∀ ε > 0, ∃ δ>0, ∀ x: ℝ, ( | x-a | < δ → | f x  - l | < ε )

definition continuous_at (f : ℝ → ℝ) (a : ℝ) : Prop :=
limit_function (λ x, f x) a (f a)

definition continuous (f: ℝ → ℝ) : Prop :=
∀ a, continuous_at f a

definition cauchy (u: ℕ → ℝ) : Prop :=
∀ ε>0, ∃ N: ℕ, ∀ p≥N, ∀ q≥N, |u p - u q | < ε

definition uniformly_continuous (f: ℝ → ℝ) : Prop :=
∀ ε>0, ∃ δ>0, ∀ x y: ℝ,
(|x - y| < δ → |f x - f y | < ε)

section course
open tactic.interactive
-- notation `|` x `|` := abs x

-----------------
-- definitions --
-----------------
namespace definitions
/- dEAduction
PrettyName
  Définitions
-/


namespace generalites
/- dEAduction
PrettyName
  Généralités
-/

/-
abs_pos : 0 < |a| ↔ a ≠ 0
abs_mul x y : |x * y| = |x| * |y|
abs_add x y : |x + y| ≤ |x| + |y|
-/

----------------------------------
namespace maximum
-- The name RealSubGroup will be replaced by ℝ in d∃∀duction, 
-- but allows to treat the cases of integers or rationals.
variables {RealSubGroup : Type} [decidable_linear_order RealSubGroup] 

lemma definition.max (a b c : RealSubGroup) :
a = max b c ↔ (b ≤ a ∧ c ≤ a ∧ (a=b ∨ a=c))
:=
begin
  todo
end

lemma theorem.ppe_max_gauche :
∀ a b : RealSubGroup, a ≤ max a b :=
begin
  intros a b,
  -- hypo_analysis,
  -- norm_num, tautology,
  exact le_max_left a b,
  -- todo
end

lemma theorem.ppe_max_droite :
∀ a b : RealSubGroup,  b ≤ max a b :=
begin
  have H := @theorem.ppe_max_gauche,
  intros a b, norm_num, tautology,
  -- exact le_max_right a b,
end

lemma theorem.max_ppe
(a b c : RealSubGroup) (Ha: a ≤ c) (Hb: b ≤ c) :
max a b ≤ c :=
begin
  norm_num, tautology,
  -- exact max_le Ha Hb,
end

lemma theorem.max_pp
(a b c : RealSubGroup) (Ha: a < c) (Hb: b < c) :
max a b < c :=
begin
  norm_num, tautology,
  -- exact max_lt Ha Hb,
end

end maximum

namespace valeur_absolue
variables {RealSubGroup : Type} [decidable_linear_ordered_comm_ring RealSubGroup] 

lemma definition.valeur_absolue (a b : RealSubGroup) :
a = abs b ↔ (a ≥ 0 ∧ (a=b ∨ a=-b))
:=
begin
  todo
end

lemma theorem.valeur_absolue :
∀ x : RealSubGroup,
((0 ≤ x) → (abs x = x)) ∧ ((x ≤ 0) → (abs x = -x)) :=
begin
  intro x, split, exact abs_of_nonneg, exact abs_of_nonpos,
end

lemma theorem.majoration_valeur_absolue :
∀ x r : RealSubGroup, (abs x < r) ↔ ((-r < x) ∧ (x < r))
:= 
/- dEAduction
PrettyName
  Majoration d'une valeur absolue
-/
begin
  intros x r,
  exact abs_lt
end


lemma theorem.inegalite_triangulaire :
∀ x y : RealSubGroup, |x + y| ≤ |x| + |y|
:= 
/- dEAduction
PrettyName
  Inégalité triangulaire
-/
begin
  intros x y, exact abs_add x y 
end

lemma theorem.valeur_absolue_produit :
∀ x y : RealSubGroup,  |x * y| = |x| * |y|
:= 
/- dEAduction
PrettyName
  Valeur absolue d'un produit
-/
begin
  intros x y, exact abs_mul x y 
end

end valeur_absolue

end generalites
namespace suites

------------------------------
-- Définitions de la limite --
------------------------------

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
  refl
end

lemma definition.converging_seq
{u : ℕ → ℝ} :
(converging_seq u) ↔ 
∃ l, limit u l
:= 
/- dEAduction
PrettyName
  Suite convergente
ImplicitUse
  True
-/
begin
  refl
end

lemma definition.limit_plus_infinity
{u : ℕ → ℝ} :
(limit_plus_infinity u) ↔ ∀ M:ℝ, ∃ N:ℕ, ∀ n ≥ N, u n ≥ M := 
/- dEAduction
PrettyName
  Limite infinie d'une suite
ImplicitUse
  True
-/
begin
  refl
end

lemma definition.increasing_seq
{u : ℕ → ℝ} :
(increasing_seq u) ↔ 
∀ p q, p ≤ q → u p ≤ u q
:= 
/- dEAduction
PrettyName
  Suite croissante
ImplicitUse
  True
-/
begin
  refl
end

lemma definition.bounded_above 
{u : ℕ → ℝ} :
(bounded_above u) ↔ 
∃ M:ℝ, ∀ n,  u n ≤ M
:= 
/- dEAduction
PrettyName
  Suite majorée
ImplicitUse
  True
-/
begin
  refl
end

-- lemma definition.bounded_below 
-- {u : ℕ → ℝ} :
-- (bounded_below_sequence u) ↔ 
-- ∃ M:ℝ, ∀ n,  u n ≥ M
-- := 
-- /- dEAduction
-- PrettyName
--   Suite minorée
-- ImplicitUse
--   True
-- -/
-- begin
--   refl
-- end

lemma definition.bounded 
{u : ℕ → ℝ} :
(bounded_sequence u) ↔ 
∃ M>0, ∀ n, | u n | ≤ M
:= 
/- dEAduction
PrettyName
  Suite bornée
ImplicitUse
  True
-/
begin
  refl
end

end suites

namespace fonctions

lemma definition.composition {X Y Z: Type} {f: X → Y} {g:Y → Z} {x:X}:
set.composition g f x = g (f x)
:=
begin
    todo,
end

lemma definition.limit_function (f : ℝ → ℝ) (a : ℝ) (l : ℝ) : 
limit_function f a l ↔ 
( ∀ ε > 0, ∃ δ>0, ∀ x: ℝ, ( | x-a | < δ → | f x  - l | < ε ) ):=
/- dEAduction
PrettyName
  Limite d'une fonction
ImplicitUse
  True
-/
begin
  refl
end

lemma definition.continuous_at (f : ℝ → ℝ) (a : ℝ) :
(continuous_at f a) ↔ (limit_function f a (f a)) :=
/- dEAduction
PrettyName
  Continuité en un point
-/
begin
  refl
end

lemma definition.continuous (f: ℝ → ℝ) :
(continuous f) ↔ ∀ a, continuous_at f a :=
/- dEAduction
PrettyName
  Continuité
ImplicitUse
  True
-/
begin
  refl
end


end fonctions

end definitions

-----------------
--  exercices  --
-----------------

namespace preliminaires
/- dEAduction
PrettyName
  Un exercice préliminaire
-/

lemma exercise.plus_petit_que_tout_pos (x: ℝ):
(∀ ε>0, x < ε) → x ≤ 0 :=
/- dEAduction
PrettyName
  Plus petit que tout
-/
begin
  todo
end

end preliminaires

namespace exercices_suites_I
/- dEAduction
PrettyName
  Exercices sur les suites I
-/

-- open definitions

-- --------------------------------------------------

-- lemma exercise.limit_alt :
-- not (converging_seq (λ n, (-1)^n))  := 
-- /- dEAduction
-- PrettyName
--   La suite -1, 1, -1, 1, ... ne converge pas.
-- -/
-- begin
--   by_contradiction H1,
--   cases H1 with l H2,
--   have H4: (((1): @real)) > ((0): @real), rotate, have H5 := @H2 (((1): @real)) (H4), rotate 1, solve1 {norm_num at * },
--   cases H5 with N H6,
--   have H8: (((2): @nat) * N) ≥ N, rotate, have H9 := @H6 (((2): @nat) * N) (H8), rotate 1, solve1 {norm_num at *, compute_n 10 },
--   simp only [] with simp_arith  at H9,
--   have H10: (((-1: int) ^ (2 * N)) = 1),


-- end


-- namespace exemples
-- Ne fonctionnent pas : 
-- il faut manipuler des partie entières,

-- lemma exercise.limit_inverse :
-- converging_seq (λ n, 1/n)  := 
-- /- dEAduction
-- PrettyName
--   La suite des inverses des entiers est convergente.
-- Description
--   Un exemple très simple de limite.
--   Savez-vous trouver le bon "N" ?
-- -/
-- begin
--   todo,
-- end

-- lemma exercise.limit_racine :
-- limit_plus_infinity  (λ n,  n^(1/2))  := 
-- /- dEAduction
-- PrettyName
--   La suite des racines carrées des entiers tend vers l'infini.
-- Description
--   Un deuxième exemple, cette fois-ci avec une suite divergente.
-- -/
-- begin
--   todo,
-- end
-- end exemples


lemma exercise.limit_constante 
(u : ℕ → ℝ) (c : ℝ) (H : ∀ n, u n = c) :
converging_seq u :=
/- dEAduction
PrettyName
  La limite d'une suite constante !
Description
  Dans ce premier exercice,
  il s'agit de démontrer, dans un cas très simple,
  l'existence d'une limite.
-/
begin
  todo,
end

lemma exercise.croissante_non_majoree
(u: ℕ → ℝ) (H1: increasing_seq u) (H2: not (bounded_above u)) :
limit_plus_infinity u :=
/- dEAduction
PrettyName
  Une suite croissante non majorée tend vers plus l'infini
Description
  Dans ce deuxième exercice,
  il s'agit à nouveau de démontrer une limite, mais infinie.
-/
begin
  todo,
end


lemma exercise.limite_positive
(u : ℕ → ℝ) (l : ℝ) (H : limit u l)
(H' : l >0) :
∃ N, ∀ n ≥ N, u n > 0
:=
/- dEAduction
PrettyName
  Suite dont la limite est strictement positive
Description
  Dans ce troisième exercice,
  il s'agit d'utiliser une hypothèse de limite.
-/
begin
  -- have W := exercise.limit_constante,
  -- hypo_analysis,
  todo,
end


lemma exercise.limite_inegalites
(u v: ℕ → ℝ) (l l' : ℝ) (H : limit u l)
(H' : limit v l'):
(∀n, u n ≤ v n ) → l ≤ l'
:=
/- dEAduction
PrettyName
  Passage à la limite dans une inégalité (*)
Description
  Comment démarrer ??
  Comment avoir un epsilon pertinent auquel appliquer nos
  définitions de limites ?...
-/
begin
  todo,
end

end exercices_suites_I



namespace exercices_suites_II
/- dEAduction
PrettyName
  Exercices sur les suites II
-/

lemma exercise.couper_epsilon_en_deux
(u : ℕ → ℝ) (l : ℝ) :
(limit u l) ↔ 
∀ ε > 0, ∃ N, ∀ n ≥ N, | u n - l | < 2*ε
:=
/- dEAduction
PrettyName
  Couper les epsilons en deux
Description
  Nous avons maintenant une limite dans les hypothèses,
  et une limite dans la conclusion !
-/
begin
  todo,
end


lemma exercise.couper_epsilon_en_100
(u : ℕ → ℝ) (l : ℝ) :
(limit u l) ↔ 
∀ ε > 0, ∃ N, ∀ n ≥ N, | u n - l | < 100*ε
:=
/- dEAduction
PrettyName
  Couper les epsilons en cent !
Description
  Simple variante du précédent,
  pour voir si vous avez compris...
-/
begin
  todo,
end

lemma exercise.limite_somme
(u v: ℕ → ℝ) (l l' : ℝ) (H : limit u l)
(H' : limit v l') :
limit (λn, u n + v n) (l+l')
:=
/- dEAduction
PrettyName
  Limite d'une somme
Description
  Aide : il peut être judicieux d'utiliser le résultat
  d'un exercice précédent...
-/


begin
  todo
end

lemma exercise.limite_unique
(u : ℕ → ℝ) (l : ℝ)(l' : ℝ) (H : limit u l) (H' : limit u l') :
l = l' 
:=
/- dEAduction
PrettyName
  Unicité de la limite (*)
Description
  Ici il peut être judicieux de raisonner par l'absurde,
  et de traiter séparément les cas l < l' et l' < l 
-/
begin
  todo,
end


lemma exercise.gendarmes
(u v w  : ℕ → ℝ) (l : ℝ) 
(H : limit u l) (H' : limit w l)
(H'' : ∀n, (((u n) ≤ v n) and ((v n) ≤ w n))) :
limit v l
:=
/- dEAduction
PrettyName
  Théorème des gendarmes (*)
-/
begin
  todo,
end


lemma exercise.borne_fois_zero
(u v: ℕ → ℝ) (H : limit u 0)
(H' : bounded_sequence v) :
limit (λn, (u n) * (v n)) 0
:=
/- dEAduction
PrettyName
  (**) Limite d'un produit (cas particulier)
-/
begin
  todo,
end


/-
A essayer : appliquer somme, CV implique borné, borné x 0
-/
lemma limite_produit
(u u': ℕ → ℝ) (l l' : ℝ) (H : limit u l)
(H' : limit u' l') :
limit (λn, (u n) * (u' n)) (l*l')
:=
begin
  todo,
end

end exercices_suites_II

namespace exercices_fonctions
/- dEAduction
PrettyName
  Exercices sur les fonctions
-/

open definitions

open set

lemma exercise.limite_positive
(f: ℝ → ℝ)
(H0: continuous f) (H1: f(0) = 1):
∃ δ>(0:ℝ), ∀ x, |x| < δ → f(x) >0 :=
/- dEAduction
PrettyName
  Limite positive
Description
  Deux limites en hypothèse, une en conclusion...
-/
begin
  todo,
end

lemma exercise.composition_limite_fonction
(f: ℝ → ℝ) (g: ℝ → ℝ) (a b c : ℝ)
(H0: limit_function (λ x, f x) a b)
(H1: limit_function (λ y, g y) b c):
limit_function (λ x, g ( f ( x)) ) a c :=
/- dEAduction
PrettyName
  Limite et composition
Description
  Deux limites en hypothèse, une en conclusion...
-/
begin
  todo
end


lemma exercise.composition_continuite (f: ℝ →  ℝ) (g: ℝ → ℝ)
(H: continuous f) (H': continuous g):
continuous (composition g f) :=
/- dEAduction
PrettyName
  Continuité et composition
-/
begin 
  todo,
end


lemma exercise.image_convergente (u: ℕ → ℝ) (l : ℝ) (f: ℝ → ℝ)
(H: limit u l) (H': continuous f):
limit (λ n, f (u n)) (f l) :=
/- dEAduction
PrettyName
  Image d'une suite convergente
Description
  Deux limites en hypothèse, une en conclusion...
-/
begin 
  todo,
end

end exercices_fonctions



namespace suites_de_Cauchy
/- dEAduction
PrettyName
  Suites de Cauchy
-/


lemma definition.suite_de_cauchy
(u: ℕ → ℝ) :
cauchy u ↔ ∀ ε>0, ∃ N: ℕ, ∀ p≥N, ∀ q≥N, |u p - u q | < ε
:=
/- dEAduction
PrettyName
  Suites de Cauchy
ImplicitUse
  True
-/
begin
  refl,
end


lemma exercise.convergente_implique_cauchy (u: ℕ → ℝ): 
converging_seq u → cauchy u :=
/- dEAduction
PrettyName
  Une suite convergente est de Cauchy
-/
begin
  todo,
end


end suites_de_Cauchy


namespace continuite_uniforme
/- dEAduction
PrettyName
  Continuité uniforme
-/

lemma definition.uniformly_continuous
(f: ℝ → ℝ) : uniformly_continuous f ↔
∀ ε>0, ∃ δ>0, ∀ x y: ℝ,
(|x - y| < δ → |f x - f y | < ε)
:=
/- dEAduction
PrettyName
  Continuité uniforme
ImplicitUse
  True
-/
begin
  refl,
end

lemma exercise.continue_de_uniformement_continue
(f: ℝ → ℝ) (H0: uniformly_continuous f):
continuous f :=
/- dEAduction
PrettyName
  Uniformément continu implique continu
-/
begin
  todo,
end

lemma exercise.cauchy_uniformement_continue
(u: ℕ → ℝ) (f: ℝ → ℝ)
(H0: cauchy u) (H1: uniformly_continuous f):
cauchy (λ n:ℕ, f (u n))
:=
/- dEAduction
PrettyName
  Image d'une suite de Cauchy
-/
begin
  todo,
end

-- TODO: cauchy => bornée, bornée => valeur d'adh,
-- Cauchy + va => cv

end continuite_uniforme

-- namespace DL
-- /- dEAduction
-- PrettyName
--   Développements limités
-- -/

-- definition DL_order_0 (f: ℝ → ℝ) : Prop :=
-- ∃ (φ : ℝ → ℝ), (limit_function φ 0 0) and 
-- (∀ h, f h = f 0 + φ h)

-- definition DL_order_1 (f: ℝ → ℝ) (a : ℝ) : Prop :=
-- ∃ (φ : ℝ → ℝ), (limit_function φ 0 0) and 
-- (∀ h, f h = f 0 + a * h + (φ h) * h)

-- lemma definition.DL_order_0
-- (f: ℝ → ℝ) (a : ℝ):
-- (DL_order_0 f) ↔ (∃ (φ : ℝ → ℝ), (limit_function φ 0 0) and 
-- (∀ h, f h = f 0 + φ h))
-- :=
-- begin
--   todo
-- end

-- example 
-- (f: ℝ → ℝ):
-- (DL_order_0 f) ↔ ∃ l, (limit_function f 0 l) :=
-- begin
--   todo
-- end
-- end DL


/- 
On peut multiplier les variantes : si une fonction a une
limite >0 en un point, elle est >0 au voisinage.
Si lim f < lim g alors f < g au voisinage.

Signe à partir d'un DL !

-/


end course