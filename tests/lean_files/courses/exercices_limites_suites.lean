import tactic
import data.real.basic
/-
- nom des variables dans la def de limit !
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
import compute3

-- dEAduction definitions
-- import set_definitions
import real_definitions


local attribute [instance] classical.prop_decidable


/-- `l` is the limit of the sequence `a` of reals -/
definition limit (u : ℕ → ℝ) (l : ℝ) : Prop :=
∀ ε > 0, ∃ N, ∀ n ≥ N, | u n - l | < ε

definition convergent (u : ℕ → ℝ) : Prop :=
∃ l, limit u l

definition limit_plus_infinity (u : ℕ → ℝ) : Prop :=
∀ M, ∃ N, ∀ n ≥ N, u n > M

definition bounded_sequence (u : ℕ → ℝ) : Prop :=
∃ M, ∀ n, | u n | ≤ M

definition even (n:ℕ) : Prop := ∃ n', n=2 * n'



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

lemma definition.even (n:ℕ) : even n ↔ ∃ n', n = 2 * n'
:=
/- dEAduction
PrettyName
  Entier naturel pair
-/
begin
   refl
end

----------------------------------
namespace maximum

lemma theorem.ppe_max_gauche : ∀ a b : ℝ, a ≤ max a b :=
begin
  intros a b,
  exact le_max_left a b,
end

lemma theorem.ppe_max_droite : ∀ a b : ℝ,  b ≤ max a b :=
begin
  intros a b,
  exact le_max_right a b,
end

lemma theorem.max_ppe (a b c : ℝ) (Ha: a ≤ c) (Hb: b ≤ c) : max a b ≤ c :=
begin
  exact max_le Ha Hb,
end

lemma theorem.max_pp (a b c : ℝ) (Ha: a < c) (Hb: b < c) : max a b < c :=
begin
  exact max_lt Ha Hb,
end

end maximum

namespace valeur_absolue

lemma theorem.valeur_absolue
(x : ℝ) : 
((0 ≤ x) → (|x| = x)) and ((x ≤ 0) → (|x| = -x)) :=
begin
  split, exact abs_of_nonneg, exact abs_of_nonpos,
end

lemma theorem.majoration_valeur_absolue
(x : ℝ) (r : ℝ) :
(|x| < r) ↔ ((-r < x) ∧ (x < r))
:= 
/- dEAduction
PrettyName
  Majoration d'une valeur absolue
-/
begin
  exact abs_lt
end


lemma theorem.inegalite_triangulaire 
(x : ℝ) (y : ℝ) : |x + y| ≤ |x| + |y|
:= 
/- dEAduction
PrettyName
  Inégalité triangulaire
-/
begin
  exact abs_add x y 
end

lemma theorem.valeur_absolue_produit
(x : ℝ) (y : ℝ) : |x * y| = |x| * |y|
:= 
/- dEAduction
PrettyName
  Valeur absolue d'un produit
-/
begin
  exact abs_mul x y 
end

end valeur_absolue

------------------------------
-- Définitions de la limit --
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

lemma definition.convergent
{u : ℕ → ℝ} :
(convergent u) ↔ 
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
{u : ℕ → ℝ} {l : ℝ} :
(limit_plus_infinity u) ↔ 
∀ M, ∃ N, ∀ n ≥ N, u n > M
:= 
/- dEAduction
PrettyName
  Limite infinie d'une suite
ImplicitUse
  True
-/
begin
  refl
end

lemma definition.bounded 
{u : ℕ → ℝ} :
(bounded_sequence u) ↔ 
∃ M, ∀ n, | u n | ≤ M
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


end definitions


namespace tests

lemma exercise.test_compute
:
0 ≤ 1 ∧ 2+2 = 4
:=
begin
  split,
  {compute_and_trace_code "1"},
  {compute_and_trace_code "1"},
end

lemma exercise.test_compute_2
(a: ℝ) (H: a >0):
(a +1 > 1)
:=
begin
  todo
end

lemma exercise.test_compute_3
(a: ℝ) (H: 0 ≤ a) (H': a ≠ 0):
(a +1 > 1)
:=
begin
  todo
end

end tests


-----------------
--  exercices  --
-----------------
namespace exercices
open definitions

--------------------------------------------------
namespace examples

lemma exercise.ex_non_cv :
¬ (convergent (λ n, (-1)^n))
:=
/- dEAduction
PrettyName
  Un exemple de suite non convergent
-/
begin
  todo
end

lemma exercise.ex_cv :
convergent (λ n, (1/n^2))
:=
/- dEAduction
PrettyName
  Un exemple de suite convergent
-/
begin
  todo
end

lemma exercise.ex_dv :
limit_plus_infinity (λ n, (real.sqrt (n+2)))
:=
/- dEAduction
PrettyName
  Un exemple de suite divergente
-/
begin
  todo
end




lemma exercise.limit_constante 
(u : ℕ → ℝ) (c : ℝ) (H : ∀ n, u n = c) :
limit u c :=
/- dEAduction
PrettyName
  La limit d'une suite constante
-/
begin
--   rw definition.limit,
--   intros ε Hε,
--   use 0,
--   intros n H1,
--   rw H,
-- `[ solve1 {norm_num at * }, trace "EFFECTIVE CODE n°4.0"] <|> `[ `[ norm_num at *, trace "EFFECTIVE CODE n°5.0"] <|> `[ skip, trace "EFFECTIVE CODE n°5.1"], compute_n 10, trace "EFFECTIVE CODE n°4.1"],
  todo
end

end examples

-------------------------------------------------
namespace premieres_proprietes
/- dEAduction
PrettyName
  Première propriétés
-/

lemma exercise.limit_unique
(u : ℕ → ℝ) (l : ℝ)(l' : ℝ) (H : limit u l) (H' : limit u l') :
l = l' 
:=
/- dEAduction
PrettyName
  Unicité de la limit
-/
begin
  -- by_contradiction,
  -- wlog Hll': l < l',
  -- exact lt_or_gt_of_ne a,
  -- set ε := (l'-l)/2 with Heps,
  -- have Hpos: ε >0, by compute1,
  -- specialize H ε Hpos, cases H with N1,
  -- specialize H' ε Hpos, cases H' with N2,
  -- set n := max N1 N2 with Hn,
  -- have HnsuppN1: n ≥ N1, from le_max_left N1 N2,
  -- have ineq1 := H_h n HnsuppN1,
  -- have HnsuppN2: n ≥ N2, from le_max_right N1 N2,
  -- have ineq1 := H'_h n HnsuppN2,

  -- sorry,  
  todo
end


lemma exercise.def_alt
(u : ℕ → ℝ) (l : ℝ) :
(limit u l) ↔ 
∀ ε > 0, ∃ N, ∀ n ≥ N, | u n - l | ≤ ε
:=
/- dEAduction
PrettyName
  Définition alternative de la limit
-/
begin
  todo
end


lemma definition.limit_infinity_alt
{u : ℕ → ℝ} {l : ℝ} :
(limit_plus_infinity u) ↔ 
∀ M>0, ∃ N, ∀ n ≥ N, u n > M
:= 
/- dEAduction
PrettyName
  Définition alternative pour une limit infinie
-/
begin
  todo
end












end premieres_proprietes


namespace proprietes
/- dEAduction
PrettyName
  Propriétés
-/

lemma exercise.limit_somme
(u u': ℕ → ℝ) (l l' : ℝ) (H : limit u l)
(H' : limit u' l') :
limit (λn, u n + u' n) (l+l')
:=
/- dEAduction
PrettyName
  Limite d'une somme
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
  todo
end


-- preuve par DL ?
lemma exercise.limit_produit
(u u': ℕ → ℝ) (l l' : ℝ) (H : limit u l)
(H' : limit u' l') :
limit (λn, (u n) * (u' n)) (l*l')
:=
/- dEAduction
PrettyName
  Limite d'un produit
-/
begin
  todo
end

lemma exercise.limit_inegalites
(u u': ℕ → ℝ) (l l' : ℝ) (H : limit u l)
(H' : limit u' l')
(H'' : ∀n, u n ≤ u' n ) :
l ≤ l'
:=
/- dEAduction
PrettyName
  Passage à la limit dans une inégalité
-/
begin
  todo
end

lemma exercise.gendarmes
(u u' v  : ℕ → ℝ) (l : ℝ) 
(H : limit u l) (H' : limit u' l)
(H'' : ∀n, (((u n) ≤ v n) and ((v n) ≤ u' n))) :
limit v l
:=
/- dEAduction
PrettyName
  Théorème des gendarmes
-/
begin
  todo
end




-- Let's make a new definition.
definition is_bounded (a : ℕ → ℝ) := ∃ B, ∀ n, |a n| ≤ B

-- Now try this:
lemma tendsto_bounded_mul_zero {a : ℕ → ℝ} {b : ℕ → ℝ}
  (hA : is_bounded a) (hB : limit b 0) 
  : limit (λ n, (a n) * (b n)) 0 :=
begin
  todo,
end

end proprietes

end exercices



end course