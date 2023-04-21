import tactic
import data.real.basic
-- import data.set
/-
- nom des variables dans la def de limite !
- variables muettes = variables globales : bof
- calcul avec abs : abs (l'-l) /2 >0 ??
(x ≠ 0 → |x| >0)
- ne pas ajouter l'inégalité au contexte si elle y est déjà !
- 'dsimp only at h' effectue les beta-réduction : (λ x, f x) 37 = f 37
- max : def et propriétés
- utiliser specialize ??

-/


-- dEAduction tactics
import structures2      -- hypo_analysis, targets_analysis
import utils            -- no_meta_vars
import user_notations   -- notations that can be used in deaduction UI for a new object
import compute
import push_neg_once    -- pushing negation just one step

-- dEAduction definitions
import set_definitions
import real_definitions


-- class real_number_subgroup (α : Type) := 
-- (subgroup : ((α = ℕ) ∨ (α = ℤ) ∨ (α = ℚ) ∨ (α = ℝ)) )

-- lemma real_number_subgroup_nat : (nat = ℕ) ∨ (nat = ℤ) ∨ (nat = ℚ) ∨ (nat = ℝ) :=
-- begin
--   left, refl,
-- end

-- instance : real_number_subgroup nat := ⟨real_number_subgroup_nat⟩ 


local attribute [instance] classical.prop_decidable


/-- `l` is the limit of the sequence `a` of reals -/
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

/-
Max :
def
max ≥ n et n'
1) We will be using `max` a lot in this workshop. `max A B` is
the max of `A` and `B`. `max` is a definition, not a theorem, so 
that means that there will be an API associated with it, i.e. 
a list of little theorems which make `max` possible to use.
We just saw the two important theorems which we'll be using:
`le_max_left A B : A ≤ max A B` and
`le_max-right A B : B ≤ max A B`.
There are other cool functions in the `max` API, for example
`max_le : A ≤ C → B ≤ C → max A B ≤ C`. The easiest way to 
find your way around the `max` API is to *guess* what the names
of the theorems are! For example what do you think 
`max A B < C ↔ A < C ∧ B < C` is called?
-/



----------------------------------
namespace maximum
-- The name RealSubGroup will be replaced by ℝ in d∃∀duction, 
-- but allows to treat the cases of integers or rationals.
variables {RealSubGroup : Type} [decidable_linear_order RealSubGroup] 

lemma theorem.ppe_max_gauche :
∀ a b : RealSubGroup, a ≤ max a b :=
begin
  -- targets_analysis,
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
-- [has_zero RealSubGroup]

-- A modifier : faire une classe "nombres" ?
lemma theorem.valeur_absolue :
∀ x : RealSubGroup,
((0:RealSubGroup) ≤ x) → (abs x = x) and ((x ≤ 0) → (abs x = -x)) :=
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
namespace exercices_suites_I
/- dEAduction
PrettyName
  Exercices sur les suites I
-/

-- open definitions

-- --------------------------------------------------
-- namespace exemples


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
--   rw definition.limit,
--   intros ε Hε,
--   use 0,
--   intros n H1,
--   rw H,
-- `[ solve1 {norm_num at * }, trace "EFFECTIVE CODE n°4.0"] <|> `[ `[ norm_num at *, trace "EFFECTIVE CODE n°5.0"] <|> `[ skip, trace "EFFECTIVE CODE n°5.1"], compute_n 10, trace "EFFECTIVE CODE n°4.1"],
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
  -- contrapose H'' with H1,
  -- push_neg,
  -- push_neg at H1,
  -- let e := (l-l')/2, have H2 : e = (l-l')/2, refl, no_meta_vars,
  -- rw limit at H H',
  -- have H3: (e:ℝ) > 0, rotate, have H4 := H e H3, rotate 1, rotate, rotate,
  -- solve1 {norm_num at *, apply mul_pos, linarith only [H1], apply inv_pos.mpr, linarith},
  -- have H5 := H' e H3,
  -- cases H4 with n H6,
  -- cases H5 with n' H7,
  -- let n'' := max n n', have H8 : n'' = max n n', refl, no_meta_vars,
  -- have H9: (n'':ℕ) ≥ n, rotate, have H10 := H6 n'' H9, rotate 1, solve1 {norm_num at *, tautology }, rotate,
  -- have H11: (n'':ℕ) ≥ n', rotate, have H12 := H7 n'' H11, rotate 1, solve1 {norm_num at *, tautology }, rotate,
  -- use n'',
  -- rw generalites.valeur_absolue.theorem.majoration_valeur_absolue at H10,
  -- cases H10 with H14 H15,
  -- rw generalites.valeur_absolue.theorem.majoration_valeur_absolue at H12,
  -- cases H12 with H17 H18,
  -- linarith only [H18, H14, H2],
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
--   rw definitions.definition.limit,
-- rw definitions.definition.limit at H H',
-- intro ε, intro H1,
-- have H2 := H _ H1,
-- have H3 := H' _ H1,
-- cases H2 with n H4,
-- cases H3 with n' H5,
-- let x2 := max n n', have H7 : x2 = max n n', refl,
-- have H9 := @definitions.maximum.theorem.ppe_max_gauche,
-- have H10 := H9 n n',
-- -- norm_num at H10,
-- rw H7 at H10,
  todo,
  -- rw limit,
  -- intro ε, intro H1,
  -- rw limit at H H',
  -- have H2: ((ε/2):ℝ) > 0, rotate, have H3 := H (ε/2) H2, rotate 1, solve1 {linarith only [H1] }, rotate,
  -- have H4: ((ε/2):ℝ) > 0, rotate, have H5 := H' (ε/2) H4, rotate 1, solve1 {assumption}, rotate,
  -- cases H3 with n H6,
  -- cases H5 with n' H7,
  -- use max n n',
  -- intro n'', intro H8,
  -- have H9: (n'':ℕ) ≥ n, rotate, have H10 := H6 n'' H9, rotate 1, solve1 {norm_num at *, tautology }, rotate,
  -- have H11: (n'':ℕ) ≥ n', rotate, have H12 := H7 n'' H11, rotate 1, solve1 {norm_num at *, tautology }, rotate,
  
  -- rw generalites.valeur_absolue.theorem.majoration_valeur_absolue at H10 H12,
  -- rw generalites.valeur_absolue.theorem.majoration_valeur_absolue,
  -- cases H12 with Ha Hb, cases H10 with Hc Hd,
  -- split,
  -- linarith only [Ha, Hc],
  -- linarith only [Hb, Hc, Hd],
end

lemma exercise.limite_unique
(u : ℕ → ℝ) (l : ℝ)(l' : ℝ) (H : limit u l) (H' : limit u l') :
l = l' 
:=
/- dEAduction
PrettyName
  (*) Unicité de la limite
-/
begin
  -- by_contradiction,
  -- wlog Hll': l < l',
  -- -- exact lt_or_gt_of_ne a,
  -- rotate,
  -- set ε := (l'-l)/2 with Heps,
  -- have Hpos: ε >0, rotate, -- by compute1,
  -- specialize H ε Hpos, rotate 2,
  -- rotate,
  
  -- cases H with N1,
  -- specialize H' ε Hpos, cases H' with N2,
  -- set n := max N1 N2 with Hn,
  -- have HnsuppN1: n ≥ N1, from le_max_left N1 N2,
  -- have ineq1 := H_h n HnsuppN1,
  -- have HnsuppN2: n ≥ N2, from le_max_right N1 N2,
  -- have ineq1 := H'_h n HnsuppN2,

  -- -- sorry,  
  -- todo,
  -- todo,
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
  (**) Théorème des gendarmes
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
  -- have H2 := (H0 0) 1 _,
  -- rcases H2 with ⟨δ, H3, H4⟩,
  -- norm_num at H4,
  -- rw H1 at H4,
  -- use δ, split, rotate,
  -- intros x x_del,
  -- have H5 := H4 _ x_del,
  -- rw generalites.valeur_absolue.theorem.majoration_valeur_absolue at *,
  -- cases H5 with H5a H5b,
  -- linarith only [H5a], linarith, assumption,
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
  todo,
end


lemma exercise.composition_continuite (f: ℝ → ℝ) (g: ℝ → ℝ)
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

-- open definitions

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

-- definition increasing (k: ℕ → ℕ) : Prop := 
-- ∀ n, (k n) > (k (n+1)) 

-- definition limit_value (u: ℕ → ℝ) (a: ℝ) : Prop :=
-- ∃ k: ℕ → ℕ, increasing k ∧ limit (λ n, (u (k n))) a

-- lemma definition.increasing (k: ℕ → ℕ): (increasing k) ↔
-- ∀ n, (k n) > (k (n+1)) :=
-- begin
--   refl,
-- end

-- lemma theorem.increasing_limit (k: ℕ → ℕ) (H: increasing k):
-- limit_plus_infinity (coe k) :=
-- begin
--   todo,
-- end

-- lemma definition.limit_value (u: ℕ → ℝ) (a: ℝ) :
-- limit_value u a ↔
-- ∃ k: ℕ → ℕ, increasing k ∧ limit (λ n, (u (k n))) a :=
-- begin
--   refl,
-- end

-- lemma exercise.limit_limit_value
--  (u: ℕ → ℝ) (a b: ℝ) (H1: limit u a) (H2: limit_value u b) :
--  b = a :=
-- /- dEAduction
-- PrettyName
--   Une suite convergence a une unique valeur d'adhérence
-- -/
-- begin
--   todo,
-- end

lemma exercise.convergente_implique_cauchy (u: ℕ → ℝ): 
converging_seq u → cauchy u :=
/- dEAduction
PrettyName
  Une suite convergente est de Cauchy
-/
begin
  todo,
  -- intro H,
  -- rw converging_seq at H, cases H with x H,
  -- have H := limit (λ n, (u n)^2)  (x^2)
end

-- lemma theorem.cauchy_bounded (u: ℕ → ℝ): 
-- cauchy u → bounded_sequence u :=
-- /- dEAduction
-- PrettyName
--   Une suite de Cauchy est bornée
-- -/
-- begin
--   todo,
-- end

-- lemma theorem.bounded_limit_value (u: ℕ → ℝ): 
-- bounded_sequence u → ∃ a, limit_value u a :=
-- /- dEAduction
-- PrettyName
--   Une suite bornée a une valeur d'adhérence
-- -/
-- begin
--   todo,
-- end

-- lemma exercise.limit_value_cauchy_converge (u: ℕ → ℝ)
-- (H1: cauchy u) (H2: ∃ a, limit_value u a) :
-- converging_seq u  :=
-- /- dEAduction
-- PrettyName
--   Une suite de Cauchy ayant une valeur d'adhérence converge
-- -/
-- begin
--   todo,
-- end

-- lemma exercise.cauchy_converge (u: ℕ → ℝ)
-- (H1: cauchy u):
-- converging_seq u  :=
-- /- dEAduction
-- PrettyName
--   Toute suite de Cauchy converge
-- -/
-- begin
--   todo,
-- end

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