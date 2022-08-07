import data.real.basic
import tactic
import real_definitions
import utils



namespace tactic.interactive
open lean.parser tactic interactive
open interactive (loc.ns)
open interactive.types
open expr


-- useful lemmas:
-- ge_iff_le
-- gt_iff_lt
-- lt_of_le_of_ne
-- le_of_lt
-- div_pos
-- mul_pos
-- inv_pos

open tactic.interactive

-------------------------------------------
-------------------------------------------
-- Make 'a < b' from 'a ≠ b' and 'a ≤ b' --
-------------------------------------------
-------------------------------------------
-- This is achieved by the following sequence of tactics:
-- * make_ineq  take "a ≤ b" and "a' ≠ b'" and try to make "a < b"
-- * extract_gt extract the list of inequalities "a ≤ b" from a list of expressions
-- * extract_non_eq does the same for "a ≠ b"
-- * list_prod make the product list of two lists
-- * get_pos_from_pos_eq_from_list is build on the previous ones:
-- it takes a list of expressions,
-- extract inequalities and non-equalities,
-- take all pairs and try to make "a < b" by applying make_ineq
-- * get_pos_from_pos_eq is an interactive tactic that applies this to the local context

meta def make_ineq : expr × expr × expr → expr × expr × expr → tactic unit
/-  Take H1 of type "a ≤ b", H2 of type "a' ≠ b'", and if a=a' and b = b'
    then add H3 of type "a < b" in the local context -/
| (H1, a, b) (H2, a', b') :=
    tactic.unify a a' >> tactic.unify b b' >> do
    {
    H ← mk_fresh_name,
    «have» H none ``(lt_of_le_of_ne %%H1 %%H2),
    tactic.trace("EFFECTIVE LEAN CODE: have H := lt_of_le_of_ne " ++ to_string H1 ++ " " ++ to_string H1)
    }
    <|>
    tactic.unify a b' >> tactic.unify a' b >> do
    {
    H ← mk_fresh_name,
    «have» H none ``(lt_of_le_of_ne %%H1 (ne.symm %%H2)),
    tactic.trace("EFFECTIVE LEAN CODE: have H := lt_of_le_of_ne " ++ to_string H1 ++ " (ne.symm " ++ to_string H2 ++ ")")
    }
    <|>
    skip

meta def make_ineq' : expr → expr → tactic unit
/- The same, but remove H1 and H2 from context
  TODO
  -/
| H1 H2 := do skip

meta def extract_gt : list expr → tactic (list (expr × expr × expr))
/- Extract from list of expr the couples (H, a,b)
where the expr H of type "a ≤ b" in is the list -/
-- match hypos with
| []                    := return []
| (hypo :: less_hypos)  := do
    {
    ineq ← infer_type hypo,
    remaining_list ← (extract_gt less_hypos),
    match ineq with
        | `(%%a ≤ %%b)  := return $ (hypo, a, b) :: remaining_list
        | _             := return $ remaining_list
        end
    }

meta def extract_non_eq : list expr → tactic (list (expr × expr × expr))
/- Extract from list of expr the couples (H, a,b)
where the expr H of type "a ≠ b" in is the list -/
-- match hypos with
| []                    := return []
| (hypo :: less_hypos)  := do
    {
    ineq ← infer_type hypo,
    remaining_list ← (extract_non_eq less_hypos),
    match ineq with
        | `(%%a ≠ %%b)      := return $ (hypo, a, b) :: remaining_list
        | `(¬ %%a = %%b)    := return $ (hypo, a, b) :: remaining_list
        | _                 := return $ remaining_list
        end
    }


meta def list_prod {α β : Type} : list α → list β → list (α × β)
/- Return the product list -/
| []    l2                  := []
| l1    []                  := []
| (h1 :: l1)  (h2 :: l2)    :=
    (h1, h2) ::
    append  (append (list_prod [h1] l2)
                    (list_prod l1 [h2]))
            (list_prod l1 l2)


meta def get_pos_from_pos_eq_from_list (hypos: list expr) : tactic unit :=
do
{
    inequalities    ← extract_gt hypos,     -- tactic.trace inequalities,
    equalities      ← extract_non_eq hypos, -- tactic.trace equalities,
    -- take all pairs and try to build " a < b "
    (list_prod inequalities equalities).mmap (λh, make_ineq h.1 h.2),
    return ()
}

meta def get_pos_from_pos_eq : tactic unit :=
/- To be applied after "norm_num at *"
    This tactic search in the hypotheses for two hypotheses of the for
    a ≤ b  and a ≠ b
    and deduces
    a < b
-/
do
{
hypos ← tactic.local_context,
get_pos_from_pos_eq_from_list hypos
}


-------------------
-------------------
-- Tactic compute -
-------------------
-------------------

lemma inv_pos_mpr {α : Type} [linear_ordered_field α] (a:α) :
0 < a → 0 < a⁻¹ := inv_pos.mpr

open linarith
meta def nl_linarith (cfg : linarith_config := {}): tactic unit :=
do
{
tactic.linarith false false []
  { cfg with preprocessors := some $
      cfg.preprocessors.get_or_else default_preprocessors ++ [nlinarith_extras] }
}


meta def compute1 : tactic unit :=
/- try several computing tactics for STRICT inequalities -/
do
{
    do {assumption, tactic.trace "EFFECTIVE LEAN CODE: assumption"}
    <|>
    -- solve e.g. "n_0 ≤ n_0 ∨ n_0 ≤ n_1"
    -- with norm_num, solves "n_0 ≤ max n_0 n_1"
    do {tactic.tautology, tactic.trace "EFFECTIVE LEAN CODE: tautology"}
    <|>
    do {nl_linarith, tactic.trace "EFFECTIVE LEAN CODE: nl_linarith"}
    <|>
    do {tactic.applyc ``mul_pos, tactic.trace "EFFECTIVE LEAN CODE: apply mul_pos"}
    <|>
    -- a>0 → a⁻¹ >0
    do {tactic.applyc ``inv_pos_mpr, tactic.trace "EFFECTIVE LEAN CODE: apply inv_pos.mpr"}
    <|>
 -- a≠0 → b≠0 → ab≠0
     do {tactic.applyc ``mul_ne_zero, tactic.trace "EFFECTIVE LEAN CODE: apply mul_ne_zero"}
--  div_pos is now useless
}

meta def compute_n (n: nat): tactic unit :=
/- Repeat n times the tactic compute1 ; never fails -/
do
{
    get_pos_from_pos_eq, -- try to add strict inequalities to the context
    tactic.iterate_exactly' n (tactic.try (compute1))
}


end tactic.interactive
