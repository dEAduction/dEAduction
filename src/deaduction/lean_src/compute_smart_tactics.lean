import data.real.basic
import tactic
import utils

open lean.parser tactic interactive
open interactive (loc.ns)
open interactive.types
open expr

open tactic.interactive
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
More additive lemmas
-/


-- lemma add_eq {X: Type} [has_add X] {a b c d: X} (H1: a=b) (H2: c=d): 
-- a + c = b + d :=
-- begin
--   congr, exact H1, exact H2,
-- end

-- lemma add_lt_eq {X: Type} [ordered_add_comm_monoid X] {a b c d: X} (H1: a=b) (H2: c < d): 
-- a + c < b + d :=
-- begin
--   todo
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
namespace tactic.interactive

meta def is_theorem : declaration → bool
| (declaration.defn _ _ _ _ _ _) := ff
| (declaration.thm _ _ _ _) := tt
| (declaration.cnst _ _ _ _) := ff
| (declaration.ax _ _ _) := tt


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
-- tactic.trace ("Got add theorems: " ++ to_string (nams.length)),
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
tactic.trace ("Try this: have " ++ to_string new_name ++ " := "
++ to_string nam ++ " " ++ to_string e1 ++ " " ++ to_string e2))
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


/-
Test and examples
-/

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
    -- smart_add z H1_lte with H104 --> fail
    smart_add H1_lt z with H104,

    -- Add a real number: ya pa plus simple ??
    set n:ℝ := 10.2, have Hn: n=10.2, refl,
    smart_add H1_lt n with H104,
    rw Hn at H104,
    sorry,
end

-- #print add_le_add


-- We could implement addition with equalities
-- (see commented add lemmas above)
-- example (H1: x = y) (H2: t=z): x+t = y + z :=
-- begin
--   smart_add H1 H2 with H3,
-- end



/-
Smart_com: apply all theorems whose name contains 'comm'
-/
-- def string.ends_with : string → string → bool 
-- | ⟨a⟩ ⟨b⟩ := list.starts_with a.reverse b.reverse

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


