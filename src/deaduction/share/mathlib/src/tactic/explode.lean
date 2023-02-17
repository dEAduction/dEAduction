/-
Copyright (c) 2018 Mario Carneiro. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Author: Mario Carneiro
-/
import tactic.core
/-!
# `#explode` command

Displays a proof term in a line by line format somewhat akin to a Fitch style
proof or the Metamath proof style.
-/

open expr tactic

namespace tactic
namespace explode

-- TODO(Mario): move back to list.basic
@[simp] def head' {α} : list α → option α
| []       := none
| (a :: l) := some a

@[derive inhabited]
inductive status | reg | intro | lam | sintro

meta structure entry :=
(expr : expr)
(line : nat)
(depth : nat)
(status : status)
(thm : string)
(deps : list nat)

meta def pad_right (l : list string) : list string :=
let n := l.foldl (λ r (s:string), max r s.length) 0 in
l.map $ λ s, nat.iterate (λ s, s.push ' ') (n - s.length) s

@[derive inhabited]
meta structure entries := mk' ::
(s : expr_map entry)
(l : list entry)

meta def entries.find (es : entries) (e : expr) := es.s.find e
meta def entries.size (es : entries) := es.s.size

meta def entries.add : entries → entry → entries
| es@⟨s, l⟩ e := if s.contains e.expr then es else ⟨s.insert e.expr e, e :: l⟩

meta def entries.head (es : entries) : option entry := head' es.l

meta def format_aux : list string → list string → list string → list entry → tactic format
| (line :: lines) (dep :: deps) (thm :: thms) (en :: es) := do
  fmt ← do {
    let margin := string.join (list.repeat " │" en.depth),
    let margin := match en.status with
      | status.sintro := " ├" ++ margin
      | status.intro := " │" ++ margin ++ " ┌"
      | status.reg := " │" ++ margin ++ ""
      | status.lam := " │" ++ margin ++ ""
      end,
    p ← infer_type en.expr >>= pp,
    let lhs :=  line ++ "│" ++ dep ++ "│ " ++ thm ++ margin ++ " ",
    return $ format.of_string lhs ++ to_string p ++ format.line },
  (++ fmt) <$> format_aux lines deps thms es
| _ _ _ _ := return format.nil

meta instance : has_to_tactic_format entries :=
⟨λ es : entries,
  let lines := pad_right $ es.l.map (λ en, to_string en.line),
      deps  := pad_right $ es.l.map (λ en, string.intercalate "," (en.deps.map to_string)),
      thms  := pad_right $ es.l.map entry.thm in
  format_aux lines deps thms es.l⟩

meta def append_dep (filter : expr → tactic unit)
 (es : entries) (e : expr) (deps : list nat) : tactic (list nat) :=
do { ei ← es.find e,
  filter ei.expr,
  return (ei.line :: deps) }
<|> return deps

meta def may_be_proof (e : expr) : tactic bool :=
do expr.sort u ← infer_type e >>= infer_type,
   return $ bnot u.nonzero

end explode
open explode

meta mutual def explode.core, explode.args (filter : expr → tactic unit)
with explode.core : expr → bool → nat → entries → tactic entries
| e@(lam n bi d b) si depth es := do
  m ← mk_fresh_name,
  let l := local_const m n bi d,
  let b' := instantiate_var b l,
  if si then
    let en : entry := ⟨l, es.size, depth, status.sintro, to_string n, []⟩ in do
    es' ← explode.core b' si depth (es.add en),
    return $ es'.add ⟨e, es'.size, depth, status.lam, "∀I", [es.size, es'.size - 1]⟩
  else do
    let en : entry := ⟨l, es.size, depth, status.intro, to_string n, []⟩,
    es' ← explode.core b' si (depth + 1) (es.add en),
    deps' ← explode.append_dep filter es' b' [],
    deps' ← explode.append_dep filter es' l deps',
    return $ es'.add ⟨e, es'.size, depth, status.lam, "∀I", deps'⟩
| e@(macro _ l) si depth es := explode.core l.head si depth es
| e si depth es := filter e >>
  match get_app_fn_args e with
  | (const n _, args) :=
    explode.args e args depth es (to_string n) []
  | (fn, []) := do
    p ← pp fn,
    let en : entry := ⟨fn, es.size, depth, status.reg, to_string p, []⟩,
    return (es.add en)
  | (fn, args) := do
    es' ← explode.core fn ff depth es,
    deps ← explode.append_dep filter es' fn [],
    explode.args e args depth es' "∀E" deps
  end
with explode.args : expr → list expr → nat → entries → string → list nat → tactic entries
| e (arg :: args) depth es thm deps := do
  es' ← explode.core arg ff depth es <|> return es,
  deps' ← explode.append_dep filter es' arg deps,
  explode.args e args depth es' thm deps'
| e [] depth es thm deps :=
  return (es.add ⟨e, es.size, depth, status.reg, thm, deps.reverse⟩)

meta def explode_expr (e : expr) (hide_non_prop := tt) : tactic entries :=
let filter := if hide_non_prop then λ e, may_be_proof e >>= guardb else λ _, skip in
tactic.explode.core filter e tt 0 (default _)

meta def explode (n : name) : tactic unit :=
do const n _ ← resolve_name n | fail "cannot resolve name",
  d ← get_decl n,
  v ← match d with
  | (declaration.defn _ _ _ v _ _) := return v
  | (declaration.thm _ _ _ v)      := return v.get
  | _                  := fail "not a definition"
  end,
  t ← pp d.type,
  explode_expr v <* trace (to_fmt n ++ " : " ++ t) >>= trace

open interactive lean lean.parser interaction_monad.result

/--
`#explode decl_name` displays a proof term in a line by line format somewhat akin to a Fitch style
proof or the Metamath proof style.

`#explode iff_true_intro` produces

```lean
iff_true_intro : ∀ {a : Prop}, a → (a ↔ true)
0│   │ a         ├ Prop
1│   │ h         ├ a
2│   │ hl        │ ┌ a
3│   │ trivial   │ │ true
4│2,3│ ∀I        │ a → true
5│   │ hr        │ ┌ true
6│5,1│ ∀I        │ true → a
7│4,6│ iff.intro │ a ↔ true
8│1,7│ ∀I        │ a → (a ↔ true)
9│0,8│ ∀I        │ ∀ {a : Prop}, a → (a ↔ true)
```
-/
@[user_command]
meta def explode_cmd (_ : parse $ tk "#explode") : parser unit :=
do n ← ident,
  explode n
.

add_tactic_doc
{ name                     := "#explode",
  category                 := doc_category.cmd,
  decl_names               := [`tactic.explode_cmd],
  tags                     := ["proof display"] }

-- #explode iff_true_intro
-- #explode nat.strong_rec_on

end tactic
