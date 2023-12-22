import data.real.basic
import tactic
import utils
import compute_smart_tactics2

open lean.parser tactic interactive
open interactive (loc.ns)
open interactive.types
open expr
-- import compute_smart_tactics2

/-
Triangular inequality lemmas.
-/

universe u
variables {X: Type u} [decidable_linear_ordered_comm_ring X]

lemma triangular_inequality :
∀ x y : X, abs (x + y) ≤ abs x + abs y
:= 
begin
  exact abs_add,
end

lemma triangular_inequality_minus :
∀ x y : X, abs (x - y) ≤ abs x + abs y
:= 
begin
  intros x y,
  have H := triangular_inequality x (-y),
  norm_num at *,
  simp only [tactic.ring.add_neg_eq_sub] at H,
  assumption,
end

/-
----------------------------------
Tactic smart_triangular_inequality.
----------------------------------
-/
-- open lean.parser tactic interactive
-- open interactive (loc.ns)
-- open interactive.types
-- open expr
-- open name


namespace tactic.interactive
open name


/-
Apply a given theorem to expr e1 and e2,
and name the resulting property new_name.
-/
meta def have_with_string_name (lemma_name: string) (e1 e2 : expr) 
(new_name: name): tactic unit := do
-- trace $ "Applying " ++ lemma_name,
-- let nam := (mk_simple_name lemma_name) in
have_with_name (mk_simple_name lemma_name) e1 e2 new_name --,
-- trace "done"


/-
Apply_triangular_inequality apply one of the two above lemma to given expressions.
-/
private meta def apply_triangular_inequality (x y: expr) (minus: bool) (new_name: name):
tactic unit :=
match minus with
| ff := do tactic.trace 
("Try this: have " ++ to_string new_name ++ " := " ++ 
"triangular_inequality (" ++ to_string x ++ ") (" ++ to_string y ++ ")"),
        have_with_string_name "triangular_inequality" x y new_name
| tt :=  do tactic.trace 
("Try this: have " ++ to_string new_name ++ " := " ++ 
"triangular_inequality_minus (" ++ to_string x ++ ") (" ++ to_string y ++ ")"),
        have_with_string_name "triangular_inequality_minus" x y new_name
end

/-
Recursively search for a sub-expression to which it is pertinent to apply
trangular inequality, and get a new inequality called <new_name> (or fail).
Namely, we look for
- sum or diff of abs, or
- abs of sum or diff.
Only pertinent sides of inequalities are tried.
-/

-- Find an upper bound from triang ineq
private meta def upper_bound_from_triang_ineq (new_name: name) (e: expr) : tactic unit
:= match e with 
| `(abs (%%x + %%y)) :=
do apply_triangular_inequality x y ff new_name
| `(abs (%%x - %%y)) :=
do apply_triangular_inequality x y tt new_name
| _ := fail "(No upper bound found)"
end

-- Find a lower bound from triang ineq
private meta def lower_bound_from_triang_ineq (new_name: name) (e: expr) : tactic unit
:= match e with 
| `((abs %%x) + (abs %%y)) := 
do (apply_triangular_inequality x y ff new_name)
| _ := fail "(No lower bound found)"
end

/- 
Try triangular inequality on expr or immediate pertinent sub-expr.
-/
private meta def try_triang_ineq (new_name: name) (e: expr) (on_target: bool):
tactic unit := match e with
|  `(%%A < %%B) := 
if on_target then do --trace "Found inequality",
  lower_bound_from_triang_ineq new_name A  <|>
  upper_bound_from_triang_ineq new_name B
else  do --trace "Found inequality",
  lower_bound_from_triang_ineq new_name B  <|>
  upper_bound_from_triang_ineq new_name A
|  `(%%A ≤ %%B) := 
if on_target then do --trace "Found inequality",
  lower_bound_from_triang_ineq new_name A <|>
  upper_bound_from_triang_ineq new_name B
else do --trace "Found inequality",
  lower_bound_from_triang_ineq new_name B <|>
  upper_bound_from_triang_ineq new_name A
| _ := do -- trace $ "No inequality found in " ++ to_string e,
  lower_bound_from_triang_ineq new_name e <|>
  upper_bound_from_triang_ineq new_name e
end


-- Immediate pertinent sub-exprs of an expr
private meta def sub_expr (e: expr) : tactic (list expr)
:= 
match e with 
| (app fonction argument) := return [fonction, argument]
| _ := return []
end

-- Immediate pertinent sub-exprs of a list of exprs
private meta def sub_expr_from_list: list expr →  tactic (list expr)
| (head :: tail) := do
L1 ← (sub_expr head),
L2 ← sub_expr_from_list tail,
return $ list.append L1 L2
| list.nil := return []

/- 
Try triangular inequality on a list of exprs.
-/
private meta def try_triang_ineq_on_list (on_target: bool):
name × list expr → tactic unit
| (new_name, (head :: tail)) := try_triang_ineq new_name head on_target
<|> (try_triang_ineq_on_list (new_name, tail))
| (_, []) := fail ""


meta def rec_triang_ineq (on_target: bool): (name × list expr) →  tactic unit
| (new_name, L) := match L with 
  | (head :: tail) :=
  -- First try triangular ineq on expr
  try_triang_ineq new_name head on_target <|> do 
  try_triang_ineq_on_list on_target (new_name, tail) <|> do 
  -- and in case of failure, on sub-expressions.
  L' ← sub_expr_from_list L, rec_triang_ineq (new_name, L')
  | list.nil := fail ""
    end


/- 
smart_triang_ineq: apply the triangular inequality
to the first pertinent sub-expression found in h.
Inequalities must be normalised!
-/
meta def smart_triang_ineq (h : parse ident) 
(nam : parse (tk "with" *> ident)) : tactic unit :=
do e ← get_local h, 
e_type ← infer_type e,
rec_triang_ineq ff (nam, [e_type])
<|> fail ("No absolute value found in " ++ to_string e)

meta def smart_triang_ineq_on_target 
(nam : parse (tk "with" *> ident)) : tactic unit :=
do (head :: _) ← get_goals, 
e_type ← infer_type head,
rec_triang_ineq tt (nam, [e_type])
<|> fail ("No absolute value found in target")

end tactic.interactive


/-
TESTS.
-/

example (a b: ℝ) (H: 1 < abs(a - b ) +2 ) : 1 < abs a + abs b + 2 :=
begin
  -- smart_triang_ineq_on_target with H1,
  -- linarith
  todo
end

-- example (a b: ℝ) (H: abs a + abs b < 1 ) : abs(a + b) < 1 :=
-- begin
--   smart_triang_ineq H with H1,
--   linarith,
-- end




