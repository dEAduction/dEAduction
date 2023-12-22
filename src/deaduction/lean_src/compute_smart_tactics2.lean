import data.real.basic
import tactic
import utils

open lean.parser tactic interactive
open interactive (loc.ns)
open interactive.types
open expr

-- open tactic.interactive
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

-- #print add_le_add_left

-- lemma add_le_add_left2

-- TODO: variations on the following:
universe u
variable {α : Type u}
variables [ordered_cancel_comm_monoid α] {a b c d : α}
@[to_additive]
lemma mul_le_mul_left2 : ∀ {a b : α} (c : α) (h : a ≤ b), c * a ≤ c * b :=
begin
    intros a b c h,
    exact mul_le_mul_left'' h c,
end


lemma add_eq {X: Type} [has_add X] {a b c d: X} (H1: a=b) (H2: c=d): 
a + c = b + d :=
begin
  congr, exact H1, exact H2,
end

lemma add_eq_lt {X: Type} [ordered_add_comm_monoid X] {a b c d: X} (H1: a=b) (H2: c < d): 
a + c < b + d :=
begin
  todo
end

lemma add_lt_eq {X: Type} [ordered_add_comm_monoid X] {a b c d: X} (H1: a<b) (H2: c = d): 
a + c < b + d :=
begin
  todo
end

lemma add_eq_le {X: Type} [ordered_add_comm_monoid X] {a b c d: X} (H1: a=b) (H2: c ≤ d): 
a + c ≤ b + d :=
begin
  todo
end

lemma add_le_eq {X: Type} [ordered_add_comm_monoid X] {a b c d: X} (H1: a ≤ b) (H2: c = d): 
a + c ≤ b + d :=
begin
  todo
end

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


open name 

def name.suffix_starts_with : name → string →  bool
| anonymous _ := ff
| (mk_string s n) p := string.starts_with s p
| (mk_numeral s n ) _ := ff


/-
Test if a given lemma has a name that starts with a given prefix.
-/
meta def lemma_name_starts_with (decl: declaration) (subname: string) : bool :=
do let nam := decl.to_name in name.suffix_starts_with nam subname


/-
Get all the lemmas whose name starts with a given prefix.
-/
meta def get_all_theorems_whose_name_starts_with (subname: string) :
tactic (list name) :=
do
env ← tactic.get_env,
pure (environment.fold env [] (λ decl nams,
if is_theorem decl && (lemma_name_starts_with decl subname) then
 declaration.to_name decl :: nams else nams))

/-
Debug: print all thms given by previous tactic.
-/
meta def trace_theorems (subname: string) : tactic (list unit) :=
do
nams ←  get_all_theorems_whose_name_starts_with subname,
nams.mmap (λ nam, tactic.trace (to_string nam))


-- run_cmd trace_theorems "assoc"
-- #check mul_lt_mul_of_pos_left


namespace tactic.interactive

/-
Apply a given theorem to expr e1 and e2,
and name the resulting property new_name.
-/
meta def have_with_name (lemma_name: name) (e1 e2 : expr) 
(new_name: name): tactic unit :=
do 
p ← resolve_name lemma_name, -- trace "lemma found",
 «have» new_name none ``(%%p %%e1 %%e2) -- <|> fail "have failed"

/-
Successively try to apply all the theorems with name in list <names> to expr e1 and e2,
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

-- variation with strings
meta def try_thm_from_strings (names: list string) (e1 e2 : expr)  (new_name: name)
: tactic unit :=
list.mfirst (λ nam,
do nam2 ← pure $ mk_simple_name nam,
have_with_name nam2 e1 e2 new_name, no_meta_vars,
tactic.trace ("Try this: have " ++ to_string new_name ++ " := "
++ to_string nam ++ " " ++ to_string e1 ++ " " ++ to_string e2))
names


/- Smart_add:
Successively try to apply all the theorems whose name starts with "add",
 to expr e1 and e2, and name the resulting property h.
 Stop at first success.
-/
-- open tactic.interactive
-- open lean.parser (tk)

meta def smart_add (h1 : parse ident) (h2 : parse ident)
(h : parse (tk "with" *> ident)) : tactic unit :=
do names ←  get_all_theorems_whose_name_starts_with "add",
   e1 ← get_local h1,
   e2 ← get_local h2,
    try_thm names e1 e2 h

meta def smart_mul (h1 : parse ident) (h2 : parse ident)
(h : parse (tk "with" *> ident)) : tactic unit :=
do names ←  get_all_theorems_whose_name_starts_with "mul",
   e1 ← get_local h1,
   e2 ← get_local h2,
    try_thm names e1 e2 h


/-
Test and examples
-/

-- variables x y z t: real
-- example -- (H1_lt: x < y) (H2_lt: t < z)
-- -- (H1_lte: x ≤ y) 
-- (H2_lte: t ≤ z)
-- (H1_e: x = y) -- (H2_e: t = z)
-- :
-- x + t ≤ y + z :=
-- begin
--     -- let a := 2,
--     -- have Haux0: a = 2, refl,
--     -- smart_add H1_lt a with H, rw Haux0 at H, clear Haux0, clear a,
--     library_search,
-- end
-- --   have H3 := add_lt_add_of_lt_of_le H1 H2,
--     -- smart_add H1_lt H2_lt with H100, -- add_lt_add
--     -- smart_add H1_lte H2_lte with H101, -- add_le_add
--     -- smart_add H1_lte H2_lt with H102a, -- add_lt_add_of_le_of_lt
--     -- smart_add H1_lt H2_lte with H102b, -- add_lt_add_of_lt_of_le
--     -- smart_add H1_lte z with H103, -- add_le_add_right
--     -- smart_add z H1_lte with H103, -- add_le_add_right
--     -- -- have H103b := add_le_add_left H1_lte z,
--     -- -- smart_add z H1_lte with H104 --> fail
--     -- smart_add H1_lt z with H104,

--     -- -- Add a real number: ya pa plus simple ??
--     -- set n:ℝ := 10.2, have Hn: n=10.2, refl,
--     -- smart_add H1_lt n with H104,
--     -- rw Hn at H104,
--     sorry,
-- end

-- #print add_le_add


-- We could implement addition with equalities
-- (see commented add lemmas above)
-- example (H1: x = y) (H2: t=z): x+t = y + z :=
-- begin
--   smart_add H1 H2 with H3,
-- end

/- 
----------------------------------------------------------
----------------------------------------------------------
|| Tactic smart_trans.
|| Try several transitivity theorem on two properties.
----------------------------------------------------------
----------------------------------------------------------
-/
def trans_lemmas := (["le_trans", "lt_trans", "ge_trans", "gt_trans", 
"lt_of_lt_of_le", "lt_of_le_of_lt",
"nat.dvd_trans"])
-- equality transitive??
-- missing: lt_of_lt_of_le, lt_of_le_of_lt

meta def smart_trans (h1 : parse ident) (h2 : parse ident)
(h : parse (tk "with" *> ident)) : tactic unit := do
-- do names ←  get_all_theorems_whose_name_starts_with "add",
   e1 ← get_local h1,
   e2 ← get_local h2,
    do {try_thm_from_strings trans_lemmas e1 e2 h}
    <|>
    do {try_thm_from_strings trans_lemmas e2 e1 h}



-- example (H: a < b) (H': c ≥ b) : a < c :=
-- begin
--     smart_trans H' H with TTT,
--     assumption,
-- end


/- 
----------------------------------------------------------
----------------------------------------------------------
|| Tactic smart_comm.
|| Get all theorems whose name ends with "comm",
|| and try to use them to rw some expr.
----------------------------------------------------------
----------------------------------------------------------
-/

-- open name 
def name.suffix_ends_with : name → string →  bool
| anonymous _ := ff
| (mk_string s n) p := string.ends_with s p
| (mk_numeral s n ) _ := ff

/-
Test if a lemma has a name which ends with a given suffix.
-/
meta def lemma_name_ends_with (decl: declaration) (subname: string) : bool :=
do let nam := decl.to_name in name.suffix_ends_with nam subname

/-
Get all lemmas whose name ends with a given suffix.
-/
meta def get_all_theorems_whose_name_ends_with (subname: string):
tactic (list name) :=
do
env ← tactic.get_env,
names ← pure (environment.fold env [] (λ decl nams,
if is_theorem decl && (lemma_name_ends_with decl subname)
&& not (to_string (declaration.to_name decl) = "eq_comm") 
then declaration.to_name decl :: nams else nams)),
--    names2 ← pure $ list.append names ["eq_comm"],
return names


/-
Debug: trace all "comm" lemmas.
-/ 

meta def trace_theorems_with_suffix (s: string): tactic (list unit) :=
do
nams ←  get_all_theorems_whose_name_ends_with s,
tactic.trace (to_string (nams.length) ++ " theorems with suffix " ++ s),
nams.mmap (λ nam, tactic.trace (to_string nam))

meta def trace_theorems_with_prefix (s: string) : tactic (list unit) :=
do
nams ←  get_all_theorems_whose_name_starts_with s,
tactic.trace (to_string (nams.length) ++ " theorems with prefix " ++ s),
nams.mmap (λ nam, tactic.trace (to_string nam))


-- run_cmd trace_theorems_with_suffix "comm"

-- run_cmd trace_theorems_with_suffix "_trans"
-- le_trans, lt_trans, ge_trans, gt_trans, nat.dvd_trans
-- equality transitive??
-- missing: lt_of_lt_of_le, lt_of_le_of_lt

-- run_cmd trace_theorems_with_suffix "assoc"

-- #print le_trans

-- run_cmd trace_comm_theorems

/-
Rewrite expr e1 using theorem whose name is nam.
TODO: reverse does not work for the moment!!
-/
meta def rw_with_name (nam: name) (oe1 : option expr) (reverse: bool) -- (on_target: bool)
: tactic unit := match oe1 with
| (some e1) := do e ← mk_const nam, rewrite_hyp e e1  {symm := reverse}, skip
-- match reverse with 
--     | ff :=  tactic.trace ("Try this: rw " ++ to_string nam ++ " at " ++ to_string e1)
--     | tt := tactic.trace ("Try this: rw ← " ++ to_string nam ++ " at " ++ to_string e1)
--     end
| none := do e ← mk_const nam, rewrite_target e  {symm := reverse}, skip
-- match reverse with 
--     | ff :=  tactic.trace ("Try this: rw " ++ to_string nam)
--     | tt := tactic.trace ("Try this: rw ← " ++ to_string nam)
--     end
end
-- do 
-- -- p ← resolve_name nam,
-- -- e ← to_expr p,
-- if reverse then do
-- e ← mk_const nam, rewrite_hyp e e1 {symm := tt}, skip
-- else do 
-- e ← mk_const nam, rewrite_hyp e e1, skip
-- | tt :=
-- end

/-
Successively try to rw e1 (or target) with all the theorems with name in list names.
Stop at first success.
If e1 is some h, rewrite on e1, else rw on target.
If both_direction is tt then also try rw ←.
-/
meta def rw_with_thm (names: list name) (e1 : option expr)
(both_directions: bool): tactic unit :=
list.mfirst 
(λ nam, do -- trace "coucou",
    (do rw_with_name nam e1 ff, no_meta_vars,
    match e1 with
        | (some h) :=  tactic.trace ("Try this: rw " ++ to_string nam ++ " at " ++ to_string h)
        | none := tactic.trace ("Try this: rw " ++ to_string nam)
    end
    )
<|> ( if (not both_directions) then failure else
    do rw_with_name nam e1 tt, no_meta_vars,
    match e1 with
        | (some h) :=  tactic.trace ("Try this: rw ← " ++ to_string nam ++ " at " ++ to_string h)
        | none := tactic.trace ("Try this: rw ← " ++ to_string nam)
    end
    )
) names
-- -- In case of success trace the successful code:
-- match e1 with
-- | (some h) :=  tactic.trace ("Try this: rw " ++ to_string nam ++ " at " ++ to_string h)
-- | (some h) := tactic.trace ("Try this: rw ← " ++ to_string nam ++ " at " ++ to_string h)
-- | none := tactic.trace ("Try this: rw " ++ to_string nam)
-- | none := tactic.trace ("Try this: rw ← " ++ to_string nam)
-- -- | _ := failure
-- end) names

-- Variation with list strings
-- meta def rw_thm_from_strings (names: list string) (e1 : option expr) (reverse: bool)
-- : tactic unit :=
-- list.mfirst (λ nam,
-- do nam2 ← pure $ mk_simple_name nam,
-- rw_with_name nam e1 reverse, no_meta_vars,
-- -- In case of success trace the successful code:
-- match (e1, reverse) with
-- | (some h, ff) :=  tactic.trace ("Try this: rw " ++ to_string nam ++ " at " ++ to_string h)
-- | (some h, tt) := tactic.trace ("Try this: rw ← " ++ to_string nam ++ " at " ++ to_string h)
-- | (_, ff) := tactic.trace ("Try this: rw " ++ to_string nam)
-- | (_, tt) := tactic.trace ("Try this: rw ← " ++ to_string nam)
-- -- | _ := failure
-- end) names

def names_from_strings (strings: list string) : (list name) :=
list.map (λ s, mk_simple_name s) strings

meta def rw_with_thm_from_strings (strings: list string) (e1 : option expr)
(both_directions: bool): tactic unit :=
rw_with_thm (names_from_strings strings) e1 both_directions


-- Other working code:
-- meta def rw_with_thm_from_strings (strings: list string) (e1 : option expr)
-- (both_directions: bool): tactic unit :=
-- list.mfirst 
-- (λ s, do nam ← pure $ mk_simple_name s,
--     (do rw_with_name nam e1 ff, no_meta_vars, 
--     match e1 with
--         | (some h) :=  tactic.trace ("Try this: rw " ++ to_string nam ++ " at " ++ to_string h)
--         | none := tactic.trace ("Try this: rw " ++ to_string nam)
--     end
--     )
-- <|> ( if (not both_directions) then skip else
--     do rw_with_name nam e1 tt, no_meta_vars,
--     match e1 with
--         | (some h) :=  tactic.trace ("Try this: rw ← " ++ to_string nam ++ " at " ++ to_string h)
--         | none := tactic.trace ("Try this: rw ← " ++ to_string nam)
--     end
--     )
-- ) strings


/- Smart_comm and smart_comm_on_target:
Successively try to rw expr using all the theorems 
- first in the comm_list,
- then those whose name ends with "comm".
Stop at first success. Note that we add lemma eq_comm at the end of the list.
-/
-- TODO: Add a final list which is removed from all names and tried at the end (e.g. eq_comm)
private def comm_list := ["add_comm", "mul_comm"]
meta def smart_comm (h1 : parse ident) : tactic unit :=
do e1 ← get_local h1,
    (do rw_with_thm_from_strings comm_list e1 ff, trace "(done with list)")
<|> (do
    names ←  get_all_theorems_whose_name_ends_with "comm",
    names2 ← pure $ list.append names ["eq_comm"],
        rw_with_thm names2 e1 ff
    )

meta def smart_comm_on_target : tactic unit :=
do 
    (rw_with_thm_from_strings comm_list none ff)
<|> (do
    names ←  get_all_theorems_whose_name_ends_with "comm",
    names2 ← pure $ list.append names ["eq_comm"],
        rw_with_thm names2 none ff
    )


/- Smart_assoc and smart_assoc_on_target:
Successively try to rw expr using all the theorems whose name ends with "assoc",
in both direct and reverse direction.
 Stop at first success.
-/
meta def smart_assoc (h1 : parse ident) : tactic unit :=
do names ←  get_all_theorems_whose_name_ends_with "assoc",
   e1 ← get_local h1, -- tactic.trace "Got h1",
    do {rw_with_thm names e1 tt} <|> do {rw_with_thm names e1 ff}

meta def smart_assoc_on_target : tactic unit :=
do names ←  get_all_theorems_whose_name_ends_with "assoc",
    do {rw_with_thm names none tt} <|> do {rw_with_thm names none ff}


-- variables (x y z t : ℝ)
-- example (H: (x*y)*z =0): (y*z)=(z*y) :=
-- begin
--     -- rw commute.right_comm at H,
--     -- rw mul_comm at H,
--     smart_comm H,
--     -- exact mul_comm y z,
--     -- smart_comm H,
--     -- smart_comm_on_target, 
--     -- smart_comm_on_target, -- smart_comm H,
--     -- smart_assoc_on_target,
--     -- assumption,
--     sorry,
-- end


-- example (H1: x+y=z+t) (H2: z=t)
-- (H3 : ∀ a, x + a = y + a):
-- ∀ a, x + a = y + a :=
-- begin
--     smart_comm H2,
--     -- smart_comm H3, -- FAIL: does not work under quantifiers
--     -- exact congr_fun (congr_arg has_add.add H1) t
--     -- conv {congr, skip, rw add_comm},
--     -- smart_comm H1,
--     -- smart_comm H1,
--     -- NON : simp_rw add_comm,
--     -- NON : conv in (x+_) {simp_rw add_comm }
--     sorry
-- end

-- example (x y t: ℝ) (H1: t + (x+y)=0): (t+x) +y = 0 :=
-- begin
--     library_search,
-- end


-- example (H1: (x+y)*z = (x*y)+t+ (x+y)) : true :=
-- begin
--     -- have H1b : (x+y)*z = (y+x)*z,
--     --     {ring},
--     --     rw H1b at H1,
--         -- {have Hcomm := add_comm x y,
--         -- rw Hcomm at H1}, 

--     have H1': (y+x)*z = (x*y)+t+ (x+y),
--     simp only [add_comm, H1], clear H1, rename H1' H1,
--     smart_assoc H1,
--     smart_comm H1,
--     smart_comm H1,
--     sorry,
-- end


/-conv.smart_comm-/




end tactic.interactive


