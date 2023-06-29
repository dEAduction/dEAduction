import data.real.basic
import tactic
import real_definitions
import utils

-- #print linarith.make_comp_with_zero

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


----------------
---- Lemmas ----
----------------
namespace compute_lemmas
lemma ineq_from_non_eq {α: Type} [linear_order α] (a b : α) : ¬ a = b ↔ (a < b ∨ b < a) :=
begin
    todo
end

/- Unused? -/
lemma definition.useful_abs {α: Type} [decidable_linear_ordered_add_comm_group α] (a: α) :
abs a = if a ≥ 0 then a else -a :=
begin
    todo
end

end compute_lemmas

open compute_lemmas

--------------------------------------------------
--------------------------------------------------
-- Detecting abs, max, strict inequalities etc. --
--------------------------------------------------
--------------------------------------------------
namespace tactic.interactive
/- Just a front-end to trace, easy to desactivate. -/
meta def compute_trace  {α : Type} [has_to_tactic_format α] (a : α) : tactic unit := 
do trace"DEBUG:", trace a

/- Check if some expression contains some constant name inside app. -/
meta def contain_cst (cst_name: name) : expr → bool
| (const a a_1) := (a = cst_name)
| (app a a_1) := (contain_cst a) ∨ (contain_cst a_1)
| _ := ff

/- Check if some expression contains some constant name of a list. -/
meta def contain_csts : (list name) × expr → bool
| ([], _) := ff
| ((n :: tail), e) := if (contain_cst n e) then tt else (contain_csts (tail, e))

/- Check if expr contains abs inside app. -/
meta def contain_abs (e: expr) : tactic bool :=
return (contain_cst `abs e)

/- List of constants that will launch `develop_ite`in `compute_n`. -/
def cst_for_ite : list name := [`abs, `max, `min] -- TODO: move in compute.cfg

/- Check if expr contains abs inside app. -/
meta def contain_ite (e: expr) : tactic bool :=
return (contain_csts (cst_for_ite, e))

/- Detect abs in target in app. -/
meta def target_abs : tactic bool :=
do  target ← tactic.target, e ← infer_type target,
    b ← contain_abs target,
    -- tactic.trace b, 
    return b

/- Detect abs in target in app. -/
meta def target_ite : tactic bool :=
do  target ← tactic.target, e ← infer_type target,
    b ← contain_ite target,
    -- tactic.trace b, 
    return b

-- example : 0 < 1 + max 2 3 := begin target_ite, sorry end  -- tt
-- example : 0 < 1 + 2/3 := begin target_ite, sorry end  -- ff

/- Check if target is a strict inequality. -/
meta def target_lt_or_gt : tactic bool :=
do  target ← tactic.target,
    match target with
    | `(%%a < %%b) := -- do trace "1", 
        return tt
    | `(%%a > %%b) := -- do trace "2", 
        return tt
    | `(¬(%%a = %%b)) := -- do trace "3", 
        return tt
    | _ := -- do trace "4", 
        return ff
    end

---------------------------
---------------------------
-- Chaining tactic string -
---------------------------
---------------------------
-- set_option trace.linarith true
-- set_option trace.eqn_compiler.elim_match true

/- Concatenate a list of strings using commas as separators-/
def string.concatenate : (list string) → string
-- (l: list string) : string :=
-- list.foldl (λ (s: string) (t: string), s ++ ", " ++ t) "" l
| []  := ""
| [s] := s
| ("" :: tail) := string.concatenate tail
| (head :: tail) := do let tail_string := string.concatenate tail,
                    match tail_string with
                    | "" := head
                    | _  := head ++ ", " ++ tail_string
                    end


/- Try some (tactic string) and in case of success return its string.
Always succeed. -/
meta def try_and_return_code (my_tactic: tactic string) : tactic string :=
do {s ← my_tactic, return s} <|> return ""

meta def norm_num_and_return_code : tactic string := 
do `[norm_num at *, return "norm_num at *"] <|> return ""

/- Iterate some (tactic string) and return the concatenated returned strings.
Stops as soon as the tactic makes no progress,
i.e. returns the empty string or num_goals = 0.
Fail if some tactic fails. -/
meta def iterate_and_return_code : nat → tactic string → tactic string
| 0       my_tactic := return ""
| (n + 1) my_tactic := do -- trace "(iterating tactic...)",
    first_code ← my_tactic, l ← num_goals,
    match first_code, l with
    | "", _  := return ""
    | s, 0   := return s
    | _ , _  := do
        remaining_code ← iterate_and_return_code n my_tactic,
        return $ string.concatenate [first_code, remaining_code]
    end

/- Apply successively tactics in a given list,
but stop as soon as there is no more goal,
and return concatenation of returned code.
Fail if some tactic fails. -/
meta def and_then_and_return_code : list (tactic string) → tactic string 
| []                  := return ""
| (first_tac :: tail) :=  do
    first_code ← first_tac, l ← num_goals,
    match first_code, l with
    | s, 0   := return s
    | _ , _  := do
        remaining_code ← and_then_and_return_code tail,
        return $ string.concatenate [first_code, remaining_code]
    end

meta def or_else_and_return_code : list (tactic string) → tactic string
| [] := fail ""
| (head :: tail) := do head <|> or_else_and_return_code tail

/- Try some tactic to solve all current goals. If the tactic fails to solve some goal, then 
stop and fail. Otherwiser, return the list of successfull codes. -/
meta def solve_all_and_return_code (tac: tactic string) : tactic (string) :=
 do strings ← tactic.all_goals tac, return (string.concatenate strings)

meta def try_tactic_string (my_tac: tactic string) : tactic string :=
do {my_tac <|> return ""}

meta def skip_tactic_string : tactic string :=
do {skip, return ""}

/- Apply some tactic string and trace the returned string as effective code with id-/
meta def apply_and_trace_code (id: string) (my_tactic: tactic string) : tactic unit:=
do  effective_code ← my_tactic, 
    tactic.trace $ "EFFECTIVE CODE LEAN n°" ++ id ++ ":" ++ effective_code,
    tactic.trace $ "Try this: "++ effective_code


-------------------
-------------------
-- Pre-processing -
-------------------
-------------------
/- Series of tactic when target is a strict inequality, or contains abs / min / max. -/

lemma inv_pos_mpr {α : Type} [linear_ordered_field α] (a:α) :
0 < a → 0 < a⁻¹ := inv_pos.mpr

-- TODO: when target abs add  apply abs_pos_of_ne_zero, apply sub_ne_zero_of_ne, 

/- Unfold some definitions using if_then_else, then get rid of if_then_else by case reasoning.
Unfolded definitions includes abs, max, min. (Fails if there is nothing to unfold.) -/
meta def develop_ite : tactic string :=
    -- do ite ← target_ite, if ite then
        do  {`[unfold abs], `[unfold min max], `[split_ifs],
             compute_trace "develope ite, #goals = ", compute_trace num_goals,  -- for debugging
             return "unfold abs, unfold min max, split_ifs"}
       --  else return "COMPUTE DEBUG: (no if-then-else found)"

/- The same for all goals: more precisely, keep unfolding and splitting in any goal 
until there is nothing to unfold anymore. Always succeeds. -/
meta def develop_ite' : tactic string :=
    -- do ite ← target_ite, if ite then
        do  {`[repeat {any_goals {unfold abs, unfold min max, split_ifs}}],
             compute_trace "develope ite', #goals = ", compute_trace num_goals,  -- for debugging
             return "repeat {any_goals {unfold abs, unfold min max, split_ifs}}"}
       --  else return "COMPUTE DEBUG: (no if-then-else found)"

/- Split non-equalities `a≠b` into `a<b or b<a`, then split cases. -/
meta def develop_neq : tactic string :=
    -- do ineq ← target_lt_or_gt, if ineq then
        do {`[rw ineq_from_non_eq at *], `[cases_type* or],
            compute_trace "develope neq, #goals = ", compute_trace num_goals,  -- for debugging
            return "rw ineq_from_non_eq at *, cases_type* or"}
        -- else return "(target is not a strict inequality)"

meta def split_tacs : (bool × bool) → list (tactic string)
        | (tt, tt) := [develop_neq, develop_ite'] -- todo
        | (tt, ff) := [develop_neq]
        | (ff, tt) := [develop_ite]
        | (ff, ff) := []

meta def mk_tac_str : (name × string) → tactic string
| (n, s) := do {tactic.applyc ``n, return s}

-------------------
-------------------
-- Tactic compute -
-------------------
-------------------
/-- A configuration object for `compute1`. 
 develop_ite: set to tt to develop if_then_else definitions, e.g. abs and max.
 -/
meta structure compute_config : Type :=
(nb_iterations : nat := 1)
(develop_ite : bool := tt) -- unused
(develop_neq : bool := tt) -- unused
(ineq_tactics: list (name × string) := [(`mul_pos, "mul_pos"),
                                        (`inv_pos_mpr, "inv_pos.mpr"),
                                        (`mul_ne_zero, "mul_ne_zero")])

open linarith
/- Non-interactive version of nl_linarith. -/
meta def nl_linarith (cfg : linarith_config := {}): tactic unit :=
do
{
tactic.linarith false false []
  { cfg with preprocessors := some $
      cfg.preprocessors.get_or_else default_preprocessors ++ [nlinarith_extras] }
}


/- Try assumption, tautology, linarith, nl_linarith. -/
meta def compute1 : tactic string :=
do compute_trace "(compute1...)",
do {   do {assumption, return "assumption"}
    <|>
    -- solve e.g. "n_0 ≤ n_0 ∨ n_0 ≤ n_1"
    -- with norm_num, solves "n_0 ≤ max n_0 n_1"
    do {tactic.tautology, return "tautology"}
    <|>
    do {tactic.linarith false false [], return "linarith"}
    <|>
    do {nl_linarith, return "nl_linarith"}
}

/- Repeat n times the tactic compute1, inserting various strategies according to
whether
            -- target is a stric inequality, and 
            -- contains ite expr (`abs`, `max`, and so on).
Always start with linarith before splitting.
-/
meta def compute_n  (cfg: compute_config := {}) : tactic string :=
    do  t_ineq ← target_lt_or_gt, t_abs ← target_ite, match (t_ineq, t_abs) with
        | (ff, ff) := do compute_trace "Target is NOT a strict inequality and does NOT contain ite",
            compute1 -- nothing more to try here (?)
        | (ff, tt) := do compute_trace "Target is NOT a strict inequality but contains ite",
        -- Essentially unfold def and split if_then_else, then re-try linarith
            let ite_tacs :=
                and_then_and_return_code [develop_ite,
                                          (solve_all_and_return_code compute1)] 
            in or_else_and_return_code [compute1, ite_tacs]
        | (tt, ff) := do compute_trace "Target is a strict inequality but does NOT contain ite",
        -- Essentially try successively specific tactics on the target and linarith
            let ineq_tacs_1 := 
                iterate_and_return_code cfg.nb_iterations $ or_else_and_return_code $
                    (cfg.ineq_tactics.map mk_tac_str) ++ [compute1]
            -- if this fails then split non_equalities
            in let ineq_tacs_2 := 
                and_then_and_return_code [develop_neq, (solve_all_and_return_code compute1)]
            in or_else_and_return_code [compute1, ineq_tacs_1, ineq_tacs_2]
        | (tt, tt) := do compute_trace "Target is a strict inequality and contains ite",
            let ineq_tacs_1 := 
                iterate_and_return_code cfg.nb_iterations $ or_else_and_return_code $
                    (cfg.ineq_tactics.map mk_tac_str) ++ [compute1]
            -- if this fails then split non_equalities
            in let ineq_tacs_2 := 
                and_then_and_return_code [try_and_return_code develop_neq, develop_ite', (solve_all_and_return_code compute1)]
            in or_else_and_return_code [compute1, ineq_tacs_1, ineq_tacs_2]
        end

/- Apply norm_num at * if possible, then the compute_n tactic n times,
and in case of success trace the effective code with id. -/
meta def compute_and_trace_code (id: string)  (cfg: compute_config := {}):
tactic unit := let tacs := [norm_num_and_return_code, (tactic.interactive.compute_n cfg)] in 
do apply_and_trace_code id (and_then_and_return_code tacs)



-- Additive lemmas:
  -- norm_num at *,
  -- < < exact add_lt_add H1 H2,
  -- < <= exact add_lt_add_of_lt_of_le H1 H2,
  -- <= < exact add_lt_add_of_le_of_lt H1 H2,
  -- <= <= exact add_le_add H1 H2,
  -- = = exact congr (congr_arg has_add.add H1) H2,
  -- < +cst exact add_lt_add_right H1 z,
  -- exact add_comm z x


-- Comm lemmas
  -- exact add_comm z x,
  -- exact mul_comm z x,
  -- exact set.inter_comm A B,


-- Simplification:
--  Cancel lemmas...


-- meta def add_ineq (e: expr) (e': expr) : tactic unit :=
-- match (e,e) with
-- | (`(%%a ≤ %%b) , `(%%a' ≤ %%b')) := have H := a + a' < b + b', by exact add_lt_add H1 H2
-- | _ := assumption
-- end


/- 
----------------------------------------------------------
----------------------------------------------------------
|| Tactic smart_add.
|| Get all theorems whose name start with "add",
|| and try to apply them to two properties.
----------------------------------------------------------
----------------------------------------------------------
-/
meta def is_theorem : declaration → bool
| (declaration.defn _ _ _ _ _ _) := ff
| (declaration.thm _ _ _ _) := tt
| (declaration.cnst _ _ _ _) := ff
| (declaration.ax _ _ _) := tt


/-
list.starts_with. We restric to (list char)
since we need a type for which equality is decidable.
-/
def list.starts_with : (list char) → (list char) → bool 
| a [] := tt
| [] b := ff
| (h::t) (h'::t') := 
    (if h = h' then list.starts_with t t' else ff) 


-- set_option trace.eqn_compiler.elim_match true
def string.starts_with : string → string → bool 
| ⟨a⟩ ⟨b⟩ := list.starts_with a b

open name 
def name.suffix_starts_with : name → string →  bool
| anonymous _ := ff
| (mk_string s n) p := string.starts_with s p
| (mk_numeral s n ) _ := ff

meta def is_add_lemma (decl: declaration) : bool :=
do let nam := decl.to_name in name.suffix_starts_with nam "add"


meta def get_all_add_theorems : tactic (list name) :=
do
env ← tactic.get_env,
pure (environment.fold env [] (λ decl nams,
if is_theorem decl && is_add_lemma decl then
 declaration.to_name decl :: nams else nams))

meta def trace_add_theorems : tactic (list unit) :=
do
nams ←  get_all_add_theorems,
tactic.trace ("Got add theorems: " ++ to_string (nams.length)),
nams.mmap (λ nam, tactic.trace (to_string nam))

-- run_cmd trace_add_theorems

/-
Apply the theorem whose name is nam to expr e1 and e2,
and name the resulting property new_name.
-/
meta def have_with_name (nam: name) (e1 e2 : expr) 
(new_name: name): tactic unit :=
do 
p ← resolve_name nam,
 «have» new_name none ``(%%p %%e1 %%e2)

/-
Successively try to apply all the theorems with name in list names to expr e1 and e2,
and name the resulting property h. Stop at first success.
-/
meta def try_thm (names: list name) (e1 e2 : expr)  (new_name: name)
: tactic unit :=
list.mfirst (λ nam,
do
have_with_name nam e1 e2 new_name, no_meta_vars,
tactic.trace ("Success with thm " ++ to_string nam))
names

/- Smart_add:
Successively try to apply all the theorems whose name starts with "add",
 to expr e1 and e2, and name the resulting property h.
 Stop at first success.
-/
open tactic.interactive
open lean.parser (tk)

meta def smart_add (h1 : parse ident) (h2 : parse ident)
(h : parse (tk "with" *> ident)) : tactic unit :=
do names ←  get_all_add_theorems,
   e1 ← get_local h1,
   e2 ← get_local h2,
    try_thm names e1 e2 h


/-Examples-/
variables x y z t: real
example (H1_lt: x < y) (H2_lt: t < z)
(H1_lte: x ≤ y) (H2_lte: t ≤ z)
:
true :=
begin
--   have H3 := add_lt_add_of_lt_of_le H1 H2,
    smart_add H1_lt H2_lt with H100,
    smart_add H1_lte H2_lte with H101,
    smart_add H1_lte H2_lt with H102a,
    smart_add H1_lt H2_lte with H102b,
    smart_add H1_lte z with H103,
    -- Add a real number: ya pa plus simple ??
    set n:ℝ := 10, have Hn: n=10, refl,
    smart_add H1_lt n with H104,
    rw Hn at H104,
    todo
end


/- Smart_com: apply all theorems whose name
-/
def string.ends_with : string → string → bool 
| ⟨a⟩ ⟨b⟩ := list.starts_with a.reverse b.reverse

open name 
def name.suffix_ends_with : name → string →  bool
| anonymous _ := ff
| (mk_string s n) p := string.ends_with s p
| (mk_numeral s n ) _ := ff

meta def is_comm_lemma (decl: declaration) : bool :=
do let nam := decl.to_name in name.suffix_ends_with nam "comm"


meta def get_all_comm_theorems : tactic (list name) :=
do
env ← tactic.get_env,
pure (environment.fold env [] (λ decl nams,
if is_theorem decl && is_comm_lemma decl 
&& not (to_string (declaration.to_name decl) = "eq_comm") 
then declaration.to_name decl :: nams else nams))

meta def trace_comm_theorems : tactic (list unit) :=
do
nams ←  get_all_comm_theorems,
tactic.trace ("Got comm theorems: " ++ to_string (nams.length)),
nams.mmap (λ nam, tactic.trace (to_string nam))

run_cmd trace_comm_theorems

/-
Rewrite expr e1 using theorem whose name is nam.
-/
meta def rw_with_name (nam: name) (e1 : expr) 
: tactic unit :=
do 
-- p ← resolve_name nam,
-- e ← to_expr p,
e ← mk_const nam, rewrite_hyp e e1, skip

/-
Successively try to apply all the theorems with name in list names to expr e1 and e2,
and name the resulting property h. Stop at first success.
-/
meta def rw_with_thm (names: list name) (e1 : expr): tactic unit :=
list.mfirst (λ nam,
do
rw_with_name nam e1, no_meta_vars,
tactic.trace ("Success with thm " ++ to_string nam))
names

/- Smart_comm:
Successively try to rw expr using all the theorems whose name ends with "comm".
 Stop at first success.
-/
open tactic.interactive
open lean.parser (tk)

-- TODO: smart_comm on target
--  try eq_comm but only at end
meta def smart_comm (h1 : parse ident) : tactic unit :=
do names ←  get_all_comm_theorems, tactic.trace "Got thms",
   e1 ← get_local h1, tactic.trace "Got h1",
    rw_with_thm names e1


example (H1: x=y) (H2: z=t)
(H3 : ∀ a, x + a = y + a):
∀ a, x + a = y + a :=
begin
    -- exact congr_fun (congr_arg has_add.add H1) t
    -- conv {congr, skip, rw add_comm},
    -- smart_comm H1,
    -- NON : simp_rw add_comm,
    -- NON : conv in (x+_) {simp_rw add_comm }
    sorry
end

example (H1: (x+y)*z = (x*y)+t+ (x+y)) : true :=
begin
    -- have H1b : (x+y)*z = (y+x)*z,
    --     {ring},
    --     rw H1b at H1,
        -- {have Hcomm := add_comm x y,
        -- rw Hcomm at H1}, 

    have H1': (y+x)*z = (x*y)+t+ (x+y),
    simp only [add_comm, H1], clear H1, rename H1' H1,
    
    
end


/-conv.smart_comm-/




end tactic.interactive


