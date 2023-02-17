/-
Copyright (c) 2018 Scott Morrison. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Scott Morrison, Reid Barton, Simon Hudon, Kenny Lau

Opposites.
-/
import data.list.defs
import data.equiv.basic

universes v u -- declare the `v` first; see `category_theory.category` for an explanation
variable (α : Sort u)

/-- The type of objects of the opposite of `α`; used to defined opposite category/group/...

  In order to avoid confusion between `α` and its opposite type, we
  set up the type of objects `opposite α` using the following pattern,
  which will be repeated later for the morphisms.

  1. Define `opposite α := α`.
  2. Define the isomorphisms `op : α → opposite α`, `unop : opposite α → α`.
  3. Make the definition `opposite` irreducible.

  This has the following consequences.

  * `opposite α` and `α` are distinct types in the elaborator, so you
    must use `op` and `unop` explicitly to convert between them.
  * Both `unop (op X) = X` and `op (unop X) = X` are definitional
    equalities. Notably, every object of the opposite category is
    definitionally of the form `op X`, which greatly simplifies the
    definition of the structure of the opposite category, for example.

  (If Lean supported definitional eta equality for records, we could
  achieve the same goals using a structure with one field.)
-/
def opposite : Sort u := α

-- Use a high right binding power (like that of postfix ⁻¹) so that, for example,
-- `presheaf Cᵒᵖ` parses as `presheaf (Cᵒᵖ)` and not `(presheaf C)ᵒᵖ`.
notation α `ᵒᵖ`:std.prec.max_plus := opposite α

namespace opposite

variables {α}
def op : α → αᵒᵖ := id
def unop : αᵒᵖ → α := id

lemma op_injective : function.injective (op : α → αᵒᵖ) := λ _ _, id
lemma unop_injective : function.injective (unop : αᵒᵖ → α) := λ _ _, id

@[simp] lemma op_inj_iff (x y : α) : op x = op y ↔ x = y := iff.rfl
@[simp] lemma unop_inj_iff (x y : αᵒᵖ) : unop x = unop y ↔ x = y := iff.rfl

@[simp] lemma op_unop (x : αᵒᵖ) : op (unop x) = x := rfl
@[simp] lemma unop_op (x : α) : unop (op x) = x := rfl

attribute [irreducible] opposite

/-- The type-level equivalence between a type and its opposite. -/
def equiv_to_opposite : α ≃ αᵒᵖ :=
{ to_fun := op,
  inv_fun := unop,
  left_inv := λ a, by simp,
  right_inv := λ a, by simp, }

@[simp]
lemma equiv_to_opposite_apply (a : α) : equiv_to_opposite a = op a := rfl
@[simp]
lemma equiv_to_opposite_symm_apply (a : αᵒᵖ) : equiv_to_opposite.symm a = unop a := rfl

lemma op_eq_iff_eq_unop {x : α} {y} : op x = y ↔ x = unop y :=
equiv_to_opposite.apply_eq_iff_eq_symm_apply _ _

lemma unop_eq_iff_eq_op {x} {y : α} : unop x = y ↔ x = op y :=
equiv_to_opposite.symm.apply_eq_iff_eq_symm_apply _ _

instance [inhabited α] : inhabited αᵒᵖ := ⟨op (default _)⟩

def op_induction {F : Π (X : αᵒᵖ), Sort v} (h : Π X, F (op X)) : Π X, F X :=
λ X, h (unop X)
end opposite

namespace tactic

open opposite
open interactive interactive.types lean.parser tactic
local postfix `?`:9001 := optional

namespace op_induction

meta def is_opposite (e : expr) : tactic bool :=
do t ← infer_type e,
   `(opposite _) ← whnf t | return ff,
   return tt

meta def find_opposite_hyp : tactic name :=
do lc ← local_context,
   h :: _ ← lc.mfilter $ is_opposite | fail "No hypotheses of the form Xᵒᵖ",
   return h.local_pp_name

end op_induction

open op_induction

meta def op_induction (h : option name) : tactic unit :=
do h ← match h with
   | (some h) := pure h
   | none     := find_opposite_hyp
   end,
   h' ← tactic.get_local h,
   revert_lst [h'],
   applyc `opposite.op_induction,
   tactic.intro h,
   skip

-- For use with `local attribute [tidy] op_induction`
meta def op_induction' := op_induction none

namespace interactive
meta def op_induction (h : parse ident?) : tactic unit :=
tactic.op_induction h
end interactive

end tactic
