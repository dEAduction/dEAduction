/-
Copyright (c) 2017 Johannes Hölzl. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Johannes Hölzl

Theory of complete lattices.
-/
import order.bounds

set_option old_structure_cmd true
open set

universes u v w w₂
variables {α : Type u} {β : Type v} {ι : Sort w} {ι₂ : Sort w₂}

/-- class for the `Sup` operator -/
class has_Sup (α : Type u) := (Sup : set α → α)
/-- class for the `Inf` operator -/
class has_Inf (α : Type u) := (Inf : set α → α)
/-- Supremum of a set -/
def Sup [has_Sup α] : set α → α := has_Sup.Sup
/-- Infimum of a set -/
def Inf [has_Inf α] : set α → α := has_Inf.Inf
/-- Indexed supremum -/
def supr [has_Sup α] (s : ι → α) : α := Sup (range s)
/-- Indexed infimum -/
def infi [has_Inf α] (s : ι → α) : α := Inf (range s)

lemma has_Inf_to_nonempty (α) [has_Inf α] : nonempty α := ⟨Inf ∅⟩
lemma has_Sup_to_nonempty (α) [has_Sup α] : nonempty α := ⟨Sup ∅⟩

notation `⨆` binders `, ` r:(scoped f, supr f) := r
notation `⨅` binders `, ` r:(scoped f, infi f) := r

section prio
set_option default_priority 100 -- see Note [default priority]
/-- A complete lattice is a bounded lattice which
  has suprema and infima for every subset. -/
class complete_lattice (α : Type u) extends bounded_lattice α, has_Sup α, has_Inf α :=
(le_Sup : ∀s, ∀a∈s, a ≤ Sup s)
(Sup_le : ∀s a, (∀b∈s, b ≤ a) → Sup s ≤ a)
(Inf_le : ∀s, ∀a∈s, Inf s ≤ a)
(le_Inf : ∀s a, (∀b∈s, a ≤ b) → a ≤ Inf s)

/-- Create a `complete_lattice` from a `partial_order` and `Inf` function
that returns the greatest lower bound of a set. Usually this constructor provides
poor definitional equalities, so it should be used with
`.. complete_lattice_of_Inf α _`. -/
def complete_lattice_of_Inf (α : Type u) [H1 : partial_order α]
  [H2 : has_Inf α] (is_glb_Inf : ∀ s : set α, is_glb s (Inf s)) :
  complete_lattice α :=
{ bot := Inf univ,
  bot_le := λ x, (is_glb_Inf univ).1 trivial,
  top := Inf ∅,
  le_top := λ a, (is_glb_Inf ∅).2 $ by simp,
  sup := λ a b, Inf {x | a ≤ x ∧ b ≤ x},
  inf := λ a b, Inf {a, b},
  le_inf := λ a b c hab hac, by { apply (is_glb_Inf _).2, simp [*] },
  inf_le_right := λ a b, (is_glb_Inf _).1 $ mem_insert_of_mem _ $ mem_singleton _,
  inf_le_left := λ a b, (is_glb_Inf _).1 $ mem_insert _ _,
  sup_le := λ a b c hac hbc, (is_glb_Inf _).1 $ by simp [*],
  le_sup_left := λ a b, (is_glb_Inf _).2 $ λ x, and.left,
  le_sup_right := λ a b, (is_glb_Inf _).2 $ λ x, and.right,
  le_Inf := λ s a ha, (is_glb_Inf s).2 ha,
  Inf_le := λ s a ha, (is_glb_Inf s).1 ha,
  Sup := λ s, Inf (upper_bounds s),
  le_Sup := λ s a ha, (is_glb_Inf (upper_bounds s)).2 $ λ b hb, hb ha,
  Sup_le := λ s a ha, (is_glb_Inf (upper_bounds s)).1 ha,
  .. H1, .. H2 }

/-- Create a `complete_lattice` from a `partial_order` and `Sup` function
that returns the least upper bound of a set. Usually this constructor provides
poor definitional equalities, so it should be used with
`.. complete_lattice_of_Sup α _`. -/
def complete_lattice_of_Sup (α : Type*) [H1 : partial_order α]
  [H2 : has_Sup α] (is_lub_Sup : ∀ s : set α, is_lub s (Sup s)) :
  complete_lattice α :=
{ top := Sup univ,
  le_top := λ x, (is_lub_Sup univ).1 trivial,
  bot := Sup ∅,
  bot_le := λ x, (is_lub_Sup ∅).2 $ by simp,
  sup := λ a b, Sup {a, b},
  sup_le := λ a b c hac hbc, (is_lub_Sup _).2 (by simp [*]),
  le_sup_left := λ a b, (is_lub_Sup _).1 $ mem_insert _ _,
  le_sup_right := λ a b, (is_lub_Sup _).1 $ mem_insert_of_mem _ $ mem_singleton _,
  inf := λ a b, Sup {x | x ≤ a ∧ x ≤ b},
  le_inf := λ a b c hab hac, (is_lub_Sup _).1 $ by simp [*],
  inf_le_left := λ a b, (is_lub_Sup _).2 (λ x, and.left),
  inf_le_right := λ a b, (is_lub_Sup _).2 (λ x, and.right),
  Inf := λ s, Sup (lower_bounds s),
  Sup_le := λ s a ha, (is_lub_Sup s).2 ha,
  le_Sup := λ s a ha, (is_lub_Sup s).1 ha,
  Inf_le := λ s a ha, (is_lub_Sup (lower_bounds s)).2 (λ b hb, hb ha),
  le_Inf := λ s a ha, (is_lub_Sup (lower_bounds s)).1 ha,
  .. H1, .. H2 }

/-- A complete linear order is a linear order whose lattice structure is complete. -/
class complete_linear_order (α : Type u) extends complete_lattice α, decidable_linear_order α
end prio

section
variables [complete_lattice α] {s t : set α} {a b : α}

@[ematch] theorem le_Sup : a ∈ s → a ≤ Sup s := complete_lattice.le_Sup s a

theorem Sup_le : (∀b∈s, b ≤ a) → Sup s ≤ a := complete_lattice.Sup_le s a

@[ematch] theorem Inf_le : a ∈ s → Inf s ≤ a := complete_lattice.Inf_le s a

theorem le_Inf : (∀b∈s, a ≤ b) → a ≤ Inf s := complete_lattice.le_Inf s a

lemma is_lub_Sup (s : set α) : is_lub s (Sup s) := ⟨assume x, le_Sup, assume x, Sup_le⟩

lemma is_lub.Sup_eq (h : is_lub s a) : Sup s = a := (is_lub_Sup s).unique h

lemma is_glb_Inf (s : set α) : is_glb s (Inf s) := ⟨assume a, Inf_le, assume a, le_Inf⟩

lemma is_glb.Inf_eq (h : is_glb s a) : Inf s = a := (is_glb_Inf s).unique h

theorem le_Sup_of_le (hb : b ∈ s) (h : a ≤ b) : a ≤ Sup s :=
le_trans h (le_Sup hb)

theorem Inf_le_of_le (hb : b ∈ s) (h : b ≤ a) : Inf s ≤ a :=
le_trans (Inf_le hb) h

theorem Sup_le_Sup (h : s ⊆ t) : Sup s ≤ Sup t :=
(is_lub_Sup s).mono (is_lub_Sup t) h

theorem Inf_le_Inf (h : s ⊆ t) : Inf t ≤ Inf s :=
(is_glb_Inf s).mono (is_glb_Inf t) h

@[simp] theorem Sup_le_iff : Sup s ≤ a ↔ (∀b ∈ s, b ≤ a) :=
is_lub_le_iff (is_lub_Sup s)

@[simp] theorem le_Inf_iff : a ≤ Inf s ↔ (∀b ∈ s, a ≤ b) :=
le_is_glb_iff (is_glb_Inf s)

theorem Inf_le_Sup (hs : s.nonempty) : Inf s ≤ Sup s :=
is_glb_le_is_lub (is_glb_Inf s) (is_lub_Sup s) hs

-- TODO: it is weird that we have to add union_def
theorem Sup_union {s t : set α} : Sup (s ∪ t) = Sup s ⊔ Sup t :=
((is_lub_Sup s).union (is_lub_Sup t)).Sup_eq

theorem Sup_inter_le {s t : set α} : Sup (s ∩ t) ≤ Sup s ⊓ Sup t :=
by finish
/-
  Sup_le (assume a ⟨a_s, a_t⟩, le_inf (le_Sup a_s) (le_Sup a_t))
-/

theorem Inf_union {s t : set α} : Inf (s ∪ t) = Inf s ⊓ Inf t :=
((is_glb_Inf s).union (is_glb_Inf t)).Inf_eq

theorem le_Inf_inter {s t : set α} : Inf s ⊔ Inf t ≤ Inf (s ∩ t) :=
by finish
/-
le_Inf (assume a ⟨a_s, a_t⟩, sup_le (Inf_le a_s) (Inf_le a_t))
-/

@[simp] theorem Sup_empty : Sup ∅ = (⊥ : α) :=
is_lub_empty.Sup_eq

@[simp] theorem Inf_empty : Inf ∅ = (⊤ : α) :=
(@is_glb_empty α _).Inf_eq

@[simp] theorem Sup_univ : Sup univ = (⊤ : α) :=
(@is_lub_univ α _).Sup_eq

@[simp] theorem Inf_univ : Inf univ = (⊥ : α) :=
is_glb_univ.Inf_eq

-- TODO(Jeremy): get this automatically
@[simp] theorem Sup_insert {a : α} {s : set α} : Sup (insert a s) = a ⊔ Sup s :=
((is_lub_Sup s).insert a).Sup_eq

@[simp] theorem Inf_insert {a : α} {s : set α} : Inf (insert a s) = a ⊓ Inf s :=
((is_glb_Inf s).insert a).Inf_eq

-- We will generalize this to conditionally complete lattices in `cSup_singleton`.
theorem Sup_singleton {a : α} : Sup {a} = a :=
is_lub_singleton.Sup_eq

-- We will generalize this to conditionally complete lattices in `cInf_singleton`.
theorem Inf_singleton {a : α} : Inf {a} = a :=
is_glb_singleton.Inf_eq

theorem Sup_pair {a b : α} : Sup {a, b} = a ⊔ b :=
(@is_lub_pair α _ a b).Sup_eq

theorem Inf_pair {a b : α} : Inf {a, b} = a ⊓ b :=
(@is_glb_pair α _ a b).Inf_eq

@[simp] theorem Inf_eq_top : Inf s = ⊤ ↔ (∀a∈s, a = ⊤) :=
iff.intro
  (assume h a ha, top_unique $ h ▸ Inf_le ha)
  (assume h, top_unique $ le_Inf $ assume a ha, top_le_iff.2 $ h a ha)

@[simp] theorem Sup_eq_bot : Sup s = ⊥ ↔ (∀a∈s, a = ⊥) :=
iff.intro
  (assume h a ha, bot_unique $ h ▸ le_Sup ha)
  (assume h, bot_unique $ Sup_le $ assume a ha, le_bot_iff.2 $ h a ha)

end

section complete_linear_order
variables [complete_linear_order α] {s t : set α} {a b : α}

lemma Inf_lt_iff : Inf s < b ↔ (∃a∈s, a < b) :=
is_glb_lt_iff (is_glb_Inf s)

lemma lt_Sup_iff : b < Sup s ↔ (∃a∈s, b < a) :=
lt_is_lub_iff (is_lub_Sup s)

lemma Sup_eq_top : Sup s = ⊤ ↔ (∀b<⊤, ∃a∈s, b < a) :=
iff.intro
  (assume (h : Sup s = ⊤) b hb, by rwa [←h, lt_Sup_iff] at hb)
  (assume h, top_unique $ le_of_not_gt $ assume h',
    let ⟨a, ha, h⟩ := h _ h' in
    lt_irrefl a $ lt_of_le_of_lt (le_Sup ha) h)

@[nolint ge_or_gt] -- see Note [nolint_ge]
lemma Inf_eq_bot : Inf s = ⊥ ↔ (∀b>⊥, ∃a∈s, a < b) :=
iff.intro
  (assume (h : Inf s = ⊥) b (hb : ⊥ < b), by rwa [←h, Inf_lt_iff] at hb)
  (assume h, bot_unique $ le_of_not_gt $ assume h',
    let ⟨a, ha, h⟩ := h _ h' in
    lt_irrefl a $ lt_of_lt_of_le h (Inf_le ha))

lemma lt_supr_iff {ι : Sort*} {f : ι → α} : a < supr f ↔ (∃i, a < f i) :=
lt_Sup_iff.trans exists_range_iff

lemma infi_lt_iff {ι : Sort*} {f : ι → α} : infi f < a ↔ (∃i, f i < a) :=
Inf_lt_iff.trans exists_range_iff

end complete_linear_order

/- supr & infi -/

section
variables [complete_lattice α] {s t : ι → α} {a b : α}

-- TODO: this declaration gives error when starting smt state
--@[ematch]
theorem le_supr (s : ι → α) (i : ι) : s i ≤ supr s :=
le_Sup ⟨i, rfl⟩

@[ematch] theorem le_supr' (s : ι → α) (i : ι) : (: s i ≤ supr s :) :=
le_Sup ⟨i, rfl⟩

/- TODO: this version would be more powerful, but, alas, the pattern matcher
   doesn't accept it.
@[ematch] theorem le_supr' (s : ι → α) (i : ι) : (: s i :) ≤ (: supr s :) :=
le_Sup ⟨i, rfl⟩
-/

lemma is_lub_supr : is_lub (range s) (⨆j, s j) := is_lub_Sup _

lemma is_lub.supr_eq (h : is_lub (range s) a) : (⨆j, s j) = a := h.Sup_eq

lemma is_glb_infi : is_glb (range s) (⨅j, s j) := is_glb_Inf _

lemma is_glb.infi_eq (h : is_glb (range s) a) : (⨅j, s j) = a := h.Inf_eq

theorem le_supr_of_le (i : ι) (h : a ≤ s i) : a ≤ supr s :=
le_trans h (le_supr _ i)

theorem supr_le (h : ∀i, s i ≤ a) : supr s ≤ a :=
Sup_le $ assume b ⟨i, eq⟩, eq ▸ h i

theorem supr_le_supr (h : ∀i, s i ≤ t i) : supr s ≤ supr t :=
supr_le $ assume i, le_supr_of_le i (h i)

theorem supr_le_supr2 {t : ι₂ → α} (h : ∀i, ∃j, s i ≤ t j) : supr s ≤ supr t :=
supr_le $ assume j, exists.elim (h j) le_supr_of_le

theorem supr_le_supr_const (h : ι → ι₂) : (⨆ i:ι, a) ≤ (⨆ j:ι₂, a) :=
supr_le $ le_supr _ ∘ h

@[simp] theorem supr_le_iff : supr s ≤ a ↔ (∀i, s i ≤ a) :=
(is_lub_le_iff is_lub_supr).trans forall_range_iff

theorem Sup_eq_supr {s : set α} : Sup s = (⨆a ∈ s, a) :=
le_antisymm
  (Sup_le $ assume b h, le_supr_of_le b $ le_supr _ h)
  (supr_le $ assume b, supr_le $ assume h, le_Sup h)

lemma le_supr_iff : (a ≤ supr s) ↔ (∀ b, (∀ i, s i ≤ b) → a ≤ b) :=
⟨λ h b hb, le_trans h (supr_le hb), λ h, h _ $ λ i, le_supr s i⟩

lemma monotone.le_map_supr [complete_lattice β] {f : α → β} (hf : monotone f) :
  (⨆ i, f (s i)) ≤ f (supr s) :=
supr_le $ λ i, hf $ le_supr _ _

lemma monotone.le_map_supr2 [complete_lattice β] {f : α → β} (hf : monotone f)
  {ι' : ι → Sort*} (s : Π i, ι' i → α) :
  (⨆ i (h : ι' i), f (s i h)) ≤ f (⨆ i (h : ι' i), s i h) :=
calc (⨆ i h, f (s i h)) ≤ (⨆ i, f (⨆ h, s i h)) :
  supr_le_supr $ λ i, hf.le_map_supr
... ≤ f (⨆ i (h : ι' i), s i h) : hf.le_map_supr

lemma monotone.le_map_Sup [complete_lattice β] {s : set α} {f : α → β} (hf : monotone f) :
  (⨆a∈s, f a) ≤ f (Sup s) :=
by rw [Sup_eq_supr]; exact hf.le_map_supr2 _

lemma supr_comp_le {ι' : Sort*} (f : ι' → α) (g : ι → ι') :
  (⨆ x, f (g x)) ≤ ⨆ y, f y :=
supr_le_supr2 $ λ x, ⟨_, le_refl _⟩

lemma monotone.supr_comp_eq [preorder β] {f : β → α} (hf : monotone f)
  {s : ι → β} (hs : ∀ x, ∃ i, x ≤ s i) :
  (⨆ x, f (s x)) = ⨆ y, f y :=
le_antisymm (supr_comp_le _ _) (supr_le_supr2 $ λ x, (hs x).imp $ λ i hi, hf hi)

-- TODO: finish doesn't do well here.
@[congr] theorem supr_congr_Prop {α : Type u} [has_Sup α] {p q : Prop} {f₁ : p → α} {f₂ : q → α}
  (pq : p ↔ q) (f : ∀x, f₁ (pq.mpr x) = f₂ x) : supr f₁ = supr f₂ :=
begin
  unfold supr,
  apply congr_arg,
  ext,
  simp,
  split,
  exact λ⟨h, W⟩, ⟨pq.1 h, eq.trans (f (pq.1 h)).symm W⟩,
  exact λ⟨h, W⟩, ⟨pq.2 h, eq.trans (f h) W⟩
end

theorem infi_le (s : ι → α) (i : ι) : infi s ≤ s i :=
Inf_le ⟨i, rfl⟩

@[ematch] theorem infi_le' (s : ι → α) (i : ι) : (: infi s ≤ s i :) :=
Inf_le ⟨i, rfl⟩

/- I wanted to see if this would help for infi_comm; it doesn't.
@[ematch] theorem infi_le₂' (s : ι → ι₂ → α) (i : ι) (j : ι₂) : (: ⨅ i j, s i j :) ≤ (: s i j :) :=
begin
  transitivity,
  apply (infi_le (λ i, ⨅ j, s i j) i),
  apply infi_le
end
-/

theorem infi_le_of_le (i : ι) (h : s i ≤ a) : infi s ≤ a :=
le_trans (infi_le _ i) h

theorem le_infi (h : ∀i, a ≤ s i) : a ≤ infi s :=
le_Inf $ assume b ⟨i, eq⟩, eq ▸ h i

theorem infi_le_infi (h : ∀i, s i ≤ t i) : infi s ≤ infi t :=
le_infi $ assume i, infi_le_of_le i (h i)

theorem infi_le_infi2 {t : ι₂ → α} (h : ∀j, ∃i, s i ≤ t j) : infi s ≤ infi t :=
le_infi $ assume j, exists.elim (h j) infi_le_of_le

theorem infi_le_infi_const (h : ι₂ → ι) : (⨅ i:ι, a) ≤ (⨅ j:ι₂, a) :=
le_infi $ infi_le _ ∘ h

@[simp] theorem le_infi_iff : a ≤ infi s ↔ (∀i, a ≤ s i) :=
⟨assume : a ≤ infi s, assume i, le_trans this (infi_le _ _), le_infi⟩

theorem Inf_eq_infi {s : set α} : Inf s = (⨅a ∈ s, a) :=
le_antisymm
  (le_infi $ assume b, le_infi $ assume h, Inf_le h)
  (le_Inf $ assume b h, infi_le_of_le b $ infi_le _ h)

lemma monotone.map_infi_le [complete_lattice β] {f : α → β} (hf : monotone f) :
  f (infi s) ≤ (⨅ i, f (s i)) :=
le_infi $ λ i, hf $ infi_le _ _

lemma monotone.map_infi2_le [complete_lattice β] {f : α → β} (hf : monotone f)
  {ι' : ι → Sort*} (s : Π i, ι' i → α) :
  f (⨅ i (h : ι' i), s i h) ≤ (⨅ i (h : ι' i), f (s i h)) :=
calc f (⨅ i (h : ι' i), s i h) ≤ (⨅ i, f (⨅ h, s i h)) : hf.map_infi_le
... ≤ (⨅ i h, f (s i h)) : infi_le_infi $ λ i, hf.map_infi_le

lemma monotone.map_Inf_le [complete_lattice β] {s : set α} {f : α → β} (hf : monotone f) :
  f (Inf s) ≤ ⨅ a∈s, f a :=
by rw [Inf_eq_infi]; exact hf.map_infi2_le _

lemma le_infi_comp {ι' : Sort*} (f : ι' → α) (g : ι → ι') :
  (⨅ y, f y) ≤ ⨅ x, f (g x) :=
infi_le_infi2 $ λ x, ⟨_, le_refl _⟩

lemma monotone.infi_comp_eq [preorder β] {f : β → α} (hf : monotone f)
  {s : ι → β} (hs : ∀ x, ∃ i, s i ≤ x) :
  (⨅ x, f (s x)) = ⨅ y, f y :=
le_antisymm (infi_le_infi2 $ λ x, (hs x).imp $ λ i hi, hf hi) (le_infi_comp _ _)

@[congr] theorem infi_congr_Prop {α : Type u} [has_Inf α] {p q : Prop} {f₁ : p → α} {f₂ : q → α}
  (pq : p ↔ q) (f : ∀x, f₁ (pq.mpr x) = f₂ x) : infi f₁ = infi f₂ :=
begin
  unfold infi,
  apply congr_arg,
  ext,
  simp,
  split,
  exact λ⟨h, W⟩, ⟨pq.1 h, eq.trans (f (pq.1 h)).symm W⟩,
  exact λ⟨h, W⟩, ⟨pq.2 h, eq.trans (f h) W⟩
end

-- We will generalize this to conditionally complete lattices in `cinfi_const`.
theorem infi_const [nonempty ι] {a : α} : (⨅ b:ι, a) = a :=
by rw [infi, range_const, Inf_singleton]

-- We will generalize this to conditionally complete lattices in `csupr_const`.
theorem supr_const [nonempty ι] {a : α} : (⨆ b:ι, a) = a :=
by rw [supr, range_const, Sup_singleton]

@[simp] lemma infi_top : (⨅i:ι, ⊤ : α) = ⊤ :=
top_unique $ le_infi $ assume i, le_refl _

@[simp] lemma supr_bot : (⨆i:ι, ⊥ : α) = ⊥ :=
bot_unique $ supr_le $ assume i, le_refl _

@[simp] lemma infi_eq_top : infi s = ⊤ ↔ (∀i, s i = ⊤) :=
iff.intro
  (assume eq i, top_unique $ eq ▸ infi_le _ _)
  (assume h, top_unique $ le_infi $ assume i, top_le_iff.2 $ h i)

@[simp] lemma supr_eq_bot : supr s = ⊥ ↔ (∀i, s i = ⊥) :=
iff.intro
  (assume eq i, bot_unique $ eq ▸ le_supr _ _)
  (assume h, bot_unique $ supr_le $ assume i, le_bot_iff.2 $ h i)

@[simp] lemma infi_pos {p : Prop} {f : p → α} (hp : p) : (⨅ h : p, f h) = f hp :=
le_antisymm (infi_le _ _) (le_infi $ assume h, le_refl _)

@[simp] lemma infi_neg {p : Prop} {f : p → α} (hp : ¬ p) : (⨅ h : p, f h) = ⊤ :=
le_antisymm le_top $ le_infi $ assume h, (hp h).elim

@[simp] lemma supr_pos {p : Prop} {f : p → α} (hp : p) : (⨆ h : p, f h) = f hp :=
le_antisymm (supr_le $ assume h, le_refl _) (le_supr _ _)

@[simp] lemma supr_neg {p : Prop} {f : p → α} (hp : ¬ p) : (⨆ h : p, f h) = ⊥ :=
le_antisymm (supr_le $ assume h, (hp h).elim) bot_le

lemma supr_eq_dif {p : Prop} [decidable p] (a : p → α) :
  (⨆h:p, a h) = (if h : p then a h else ⊥) :=
by by_cases p; simp [h]

lemma supr_eq_if {p : Prop} [decidable p] (a : α) :
  (⨆h:p, a) = (if p then a else ⊥) :=
by rw [supr_eq_dif, dif_eq_if]

lemma infi_eq_dif {p : Prop} [decidable p] (a : p → α) :
  (⨅h:p, a h) = (if h : p then a h else ⊤) :=
by by_cases p; simp [h]

lemma infi_eq_if {p : Prop} [decidable p] (a : α) :
  (⨅h:p, a) = (if p then a else ⊤) :=
by rw [infi_eq_dif, dif_eq_if]

-- TODO: should this be @[simp]?
theorem infi_comm {f : ι → ι₂ → α} : (⨅i, ⨅j, f i j) = (⨅j, ⨅i, f i j) :=
le_antisymm
  (le_infi $ assume i, le_infi $ assume j, infi_le_of_le j $ infi_le _ i)
  (le_infi $ assume j, le_infi $ assume i, infi_le_of_le i $ infi_le _ j)

/- TODO: this is strange. In the proof below, we get exactly the desired
   among the equalities, but close does not get it.
begin
  apply @le_antisymm,
    simp, intros,
    begin [smt]
      ematch, ematch, ematch, trace_state, have := le_refl (f i_1 i),
      trace_state, close
    end
end
-/

-- TODO: should this be @[simp]?
theorem supr_comm {f : ι → ι₂ → α} : (⨆i, ⨆j, f i j) = (⨆j, ⨆i, f i j) :=
le_antisymm
  (supr_le $ assume i, supr_le $ assume j, le_supr_of_le j $ le_supr _ i)
  (supr_le $ assume j, supr_le $ assume i, le_supr_of_le i $ le_supr _ j)

@[simp] theorem infi_infi_eq_left {b : β} {f : Πx:β, x = b → α} : (⨅x, ⨅h:x = b, f x h) = f b rfl :=
le_antisymm
  (infi_le_of_le b $ infi_le _ rfl)
  (le_infi $ assume b', le_infi $ assume eq, match b', eq with ._, rfl := le_refl _ end)

@[simp] theorem infi_infi_eq_right {b : β} {f : Πx:β, b = x → α} : (⨅x, ⨅h:b = x, f x h) = f b rfl :=
le_antisymm
  (infi_le_of_le b $ infi_le _ rfl)
  (le_infi $ assume b', le_infi $ assume eq, match b', eq with ._, rfl := le_refl _ end)

@[simp] theorem supr_supr_eq_left {b : β} {f : Πx:β, x = b → α} : (⨆x, ⨆h : x = b, f x h) = f b rfl :=
le_antisymm
  (supr_le $ assume b', supr_le $ assume eq, match b', eq with ._, rfl := le_refl _ end)
  (le_supr_of_le b $ le_supr _ rfl)

@[simp] theorem supr_supr_eq_right {b : β} {f : Πx:β, b = x → α} : (⨆x, ⨆h : b = x, f x h) = f b rfl :=
le_antisymm
  (supr_le $ assume b', supr_le $ assume eq, match b', eq with ._, rfl := le_refl _ end)
  (le_supr_of_le b $ le_supr _ rfl)

attribute [ematch] le_refl

theorem infi_inf_eq {f g : ι → α} : (⨅ x, f x ⊓ g x) = (⨅ x, f x) ⊓ (⨅ x, g x) :=
le_antisymm
  (le_inf
    (le_infi $ assume i, infi_le_of_le i inf_le_left)
    (le_infi $ assume i, infi_le_of_le i inf_le_right))
  (le_infi $ assume i, le_inf
    (inf_le_left_of_le $ infi_le _ _)
    (inf_le_right_of_le $ infi_le _ _))

/- TODO: here is another example where more flexible pattern matching
   might help.

begin
  apply @le_antisymm,
  safe, pose h := f a ⊓ g a, begin [smt] ematch, ematch  end
end
-/

lemma infi_inf {f : ι → α} {a : α} (i : ι) : (⨅x, f x) ⊓ a = (⨅ x, f x ⊓ a) :=
le_antisymm
  (le_infi $ assume i, le_inf (inf_le_left_of_le $ infi_le _ _) inf_le_right)
  (le_inf (infi_le_infi $ assume i, inf_le_left) (infi_le_of_le i inf_le_right))

lemma inf_infi {f : ι → α} {a : α} (i : ι) : a ⊓ (⨅x, f x) = (⨅ x, a ⊓ f x) :=
by rw [inf_comm, infi_inf i]; simp [inf_comm]

lemma binfi_inf {ι : Sort*} {p : ι → Prop}
  {f : Πi, p i → α} {a : α} {i : ι} (hi : p i) :
  (⨅i (h : p i), f i h) ⊓ a = (⨅ i (h : p i), f i h ⊓ a) :=
le_antisymm
  (le_infi $ assume i, le_infi $ assume hi,
    le_inf (inf_le_left_of_le $ infi_le_of_le i $ infi_le _ _) inf_le_right)
  (le_inf (infi_le_infi $ assume i, infi_le_infi $ assume hi, inf_le_left)
     (infi_le_of_le i $ infi_le_of_le hi $ inf_le_right))

theorem supr_sup_eq {f g : β → α} : (⨆ x, f x ⊔ g x) = (⨆ x, f x) ⊔ (⨆ x, g x) :=
le_antisymm
  (supr_le $ assume i, sup_le
    (le_sup_left_of_le $ le_supr _ _)
    (le_sup_right_of_le $ le_supr _ _))
  (sup_le
    (supr_le $ assume i, le_supr_of_le i le_sup_left)
    (supr_le $ assume i, le_supr_of_le i le_sup_right))

/- supr and infi under Prop -/

@[simp] theorem infi_false {s : false → α} : infi s = ⊤ :=
le_antisymm le_top (le_infi $ assume i, false.elim i)

@[simp] theorem supr_false {s : false → α} : supr s = ⊥ :=
le_antisymm (supr_le $ assume i, false.elim i) bot_le

@[simp] theorem infi_true {s : true → α} : infi s = s trivial :=
le_antisymm (infi_le _ _) (le_infi $ assume ⟨⟩, le_refl _)

@[simp] theorem supr_true {s : true → α} : supr s = s trivial :=
le_antisymm (supr_le $ assume ⟨⟩, le_refl _) (le_supr _ _)

@[simp] theorem infi_exists {p : ι → Prop} {f : Exists p → α} : (⨅ x, f x) = (⨅ i, ⨅ h:p i, f ⟨i, h⟩) :=
le_antisymm
  (le_infi $ assume i, le_infi $ assume : p i, infi_le _ _)
  (le_infi $ assume ⟨i, h⟩, infi_le_of_le i $ infi_le _ _)

@[simp] theorem supr_exists {p : ι → Prop} {f : Exists p → α} : (⨆ x, f x) = (⨆ i, ⨆ h:p i, f ⟨i, h⟩) :=
le_antisymm
  (supr_le $ assume ⟨i, h⟩, le_supr_of_le i $ le_supr (λh:p i, f ⟨i, h⟩) _)
  (supr_le $ assume i, supr_le $ assume : p i, le_supr _ _)

theorem infi_and {p q : Prop} {s : p ∧ q → α} : infi s = (⨅ h₁ h₂, s ⟨h₁, h₂⟩) :=
le_antisymm
  (le_infi $ assume i, le_infi $ assume j, infi_le _ _)
  (le_infi $ assume ⟨i, h⟩, infi_le_of_le i $ infi_le _ _)

theorem supr_and {p q : Prop} {s : p ∧ q → α} : supr s = (⨆ h₁ h₂, s ⟨h₁, h₂⟩) :=
le_antisymm
  (supr_le $ assume ⟨i, h⟩, le_supr_of_le i $ le_supr (λj, s ⟨i, j⟩) _)
  (supr_le $ assume i, supr_le $ assume j, le_supr _ _)

theorem infi_or {p q : Prop} {s : p ∨ q → α} :
  infi s = (⨅ h : p, s (or.inl h)) ⊓ (⨅ h : q, s (or.inr h)) :=
le_antisymm
  (le_inf
    (infi_le_infi2 $ assume j, ⟨_, le_refl _⟩)
    (infi_le_infi2 $ assume j, ⟨_, le_refl _⟩))
  (le_infi $ assume i, match i with
  | or.inl i := inf_le_left_of_le $ infi_le _ _
  | or.inr j := inf_le_right_of_le $ infi_le _ _
  end)

theorem supr_or {p q : Prop} {s : p ∨ q → α} :
  (⨆ x, s x) = (⨆ i, s (or.inl i)) ⊔ (⨆ j, s (or.inr j)) :=
le_antisymm
  (supr_le $ assume s, match s with
  | or.inl i := le_sup_left_of_le $ le_supr _ i
  | or.inr j := le_sup_right_of_le $ le_supr _ j
  end)
  (sup_le
    (supr_le_supr2 $ assume i, ⟨or.inl i, le_refl _⟩)
    (supr_le_supr2 $ assume j, ⟨or.inr j, le_refl _⟩))

lemma Sup_range {α : Type u} [has_Sup α] {f : ι → α} : Sup (range f) = supr f := rfl

lemma Inf_range {α : Type u} [has_Inf α] {f : ι → α} : Inf (range f) = infi f := rfl

lemma supr_range {g : β → α} {f : ι → β} : (⨆b∈range f, g b) = (⨆i, g (f i)) :=
le_antisymm
  (supr_le $ assume b, supr_le $ assume ⟨i, (h : f i = b)⟩, h ▸ le_supr _ i)
  (supr_le $ assume i, le_supr_of_le (f i) $ le_supr (λp, g (f i)) (mem_range_self _))

lemma infi_range {g : β → α} {f : ι → β} : (⨅b∈range f, g b) = (⨅i, g (f i)) :=
le_antisymm
  (le_infi $ assume i, infi_le_of_le (f i) $ infi_le (λp, g (f i)) (mem_range_self _))
  (le_infi $ assume b, le_infi $ assume ⟨i, (h : f i = b)⟩, h ▸ infi_le _ i)

theorem Inf_image {s : set β} {f : β → α} : Inf (f '' s) = (⨅ a ∈ s, f a) :=
calc Inf (set.image f s) = (⨅a, ⨅h : ∃b, b ∈ s ∧ f b = a, a) : Inf_eq_infi
                     ... = (⨅a, ⨅b, ⨅h : f b = a ∧ b ∈ s, a) : by simp [and_comm]
                     ... = (⨅a, ⨅b, ⨅h : a = f b, ⨅h : b ∈ s, a) : by simp [infi_and, eq_comm]
                     ... = (⨅b, ⨅a, ⨅h : a = f b, ⨅h : b ∈ s, a) : by rw [infi_comm]
                     ... = (⨅a∈s, f a) : congr_arg infi $ by funext x; rw [infi_infi_eq_left]

theorem Sup_image {s : set β} {f : β → α} : Sup (f '' s) = (⨆ a ∈ s, f a) :=
calc Sup (set.image f s) = (⨆a, ⨆h : ∃b, b ∈ s ∧ f b = a, a) : Sup_eq_supr
                     ... = (⨆a, ⨆b, ⨆h : f b = a ∧ b ∈ s, a) : by simp [and_comm]
                     ... = (⨆a, ⨆b, ⨆h : a = f b, ⨆h : b ∈ s, a) : by simp [supr_and, eq_comm]
                     ... = (⨆b, ⨆a, ⨆h : a = f b, ⨆h : b ∈ s, a) : by rw [supr_comm]
                     ... = (⨆a∈s, f a) : congr_arg supr $ by funext x; rw [supr_supr_eq_left]

/- supr and infi under set constructions -/

theorem infi_emptyset {f : β → α} : (⨅ x ∈ (∅ : set β), f x) = ⊤ :=
by simp

theorem supr_emptyset {f : β → α} : (⨆ x ∈ (∅ : set β), f x) = ⊥ :=
by simp

theorem infi_univ {f : β → α} : (⨅ x ∈ (univ : set β), f x) = (⨅ x, f x) :=
by simp

theorem supr_univ {f : β → α} : (⨆ x ∈ (univ : set β), f x) = (⨆ x, f x) :=
by simp

theorem infi_union {f : β → α} {s t : set β} : (⨅ x ∈ s ∪ t, f x) = (⨅x∈s, f x) ⊓ (⨅x∈t, f x) :=
calc (⨅ x ∈ s ∪ t, f x) = (⨅ x, (⨅h : x∈s, f x) ⊓ (⨅h : x∈t, f x)) : congr_arg infi $ funext $ assume x, infi_or
                    ... = (⨅x∈s, f x) ⊓ (⨅x∈t, f x) : infi_inf_eq

theorem infi_le_infi_of_subset {f : β → α} {s t : set β} (h : s ⊆ t) :
  (⨅ x ∈ t, f x) ≤ (⨅ x ∈ s, f x) :=
by rw [(union_eq_self_of_subset_left h).symm, infi_union]; exact inf_le_left

theorem supr_union {f : β → α} {s t : set β} : (⨆ x ∈ s ∪ t, f x) = (⨆x∈s, f x) ⊔ (⨆x∈t, f x) :=
calc (⨆ x ∈ s ∪ t, f x) = (⨆ x, (⨆h : x∈s, f x) ⊔ (⨆h : x∈t, f x)) : congr_arg supr $ funext $ assume x, supr_or
                    ... = (⨆x∈s, f x) ⊔ (⨆x∈t, f x) : supr_sup_eq

theorem supr_le_supr_of_subset {f : β → α} {s t : set β} (h : s ⊆ t) :
  (⨆ x ∈ s, f x) ≤ (⨆ x ∈ t, f x) :=
by rw [(union_eq_self_of_subset_left h).symm, supr_union]; exact le_sup_left

theorem infi_insert {f : β → α} {s : set β} {b : β} : (⨅ x ∈ insert b s, f x) = f b ⊓ (⨅x∈s, f x) :=
eq.trans infi_union $ congr_arg (λx:α, x ⊓ (⨅x∈s, f x)) infi_infi_eq_left

theorem supr_insert {f : β → α} {s : set β} {b : β} : (⨆ x ∈ insert b s, f x) = f b ⊔ (⨆x∈s, f x) :=
eq.trans supr_union $ congr_arg (λx:α, x ⊔ (⨆x∈s, f x)) supr_supr_eq_left

theorem infi_singleton {f : β → α} {b : β} : (⨅ x ∈ (singleton b : set β), f x) = f b :=
by simp

theorem infi_pair {f : β → α} {a b : β} : (⨅ x ∈ ({a, b} : set β), f x) = f a ⊓ f b :=
by rw [infi_insert, infi_singleton]

theorem supr_singleton {f : β → α} {b : β} : (⨆ x ∈ (singleton b : set β), f x) = f b :=
by simp

theorem supr_pair {f : β → α} {a b : β} : (⨆ x ∈ ({a, b} : set β), f x) = f a ⊔ f b :=
by rw [supr_insert, supr_singleton]

lemma infi_image {γ} {f : β → γ} {g : γ → α} {t : set β} :
  (⨅ c ∈ f '' t, g c) = (⨅ b ∈ t, g (f b)) :=
le_antisymm
  (le_infi $ assume b, le_infi $ assume hbt,
    infi_le_of_le (f b) $ infi_le (λ_, g (f b)) (mem_image_of_mem f hbt))
  (le_infi $ assume c, le_infi $ assume ⟨b, hbt, eq⟩,
    eq ▸ infi_le_of_le b $ infi_le (λ_, g (f b)) hbt)

lemma supr_image {γ} {f : β → γ} {g : γ → α} {t : set β} :
  (⨆ c ∈ f '' t, g c) = (⨆ b ∈ t, g (f b)) :=
le_antisymm
  (supr_le $ assume c, supr_le $ assume ⟨b, hbt, eq⟩,
    eq ▸ le_supr_of_le b $ le_supr (λ_, g (f b)) hbt)
  (supr_le $ assume b, supr_le $ assume hbt,
    le_supr_of_le (f b) $ le_supr (λ_, g (f b)) (mem_image_of_mem f hbt))

/- supr and infi under Type -/

@[simp] theorem infi_empty {s : empty → α} : infi s = ⊤ :=
le_antisymm le_top (le_infi $ assume i, empty.rec_on _ i)

@[simp] theorem supr_empty {s : empty → α} : supr s = ⊥ :=
le_antisymm (supr_le $ assume i, empty.rec_on _ i) bot_le

@[simp] theorem infi_unit {f : unit → α} : (⨅ x, f x) = f () :=
le_antisymm (infi_le _ _) (le_infi $ assume ⟨⟩, le_refl _)

@[simp] theorem supr_unit {f : unit → α} : (⨆ x, f x) = f () :=
le_antisymm (supr_le $ assume ⟨⟩, le_refl _) (le_supr _ _)

lemma supr_bool_eq {f : bool → α} : (⨆b:bool, f b) = f tt ⊔ f ff :=
le_antisymm
  (supr_le $ assume b, match b with tt := le_sup_left | ff := le_sup_right end)
  (sup_le (le_supr _ _) (le_supr _ _))

lemma infi_bool_eq {f : bool → α} : (⨅b:bool, f b) = f tt ⊓ f ff :=
le_antisymm
  (le_inf (infi_le _ _) (infi_le _ _))
  (le_infi $ assume b, match b with tt := inf_le_left | ff := inf_le_right end)

theorem infi_subtype {p : ι → Prop} {f : subtype p → α} : (⨅ x, f x) = (⨅ i (h:p i), f ⟨i, h⟩) :=
le_antisymm
  (le_infi $ assume i, le_infi $ assume : p i, infi_le _ _)
  (le_infi $ assume ⟨i, h⟩, infi_le_of_le i $ infi_le _ _)

lemma infi_subtype' {p : ι → Prop} {f : ∀ i, p i → α} :
  (⨅ i (h : p i), f i h) = (⨅ x : subtype p, f x.val x.property) :=
(@infi_subtype _ _ _ p (λ x, f x.val x.property)).symm

lemma infi_subtype'' {ι} (s : set ι) (f : ι → α) :
(⨅ i : s, f i) = ⨅ (t : ι) (H : t ∈ s), f t :=
infi_subtype

lemma is_glb_binfi {s : set β} {f : β → α} : is_glb (f '' s) (⨅ x ∈ s, f x) :=
by simpa only [range_comp, subtype.range_val, infi_subtype'] using @is_glb_infi α s _ (f ∘ subtype.val)

theorem supr_subtype {p : ι → Prop} {f : subtype p → α} : (⨆ x, f x) = (⨆ i (h:p i), f ⟨i, h⟩) :=
le_antisymm
  (supr_le $ assume ⟨i, h⟩, le_supr_of_le i $ le_supr (λh:p i, f ⟨i, h⟩) _)
  (supr_le $ assume i, supr_le $ assume : p i, le_supr _ _)

lemma supr_subtype' {p : ι → Prop} {f : ∀ i, p i → α} :
  (⨆ i (h : p i), f i h) = (⨆ x : subtype p, f x.val x.property) :=
(@supr_subtype _ _ _ p (λ x, f x.val x.property)).symm

lemma is_lub_bsupr {s : set β} {f : β → α} : is_lub (f '' s) (⨆ x ∈ s, f x) :=
by simpa only [range_comp, subtype.range_val, supr_subtype'] using @is_lub_supr α s _ (f ∘ subtype.val)

theorem infi_sigma {p : β → Type w} {f : sigma p → α} : (⨅ x, f x) = (⨅ i (h:p i), f ⟨i, h⟩) :=
le_antisymm
  (le_infi $ assume i, le_infi $ assume : p i, infi_le _ _)
  (le_infi $ assume ⟨i, h⟩, infi_le_of_le i $ infi_le _ _)

theorem supr_sigma {p : β → Type w} {f : sigma p → α} : (⨆ x, f x) = (⨆ i (h:p i), f ⟨i, h⟩) :=
le_antisymm
  (supr_le $ assume ⟨i, h⟩, le_supr_of_le i $ le_supr (λh:p i, f ⟨i, h⟩) _)
  (supr_le $ assume i, supr_le $ assume : p i, le_supr _ _)

theorem infi_prod {γ : Type w} {f : β × γ → α} : (⨅ x, f x) = (⨅ i j, f (i, j)) :=
le_antisymm
  (le_infi $ assume i, le_infi $ assume j, infi_le _ _)
  (le_infi $ assume ⟨i, h⟩, infi_le_of_le i $ infi_le _ _)

theorem supr_prod {γ : Type w} {f : β × γ → α} : (⨆ x, f x) = (⨆ i j, f (i, j)) :=
le_antisymm
  (supr_le $ assume ⟨i, h⟩, le_supr_of_le i $ le_supr (λj, f ⟨i, j⟩) _)
  (supr_le $ assume i, supr_le $ assume j, le_supr _ _)

theorem infi_sum {γ : Type w} {f : β ⊕ γ → α} :
  (⨅ x, f x) = (⨅ i, f (sum.inl i)) ⊓ (⨅ j, f (sum.inr j)) :=
le_antisymm
  (le_inf
    (infi_le_infi2 $ assume i, ⟨_, le_refl _⟩)
    (infi_le_infi2 $ assume j, ⟨_, le_refl _⟩))
  (le_infi $ assume s, match s with
  | sum.inl i := inf_le_left_of_le $ infi_le _ _
  | sum.inr j := inf_le_right_of_le $ infi_le _ _
  end)

theorem supr_sum {γ : Type w} {f : β ⊕ γ → α} :
  (⨆ x, f x) = (⨆ i, f (sum.inl i)) ⊔ (⨆ j, f (sum.inr j)) :=
le_antisymm
  (supr_le $ assume s, match s with
  | sum.inl i := le_sup_left_of_le $ le_supr _ i
  | sum.inr j := le_sup_right_of_le $ le_supr _ j
  end)
  (sup_le
    (supr_le_supr2 $ assume i, ⟨sum.inl i, le_refl _⟩)
    (supr_le_supr2 $ assume j, ⟨sum.inr j, le_refl _⟩))

end

section complete_linear_order
variables [complete_linear_order α]

lemma supr_eq_top (f : ι → α) : supr f = ⊤ ↔ (∀b<⊤, ∃i, b < f i) :=
by rw [← Sup_range, Sup_eq_top];
from forall_congr (assume b, forall_congr (assume hb, set.exists_range_iff))

@[nolint ge_or_gt] -- see Note [nolint_ge]
lemma infi_eq_bot (f : ι → α) : infi f = ⊥ ↔ (∀b>⊥, ∃i, b > f i) :=
by rw [← Inf_range, Inf_eq_bot];
from forall_congr (assume b, forall_congr (assume hb, set.exists_range_iff))

end complete_linear_order

/- Instances -/

instance complete_lattice_Prop : complete_lattice Prop :=
{ Sup    := λs, ∃a∈s, a,
  le_Sup := assume s a h p, ⟨a, h, p⟩,
  Sup_le := assume s a h ⟨b, h', p⟩, h b h' p,
  Inf    := λs, ∀a:Prop, a∈s → a,
  Inf_le := assume s a h p, p a h,
  le_Inf := assume s a h p b hb, h b hb p,
  ..bounded_lattice_Prop }

lemma Inf_Prop_eq {s : set Prop} : Inf s = (∀p ∈ s, p) := rfl

lemma Sup_Prop_eq {s : set Prop} : Sup s = (∃p ∈ s, p) := rfl

lemma infi_Prop_eq {ι : Sort*} {p : ι → Prop} : (⨅i, p i) = (∀i, p i) :=
le_antisymm (assume h i, h _ ⟨i, rfl⟩ ) (assume h p ⟨i, eq⟩, eq ▸ h i)

lemma supr_Prop_eq {ι : Sort*} {p : ι → Prop} : (⨆i, p i) = (∃i, p i) :=
le_antisymm (assume ⟨q, ⟨i, (eq : p i = q)⟩, hq⟩, ⟨i, eq.symm ▸ hq⟩) (assume ⟨i, hi⟩, ⟨p i, ⟨i, rfl⟩, hi⟩)

instance pi.complete_lattice {α : Type u} {β : α → Type v} [∀ i, complete_lattice (β i)] :
  complete_lattice (Π i, β i) :=
by { pi_instance;
     { intros, intro,
       apply_field, intros,
       simp at H, rcases H with ⟨ x, H₀, H₁ ⟩,
       subst b, apply a_1 _ H₀ i, } }

lemma Inf_apply
  {α : Type u} {β : α → Type v} [∀ i, complete_lattice (β i)] {s : set (Πa, β a)} {a : α} :
  (Inf s) a = (⨅f∈s, (f : Πa, β a) a) :=
by rw [← Inf_image]; refl

lemma infi_apply {α : Type u} {β : α → Type v} {ι : Sort*} [∀ i, complete_lattice (β i)]
  {f : ι → Πa, β a} {a : α} : (⨅i, f i) a = (⨅i, f i a) :=
by erw [← Inf_range, Inf_apply, infi_range]

lemma Sup_apply
  {α : Type u} {β : α → Type v} [∀ i, complete_lattice (β i)] {s : set (Πa, β a)} {a : α} :
  (Sup s) a = (⨆f∈s, (f : Πa, β a) a) :=
by rw [← Sup_image]; refl

lemma supr_apply {α : Type u} {β : α → Type v} {ι : Sort*} [∀ i, complete_lattice (β i)]
  {f : ι → Πa, β a} {a : α} : (⨆i, f i) a = (⨆i, f i a) :=
by erw [← Sup_range, Sup_apply, supr_range]

section complete_lattice
variables [preorder α] [complete_lattice β]

theorem monotone_Sup_of_monotone {s : set (α → β)} (m_s : ∀f∈s, monotone f) : monotone (Sup s) :=
assume x y h, Sup_le $ assume x' ⟨f, f_in, fx_eq⟩, le_Sup_of_le ⟨f, f_in, rfl⟩ $ fx_eq ▸ m_s _ f_in h

theorem monotone_Inf_of_monotone {s : set (α → β)} (m_s : ∀f∈s, monotone f) : monotone (Inf s) :=
assume x y h, le_Inf $ assume x' ⟨f, f_in, fx_eq⟩, Inf_le_of_le ⟨f, f_in, rfl⟩ $ fx_eq ▸ m_s _ f_in h

end complete_lattice

namespace order_dual
variable (α)

instance [has_Inf α] : has_Sup (order_dual α) := ⟨(Inf : set α → α)⟩
instance [has_Sup α] : has_Inf (order_dual α) := ⟨(Sup : set α → α)⟩

instance [complete_lattice α] : complete_lattice (order_dual α) :=
{ le_Sup := @complete_lattice.Inf_le α _,
  Sup_le := @complete_lattice.le_Inf α _,
  Inf_le := @complete_lattice.le_Sup α _,
  le_Inf := @complete_lattice.Sup_le α _,
  .. order_dual.bounded_lattice α, ..order_dual.has_Sup α, ..order_dual.has_Inf α }

instance [complete_linear_order α] : complete_linear_order (order_dual α) :=
{ .. order_dual.complete_lattice α, .. order_dual.decidable_linear_order α }

end order_dual

namespace prod
variables (α β)

instance [has_Inf α] [has_Inf β] : has_Inf (α × β) :=
⟨λs, (Inf (prod.fst '' s), Inf (prod.snd '' s))⟩

instance [has_Sup α] [has_Sup β] : has_Sup (α × β) :=
⟨λs, (Sup (prod.fst '' s), Sup (prod.snd '' s))⟩

instance [complete_lattice α] [complete_lattice β] : complete_lattice (α × β) :=
{ le_Sup := assume s p hab, ⟨le_Sup $ mem_image_of_mem _ hab, le_Sup $ mem_image_of_mem _ hab⟩,
  Sup_le := assume s p h,
    ⟨ Sup_le $ ball_image_of_ball $ assume p hp, (h p hp).1,
      Sup_le $ ball_image_of_ball $ assume p hp, (h p hp).2⟩,
  Inf_le := assume s p hab, ⟨Inf_le $ mem_image_of_mem _ hab, Inf_le $ mem_image_of_mem _ hab⟩,
  le_Inf := assume s p h,
    ⟨ le_Inf $ ball_image_of_ball $ assume p hp, (h p hp).1,
      le_Inf $ ball_image_of_ball $ assume p hp, (h p hp).2⟩,
  .. prod.bounded_lattice α β,
  .. prod.has_Sup α β,
  .. prod.has_Inf α β }

end prod
