/-
Copyright (c) 2016 Jeremy Avigad. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jeremy Avigad, Leonardo de Moura
-/
import tactic.doc_commands

/-!
# Basic logic properties

This file is one of the earliest imports in mathlib.

## Implementation notes

Theorems that require decidability hypotheses are in the namespace "decidable".
Classical versions are in the namespace "classical".

In the presence of automation, this whole file may be unnecessary. On the other hand,
maybe it is useful for writing automation.
-/

section miscellany

/- We add the `inline` attribute to optimize VM computation using these declarations. For example,
  `if p ∧ q then ... else ...` will not evaluate the decidability of `q` if `p` is false. -/
attribute [inline] and.decidable or.decidable decidable.false xor.decidable iff.decidable
  decidable.true implies.decidable not.decidable ne.decidable
  bool.decidable_eq decidable.to_bool

variables {α : Type*} {β : Type*}

@[reducible] def hidden {α : Sort*} {a : α} := a

def empty.elim {C : Sort*} : empty → C.

instance : subsingleton empty := ⟨λa, a.elim⟩

instance : decidable_eq empty := λa, a.elim

instance sort.inhabited : inhabited (Sort*) := ⟨punit⟩
instance sort.inhabited' : inhabited (default (Sort*)) := ⟨punit.star⟩

instance psum.inhabited_left {α β} [inhabited α] : inhabited (psum α β) := ⟨psum.inl (default _)⟩
instance psum.inhabited_right {α β} [inhabited β] : inhabited (psum α β) := ⟨psum.inr (default _)⟩

@[priority 10] instance decidable_eq_of_subsingleton
  {α} [subsingleton α] : decidable_eq α
| a b := is_true (subsingleton.elim a b)

/-- Add an instance to "undo" coercion transitivity into a chain of coercions, because
   most simp lemmas are stated with respect to simple coercions and will not match when
   part of a chain. -/
@[simp] theorem coe_coe {α β γ} [has_coe α β] [has_coe_t β γ]
  (a : α) : (a : γ) = (a : β) := rfl

theorem coe_fn_coe_trans
  {α β γ} [has_coe α β] [has_coe_t_aux β γ] [has_coe_to_fun γ]
  (x : α) : @coe_fn α _ x = @coe_fn β _ x := rfl

@[simp] theorem coe_fn_coe_base
  {α β} [has_coe α β] [has_coe_to_fun β]
  (x : α) : @coe_fn α _ x = @coe_fn β _ x := rfl

theorem coe_sort_coe_trans
  {α β γ} [has_coe α β] [has_coe_t_aux β γ] [has_coe_to_sort γ]
  (x : α) : @coe_sort α _ x = @coe_sort β _ x := rfl

/--
Many structures such as bundled morphisms coerce to functions so that you can
transparently apply them to arguments. For example, if `e : α ≃ β` and `a : α`
then you can write `e a` and this is elaborated as `⇑e a`. This type of
coercion is implemented using the `has_coe_to_fun`type class. There is one
important consideration:

If a type coerces to another type which in turn coerces to a function,
then it **must** implement `has_coe_to_fun` directly:
```lean
structure sparkling_equiv (α β) extends α ≃ β

-- if we add a `has_coe` instance,
instance {α β} : has_coe (sparkling_equiv α β) (α ≃ β) :=
⟨sparkling_equiv.to_equiv⟩

-- then a `has_coe_to_fun` instance **must** be added as well:
instance {α β} : has_coe_to_fun (sparkling_equiv α β) :=
⟨λ _, α → β, λ f, f.to_equiv.to_fun⟩
```

(Rationale: if we do not declare the direct coercion, then `⇑e a` is not in
simp-normal form. The lemma `coe_fn_coe_base` will unfold it to `⇑↑e a`. This
often causes loops in the simplifier.)
-/
library_note "function coercion"

@[simp] theorem coe_sort_coe_base
  {α β} [has_coe α β] [has_coe_to_sort β]
  (x : α) : @coe_sort α _ x = @coe_sort β _ x := rfl

/-- `pempty` is the universe-polymorphic analogue of `empty`. -/
@[derive decidable_eq]
inductive {u} pempty : Sort u

def pempty.elim {C : Sort*} : pempty → C.

instance subsingleton_pempty : subsingleton pempty := ⟨λa, a.elim⟩

@[simp] lemma not_nonempty_pempty : ¬ nonempty pempty :=
assume ⟨h⟩, h.elim

@[simp] theorem forall_pempty {P : pempty → Prop} : (∀ x : pempty, P x) ↔ true :=
⟨λ h, trivial, λ h x, by cases x⟩

@[simp] theorem exists_pempty {P : pempty → Prop} : (∃ x : pempty, P x) ↔ false :=
⟨λ h, by { cases h with w, cases w }, false.elim⟩

lemma congr_arg_heq {α} {β : α → Sort*} (f : ∀ a, β a) : ∀ {a₁ a₂ : α}, a₁ = a₂ → f a₁ == f a₂
| a _ rfl := heq.rfl

lemma plift.down_inj {α : Sort*} : ∀ (a b : plift α), a.down = b.down → a = b
| ⟨a⟩ ⟨b⟩ rfl := rfl

-- missing [symm] attribute for ne in core.
attribute [symm] ne.symm

lemma ne_comm {α} {a b : α} : a ≠ b ↔ b ≠ a := ⟨ne.symm, ne.symm⟩

@[simp] lemma eq_iff_eq_cancel_left {b c : α} :
  (∀ {a}, a = b ↔ a = c) ↔ (b = c) :=
⟨λ h, by rw [← h], λ h a, by rw h⟩

@[simp] lemma eq_iff_eq_cancel_right {a b : α} :
  (∀ {c}, a = c ↔ b = c) ↔ (a = b) :=
⟨λ h, by rw h, λ h a, by rw h⟩

/-- Wrapper for adding elementary propositions to the type class systems.
Warning: this can easily be abused. See the rest of this docstring for details.

Certain propositions should not be treated as a class globally,
but sometimes it is very convenient to be able to use the type class system
in specific circumstances.

For example, `zmod p` is a field if and only if `p` is a prime number.
In order to be able to find this field instance automatically by type class search,
we have to turn `p.prime` into an instance implicit assumption.

On the other hand, making `nat.prime` a class would require a major refactoring of the library,
and it is questionable whether making `nat.prime` a class is desirable at all.
The compromise is to add the assumption `[fact p.prime]` to `zmod.field`.

In particular, this class is not intended for turning the type class system
into an automated theorem prover for first order logic. -/
@[class]
def fact (p : Prop) := p

end miscellany

/-!
### Declarations about propositional connectives
-/

theorem false_ne_true : false ≠ true
| h := h.symm ▸ trivial

section propositional
variables {a b c d : Prop}

/-! ### Declarations about `implies` -/

theorem iff_of_eq (e : a = b) : a ↔ b := e ▸ iff.rfl

theorem iff_iff_eq : (a ↔ b) ↔ a = b := ⟨propext, iff_of_eq⟩

@[simp] lemma eq_iff_iff {p q : Prop} : (p = q) ↔ (p ↔ q) := iff_iff_eq.symm

@[simp] theorem imp_self : (a → a) ↔ true := iff_true_intro id

theorem imp_intro {α β : Prop} (h : α) : β → α := λ _, h

theorem imp_false : (a → false) ↔ ¬ a := iff.rfl

theorem imp_and_distrib {α} : (α → b ∧ c) ↔ (α → b) ∧ (α → c) :=
⟨λ h, ⟨λ ha, (h ha).left, λ ha, (h ha).right⟩,
 λ h ha, ⟨h.left ha, h.right ha⟩⟩

@[simp] theorem and_imp : (a ∧ b → c) ↔ (a → b → c) :=
iff.intro (λ h ha hb, h ⟨ha, hb⟩) (λ h ⟨ha, hb⟩, h ha hb)

theorem iff_def : (a ↔ b) ↔ (a → b) ∧ (b → a) :=
iff_iff_implies_and_implies _ _

theorem iff_def' : (a ↔ b) ↔ (b → a) ∧ (a → b) :=
iff_def.trans and.comm

theorem imp_true_iff {α : Sort*} : (α → true) ↔ true :=
iff_true_intro $ λ_, trivial

@[simp] theorem imp_iff_right (ha : a) : (a → b) ↔ b :=
⟨λf, f ha, imp_intro⟩

/-! ### Declarations about `not` -/

def not.elim {α : Sort*} (H1 : ¬a) (H2 : a) : α := absurd H2 H1

@[reducible] theorem not.imp {a b : Prop} (H2 : ¬b) (H1 : a → b) : ¬a := mt H1 H2

theorem not_not_of_not_imp : ¬(a → b) → ¬¬a :=
mt not.elim

theorem not_of_not_imp {a : Prop} : ¬(a → b) → ¬b :=
mt imp_intro

theorem dec_em (p : Prop) [decidable p] : p ∨ ¬p := decidable.em p

theorem by_contradiction {p} [decidable p] : (¬p → false) → p :=
decidable.by_contradiction

theorem not_not [decidable a] : ¬¬a ↔ a :=
iff.intro by_contradiction not_not_intro

theorem of_not_not [decidable a] : ¬¬a → a :=
by_contradiction

theorem of_not_imp [decidable a] (h : ¬ (a → b)) : a :=
by_contradiction (not_not_of_not_imp h)

theorem not.imp_symm [decidable a] (h : ¬a → b) (hb : ¬b) : a :=
by_contradiction $ hb ∘ h

theorem not_imp_comm [decidable a] [decidable b] : (¬a → b) ↔ (¬b → a) :=
⟨not.imp_symm, not.imp_symm⟩

theorem imp.swap : (a → b → c) ↔ (b → a → c) :=
⟨function.swap, function.swap⟩

theorem imp_not_comm : (a → ¬b) ↔ (b → ¬a) :=
imp.swap

/-! ### Declarations about `and` -/

theorem not_and_of_not_left (b : Prop) : ¬a → ¬(a ∧ b) :=
mt and.left

theorem not_and_of_not_right (a : Prop) {b : Prop} : ¬b → ¬(a ∧ b) :=
mt and.right

theorem and.imp_left (h : a → b) : a ∧ c → b ∧ c :=
and.imp h id

theorem and.imp_right (h : a → b) : c ∧ a → c ∧ b :=
and.imp id h

lemma and.right_comm : (a ∧ b) ∧ c ↔ (a ∧ c) ∧ b :=
by simp [and.left_comm, and.comm]

lemma and.rotate : a ∧ b ∧ c ↔ b ∧ c ∧ a :=
by simp [and.left_comm, and.comm]

theorem and_not_self_iff (a : Prop) : a ∧ ¬ a ↔ false :=
iff.intro (assume h, (h.right) (h.left)) (assume h, h.elim)

theorem not_and_self_iff (a : Prop) : ¬ a ∧ a ↔ false :=
iff.intro (assume ⟨hna, ha⟩, hna ha) false.elim

theorem and_iff_left_of_imp {a b : Prop} (h : a → b) : (a ∧ b) ↔ a :=
iff.intro and.left (λ ha, ⟨ha, h ha⟩)

theorem and_iff_right_of_imp {a b : Prop} (h : b → a) : (a ∧ b) ↔ b :=
iff.intro and.right (λ hb, ⟨h hb, hb⟩)

lemma and.congr_right_iff : (a ∧ b ↔ a ∧ c) ↔ (a → (b ↔ c)) :=
⟨λ h ha, by simp [ha] at h; exact h, and_congr_right⟩

@[simp] lemma and_self_left : a ∧ a ∧ b ↔ a ∧ b :=
⟨λ h, ⟨h.1, h.2.2⟩, λ h, ⟨h.1, h.1, h.2⟩⟩

@[simp] lemma and_self_right : (a ∧ b) ∧ b ↔ a ∧ b :=
⟨λ h, ⟨h.1.1, h.2⟩, λ h, ⟨⟨h.1, h.2⟩, h.2⟩⟩

/-! ### Declarations about `or` -/

theorem or_of_or_of_imp_of_imp (h₁ : a ∨ b) (h₂ : a → c) (h₃ : b → d) : c ∨ d :=
or.imp h₂ h₃ h₁

theorem or_of_or_of_imp_left (h₁ : a ∨ c) (h : a → b) : b ∨ c :=
or.imp_left h h₁

theorem or_of_or_of_imp_right (h₁ : c ∨ a) (h : a → b) : c ∨ b :=
or.imp_right h h₁

theorem or.elim3 (h : a ∨ b ∨ c) (ha : a → d) (hb : b → d) (hc : c → d) : d :=
or.elim h ha (assume h₂, or.elim h₂ hb hc)

theorem or_imp_distrib : (a ∨ b → c) ↔ (a → c) ∧ (b → c) :=
⟨assume h, ⟨assume ha, h (or.inl ha), assume hb, h (or.inr hb)⟩,
  assume ⟨ha, hb⟩, or.rec ha hb⟩

theorem or_iff_not_imp_left [decidable a] : a ∨ b ↔ (¬ a → b) :=
⟨or.resolve_left, λ h, dite _ or.inl (or.inr ∘ h)⟩

theorem or_iff_not_imp_right [decidable b] : a ∨ b ↔ (¬ b → a) :=
or.comm.trans or_iff_not_imp_left

theorem not_imp_not [decidable a] : (¬ a → ¬ b) ↔ (b → a) :=
⟨assume h hb, by_contradiction $ assume na, h na hb, mt⟩

/-! ### Declarations about distributivity -/

theorem and_or_distrib_left : a ∧ (b ∨ c) ↔ (a ∧ b) ∨ (a ∧ c) :=
⟨λ ⟨ha, hbc⟩, hbc.imp (and.intro ha) (and.intro ha),
 or.rec (and.imp_right or.inl) (and.imp_right or.inr)⟩

theorem or_and_distrib_right : (a ∨ b) ∧ c ↔ (a ∧ c) ∨ (b ∧ c) :=
(and.comm.trans and_or_distrib_left).trans (or_congr and.comm and.comm)

theorem or_and_distrib_left : a ∨ (b ∧ c) ↔ (a ∨ b) ∧ (a ∨ c) :=
⟨or.rec (λha, and.intro (or.inl ha) (or.inl ha)) (and.imp or.inr or.inr),
 and.rec $ or.rec (imp_intro ∘ or.inl) (or.imp_right ∘ and.intro)⟩

theorem and_or_distrib_right : (a ∧ b) ∨ c ↔ (a ∨ c) ∧ (b ∨ c) :=
(or.comm.trans or_and_distrib_left).trans (and_congr or.comm or.comm)

@[simp] lemma or_self_left : a ∨ a ∨ b ↔ a ∨ b :=
⟨λ h, h.elim or.inl id, λ h, h.elim or.inl (or.inr ∘ or.inr)⟩

@[simp] lemma or_self_right : (a ∨ b) ∨ b ↔ a ∨ b :=
⟨λ h, h.elim id or.inr, λ h, h.elim (or.inl ∘ or.inl) or.inr⟩

/-! Declarations about `iff` -/

theorem iff_of_true (ha : a) (hb : b) : a ↔ b :=
⟨λ_, hb, λ _, ha⟩

theorem iff_of_false (ha : ¬a) (hb : ¬b) : a ↔ b :=
⟨ha.elim, hb.elim⟩

theorem iff_true_left (ha : a) : (a ↔ b) ↔ b :=
⟨λ h, h.1 ha, iff_of_true ha⟩

theorem iff_true_right (ha : a) : (b ↔ a) ↔ b :=
iff.comm.trans (iff_true_left ha)

theorem iff_false_left (ha : ¬a) : (a ↔ b) ↔ ¬b :=
⟨λ h, mt h.2 ha, iff_of_false ha⟩

theorem iff_false_right (ha : ¬a) : (b ↔ a) ↔ ¬b :=
iff.comm.trans (iff_false_left ha)

theorem not_or_of_imp [decidable a] (h : a → b) : ¬ a ∨ b :=
if ha : a then or.inr (h ha) else or.inl ha

theorem imp_iff_not_or [decidable a] : (a → b) ↔ (¬ a ∨ b) :=
⟨not_or_of_imp, or.neg_resolve_left⟩

theorem imp_or_distrib [decidable a] : (a → b ∨ c) ↔ (a → b) ∨ (a → c) :=
by simp [imp_iff_not_or, or.comm, or.left_comm]

theorem imp_or_distrib' [decidable b] : (a → b ∨ c) ↔ (a → b) ∨ (a → c) :=
by by_cases b; simp [h, or_iff_right_of_imp ((∘) false.elim)]

theorem not_imp_of_and_not : a ∧ ¬ b → ¬ (a → b)
| ⟨ha, hb⟩ h := hb $ h ha

theorem not_imp [decidable a] : ¬(a → b) ↔ a ∧ ¬b :=
⟨λ h, ⟨of_not_imp h, not_of_not_imp h⟩, not_imp_of_and_not⟩

-- for monotonicity
lemma imp_imp_imp
  (h₀ : c → a) (h₁ : b → d) :
  (a → b) → (c → d) :=
assume (h₂ : a → b),
h₁ ∘ h₂ ∘ h₀

theorem peirce (a b : Prop) [decidable a] : ((a → b) → a) → a :=
if ha : a then λ h, ha else λ h, h ha.elim

theorem peirce' {a : Prop} (H : ∀ b : Prop, (a → b) → a) : a := H _ id

theorem not_iff_not [decidable a] [decidable b] : (¬ a ↔ ¬ b) ↔ (a ↔ b) :=
by rw [@iff_def (¬ a), @iff_def' a]; exact and_congr not_imp_not not_imp_not

theorem not_iff_comm [decidable a] [decidable b] : (¬ a ↔ b) ↔ (¬ b ↔ a) :=
by rw [@iff_def (¬ a), @iff_def (¬ b)]; exact and_congr not_imp_comm imp_not_comm

theorem not_iff [decidable b] : ¬ (a ↔ b) ↔ (¬ a ↔ b) :=
by split; intro h; [split, skip]; intro h'; [by_contradiction,intro,skip];
   try { refine h _; simp [*] }; rw [h',not_iff_self] at h; exact h

theorem iff_not_comm [decidable a] [decidable b] : (a ↔ ¬ b) ↔ (b ↔ ¬ a) :=
by rw [@iff_def a, @iff_def b]; exact and_congr imp_not_comm not_imp_comm

theorem iff_iff_and_or_not_and_not [decidable b] : (a ↔ b) ↔ (a ∧ b) ∨ (¬ a ∧ ¬ b) :=
by { split; intro h,
     { rw h; by_cases b; [left,right]; split; assumption },
     { cases h with h h; cases h; split; intro; { contradiction <|> assumption } } }

theorem not_and_not_right [decidable b] : ¬(a ∧ ¬b) ↔ (a → b) :=
⟨λ h ha, h.imp_symm $ and.intro ha, λ h ⟨ha, hb⟩, hb $ h ha⟩

@[inline] def decidable_of_iff (a : Prop) (h : a ↔ b) [D : decidable a] : decidable b :=
decidable_of_decidable_of_iff D h

@[inline] def decidable_of_iff' (b : Prop) (h : a ↔ b) [D : decidable b] : decidable a :=
decidable_of_decidable_of_iff D h.symm

def decidable_of_bool : ∀ (b : bool) (h : b ↔ a), decidable a
| tt h := is_true (h.1 rfl)
| ff h := is_false (mt h.2 bool.ff_ne_tt)

/-! ### De Morgan's laws -/

theorem not_and_of_not_or_not (h : ¬ a ∨ ¬ b) : ¬ (a ∧ b)
| ⟨ha, hb⟩ := or.elim h (absurd ha) (absurd hb)

theorem not_and_distrib [decidable a] : ¬ (a ∧ b) ↔ ¬a ∨ ¬b :=
⟨λ h, if ha : a then or.inr (λ hb, h ⟨ha, hb⟩) else or.inl ha, not_and_of_not_or_not⟩

theorem not_and_distrib' [decidable b] : ¬ (a ∧ b) ↔ ¬a ∨ ¬b :=
⟨λ h, if hb : b then or.inl (λ ha, h ⟨ha, hb⟩) else or.inr hb, not_and_of_not_or_not⟩

@[simp] theorem not_and : ¬ (a ∧ b) ↔ (a → ¬ b) := and_imp

theorem not_and' : ¬ (a ∧ b) ↔ b → ¬a :=
not_and.trans imp_not_comm

theorem not_or_distrib : ¬ (a ∨ b) ↔ ¬ a ∧ ¬ b :=
⟨λ h, ⟨λ ha, h (or.inl ha), λ hb, h (or.inr hb)⟩,
 λ ⟨h₁, h₂⟩ h, or.elim h h₁ h₂⟩

theorem or_iff_not_and_not [decidable a] [decidable b] : a ∨ b ↔ ¬ (¬a ∧ ¬b) :=
by rw [← not_or_distrib, not_not]

theorem and_iff_not_or_not [decidable a] [decidable b] : a ∧ b ↔ ¬ (¬ a ∨ ¬ b) :=
by rw [← not_and_distrib, not_not]

end propositional

/-! ### Declarations about equality -/

section equality
variables {α : Sort*} {a b : α}

@[simp] theorem heq_iff_eq : a == b ↔ a = b :=
⟨eq_of_heq, heq_of_eq⟩

theorem proof_irrel_heq {p q : Prop} (hp : p) (hq : q) : hp == hq :=
have p = q, from propext ⟨λ _, hq, λ _, hp⟩,
by subst q; refl

theorem ne_of_mem_of_not_mem {α β} [has_mem α β] {s : β} {a b : α}
  (h : a ∈ s) : b ∉ s → a ≠ b :=
mt $ λ e, e ▸ h

theorem eq_equivalence : equivalence (@eq α) :=
⟨eq.refl, @eq.symm _, @eq.trans _⟩

/-- Transport through trivial families is the identity. -/
@[simp]
lemma eq_rec_constant {α : Sort*} {a a' : α} {β : Sort*} (y : β) (h : a = a') :
  (@eq.rec α a (λ a, β) y a' h) = y :=
by { cases h, refl, }

@[simp]
lemma eq_mp_rfl {α : Sort*} {a : α} : eq.mp (eq.refl α) a = a := rfl

@[simp]
lemma eq_mpr_rfl {α : Sort*} {a : α} : eq.mpr (eq.refl α) a = a := rfl

lemma heq_of_eq_mp :
  ∀ {α β : Sort*} {a : α} {a' : β} (e : α = β) (h₂ : (eq.mp e a) = a'), a == a'
| α ._ a a' rfl h := eq.rec_on h (heq.refl _)

lemma rec_heq_of_heq {β} {C : α → Sort*} {x : C a} {y : β} (eq : a = b) (h : x == y) :
  @eq.rec α a C x b eq == y :=
by subst eq; exact h

@[simp] lemma {u} eq_mpr_heq {α β : Sort u} (h : β = α) (x : α) : eq.mpr h x == x :=
by subst h; refl

protected lemma eq.congr {x₁ x₂ y₁ y₂ : α} (h₁ : x₁ = y₁) (h₂ : x₂ = y₂) :
  (x₁ = x₂) ↔ (y₁ = y₂) :=
by { subst h₁, subst h₂ }

lemma eq.congr_left {x y z : α} (h : x = y) : x = z ↔ y = z := by rw [h]
lemma eq.congr_right {x y z : α} (h : x = y) : z = x ↔ z = y := by rw [h]

lemma congr_arg2 {α β γ : Type*} (f : α → β → γ) {x x' : α} {y y' : β}
  (hx : x = x') (hy : y = y') : f x y = f x' y' :=
by { subst hx, subst hy }

end equality

/-! ### Declarations about quantifiers -/

section quantifiers
variables {α : Sort*} {β : Sort*} {p q : α → Prop} {b : Prop}

lemma Exists.imp (h : ∀ a, (p a → q a)) (p : ∃ a, p a) : ∃ a, q a := exists_imp_exists h p

lemma exists_imp_exists' {p : α → Prop} {q : β → Prop} (f : α → β) (hpq : ∀ a, p a → q (f a))
  (hp : ∃ a, p a) : ∃ b, q b :=
exists.elim hp (λ a hp', ⟨_, hpq _ hp'⟩)

theorem forall_swap {p : α → β → Prop} : (∀ x y, p x y) ↔ ∀ y x, p x y :=
⟨function.swap, function.swap⟩

theorem exists_swap {p : α → β → Prop} : (∃ x y, p x y) ↔ ∃ y x, p x y :=
⟨λ ⟨x, y, h⟩, ⟨y, x, h⟩, λ ⟨y, x, h⟩, ⟨x, y, h⟩⟩

@[simp] theorem exists_imp_distrib : ((∃ x, p x) → b) ↔ ∀ x, p x → b :=
⟨λ h x hpx, h ⟨x, hpx⟩, λ h ⟨x, hpx⟩, h x hpx⟩

--theorem forall_not_of_not_exists (h : ¬ ∃ x, p x) : ∀ x, ¬ p x :=
--forall_imp_of_exists_imp h

theorem not_exists_of_forall_not (h : ∀ x, ¬ p x) : ¬ ∃ x, p x :=
exists_imp_distrib.2 h

@[simp] theorem not_exists : (¬ ∃ x, p x) ↔ ∀ x, ¬ p x :=
exists_imp_distrib

theorem not_forall_of_exists_not : (∃ x, ¬ p x) → ¬ ∀ x, p x
| ⟨x, hn⟩ h := hn (h x)

theorem not_forall {p : α → Prop}
    [decidable (∃ x, ¬ p x)] [∀ x, decidable (p x)] :
  (¬ ∀ x, p x) ↔ ∃ x, ¬ p x :=
⟨not.imp_symm $ λ nx x, nx.imp_symm $ λ h, ⟨x, h⟩,
 not_forall_of_exists_not⟩

theorem not_forall_not [decidable (∃ x, p x)] :
  (¬ ∀ x, ¬ p x) ↔ ∃ x, p x :=
(@not_iff_comm _ _ _ (decidable_of_iff (¬ ∃ x, p x) not_exists)).1 not_exists

theorem not_exists_not [∀ x, decidable (p x)] :
  (¬ ∃ x, ¬ p x) ↔ ∀ x, p x :=
by simp [not_not]

@[simp] theorem forall_true_iff : (α → true) ↔ true :=
iff_true_intro (λ _, trivial)

-- Unfortunately this causes simp to loop sometimes, so we
-- add the 2 and 3 cases as simp lemmas instead
theorem forall_true_iff' (h : ∀ a, p a ↔ true) : (∀ a, p a) ↔ true :=
iff_true_intro (λ _, of_iff_true (h _))

@[simp] theorem forall_2_true_iff {β : α → Sort*} : (∀ a, β a → true) ↔ true :=
forall_true_iff' $ λ _, forall_true_iff

@[simp] theorem forall_3_true_iff {β : α → Sort*} {γ : Π a, β a → Sort*} :
  (∀ a (b : β a), γ a b → true) ↔ true :=
forall_true_iff' $ λ _, forall_2_true_iff

@[simp] theorem forall_const (α : Sort*) [i : nonempty α] : (α → b) ↔ b :=
⟨i.elim, λ hb x, hb⟩

@[simp] theorem exists_const (α : Sort*) [i : nonempty α] : (∃ x : α, b) ↔ b :=
⟨λ ⟨x, h⟩, h, i.elim exists.intro⟩

theorem forall_and_distrib : (∀ x, p x ∧ q x) ↔ (∀ x, p x) ∧ (∀ x, q x) :=
⟨λ h, ⟨λ x, (h x).left, λ x, (h x).right⟩, λ ⟨h₁, h₂⟩ x, ⟨h₁ x, h₂ x⟩⟩

theorem exists_or_distrib : (∃ x, p x ∨ q x) ↔ (∃ x, p x) ∨ (∃ x, q x) :=
⟨λ ⟨x, hpq⟩, hpq.elim (λ hpx, or.inl ⟨x, hpx⟩) (λ hqx, or.inr ⟨x, hqx⟩),
 λ hepq, hepq.elim (λ ⟨x, hpx⟩, ⟨x, or.inl hpx⟩) (λ ⟨x, hqx⟩, ⟨x, or.inr hqx⟩)⟩

@[simp] theorem exists_and_distrib_left {q : Prop} {p : α → Prop} :
  (∃x, q ∧ p x) ↔ q ∧ (∃x, p x) :=
⟨λ ⟨x, hq, hp⟩, ⟨hq, x, hp⟩, λ ⟨hq, x, hp⟩, ⟨x, hq, hp⟩⟩

@[simp] theorem exists_and_distrib_right {q : Prop} {p : α → Prop} :
  (∃x, p x ∧ q) ↔ (∃x, p x) ∧ q :=
by simp [and_comm]

@[simp] theorem forall_eq {a' : α} : (∀a, a = a' → p a) ↔ p a' :=
⟨λ h, h a' rfl, λ h a e, e.symm ▸ h⟩

@[simp] theorem exists_eq {a' : α} : ∃ a, a = a' := ⟨_, rfl⟩

@[simp] theorem exists_eq' {a' : α} : Exists (eq a') := ⟨_, rfl⟩

@[simp] theorem exists_eq_left {a' : α} : (∃ a, a = a' ∧ p a) ↔ p a' :=
⟨λ ⟨a, e, h⟩, e ▸ h, λ h, ⟨_, rfl, h⟩⟩

@[simp] theorem exists_eq_right {a' : α} : (∃ a, p a ∧ a = a') ↔ p a' :=
(exists_congr $ by exact λ a, and.comm).trans exists_eq_left

@[simp] theorem exists_exists_and_eq_and {f : α → β} {p : α → Prop} {q : β → Prop} :
  (∃ b, (∃ a, p a ∧ f a = b) ∧ q b) ↔ ∃ a, p a ∧ q (f a) :=
⟨λ ⟨b, ⟨a, ha, hab⟩, hb⟩, ⟨a, ha, hab.symm ▸ hb⟩, λ ⟨a, hp, hq⟩, ⟨f a, ⟨a, hp, rfl⟩, hq⟩⟩

@[simp] theorem exists_exists_eq_and {f : α → β} {p : β → Prop} :
  (∃ b, (∃ a, f a = b) ∧ p b) ↔ ∃ a, p (f a) :=
⟨λ ⟨b, ⟨a, ha⟩, hb⟩, ⟨a, ha.symm ▸ hb⟩, λ ⟨a, ha⟩, ⟨f a, ⟨a, rfl⟩, ha⟩⟩

@[simp] theorem forall_eq' {a' : α} : (∀a, a' = a → p a) ↔ p a' :=
by simp [@eq_comm _ a']

@[simp] theorem exists_eq_left' {a' : α} : (∃ a, a' = a ∧ p a) ↔ p a' :=
by simp [@eq_comm _ a']

@[simp] theorem exists_eq_right' {a' : α} : (∃ a, p a ∧ a' = a) ↔ p a' :=
by simp [@eq_comm _ a']

theorem exists_comm {p : α → β → Prop} : (∃ a b, p a b) ↔ ∃ b a, p a b :=
⟨λ ⟨a, b, h⟩, ⟨b, a, h⟩, λ ⟨b, a, h⟩, ⟨a, b, h⟩⟩

theorem forall_or_of_or_forall (h : b ∨ ∀x, p x) (x) : b ∨ p x :=
h.imp_right $ λ h₂, h₂ x

theorem forall_or_distrib_left {q : Prop} {p : α → Prop} [decidable q] :
  (∀x, q ∨ p x) ↔ q ∨ (∀x, p x) :=
⟨λ h, if hq : q then or.inl hq else or.inr $ λ x, (h x).resolve_left hq,
  forall_or_of_or_forall⟩

theorem forall_or_distrib_right {q : Prop} {p : α → Prop} [decidable q] :
  (∀x, p x ∨ q) ↔ (∀x, p x) ∨ q :=
by simp [or_comm, forall_or_distrib_left]

/-- A predicate holds everywhere on the image of a surjective functions iff
    it holds everywhere. -/
theorem forall_iff_forall_surj
  {α β : Type*} {f : α → β} (h : function.surjective f) {P : β → Prop} :
  (∀ a, P (f a)) ↔ ∀ b, P b :=
⟨λ ha b, by cases h b with a hab; rw ←hab; exact ha a, λ hb a, hb $ f a⟩

@[simp] theorem exists_prop {p q : Prop} : (∃ h : p, q) ↔ p ∧ q :=
⟨λ ⟨h₁, h₂⟩, ⟨h₁, h₂⟩, λ ⟨h₁, h₂⟩, ⟨h₁, h₂⟩⟩

@[simp] theorem exists_false : ¬ (∃a:α, false) := assume ⟨a, h⟩, h

theorem Exists.fst {p : b → Prop} : Exists p → b
| ⟨h, _⟩ := h

theorem Exists.snd {p : b → Prop} : ∀ h : Exists p, p h.fst
| ⟨_, h⟩ := h

@[simp] theorem forall_prop_of_true {p : Prop} {q : p → Prop} (h : p) : (∀ h' : p, q h') ↔ q h :=
@forall_const (q h) p ⟨h⟩

@[simp] theorem exists_prop_of_true {p : Prop} {q : p → Prop} (h : p) : (∃ h' : p, q h') ↔ q h :=
@exists_const (q h) p ⟨h⟩

@[simp] theorem forall_prop_of_false {p : Prop} {q : p → Prop} (hn : ¬ p) : (∀ h' : p, q h') ↔ true :=
iff_true_intro $ λ h, hn.elim h

@[simp] theorem exists_prop_of_false {p : Prop} {q : p → Prop} : ¬ p → ¬ (∃ h' : p, q h') :=
mt Exists.fst

lemma exists_unique.exists {α : Sort*} {p : α → Prop} (h : ∃! x, p x) : ∃ x, p x :=
exists.elim h (λ x hx, ⟨x, and.left hx⟩)

lemma exists_unique.unique {α : Sort*} {p : α → Prop} (h : ∃! x, p x)
  {y₁ y₂ : α} (py₁ : p y₁) (py₂ : p y₂) : y₁ = y₂ :=
unique_of_exists_unique h py₁ py₂

@[simp] lemma exists_unique_iff_exists {α : Sort*} [subsingleton α] {p : α → Prop} :
  (∃! x, p x) ↔ ∃ x, p x :=
⟨λ h, h.exists, Exists.imp $ λ x hx, ⟨hx, λ y _, subsingleton.elim y x⟩⟩

lemma exists_unique.elim2 {α : Sort*} {p : α → Sort*} [∀ x, subsingleton (p x)]
  {q : Π x (h : p x), Prop} {b : Prop} (h₂ : ∃! x (h : p x), q x h)
  (h₁ : ∀ x (h : p x), q x h → (∀ y (hy : p y), q y hy → y = x) → b) : b :=
begin
  simp only [exists_unique_iff_exists] at h₂,
  apply h₂.elim,
  exact λ x ⟨hxp, hxq⟩ H, h₁ x hxp hxq (λ y hyp hyq, H y ⟨hyp, hyq⟩)
end

lemma exists_unique.intro2 {α : Sort*} {p : α → Sort*} [∀ x, subsingleton (p x)]
  {q : Π (x : α) (h : p x), Prop} (w : α) (hp : p w) (hq : q w hp)
  (H : ∀ y (hy : p y), q y hy → y = w) :
  ∃! x (hx : p x), q x hx :=
begin
  simp only [exists_unique_iff_exists],
  exact exists_unique.intro w ⟨hp, hq⟩ (λ y ⟨hyp, hyq⟩, H y hyp hyq)
end

lemma exists_unique.exists2 {α : Sort*} {p : α → Sort*} {q : Π (x : α) (h : p x), Prop}
  (h : ∃! x (hx : p x), q x hx) :
  ∃ x (hx : p x), q x hx :=
h.exists.imp (λ x hx, hx.exists)

lemma exists_unique.unique2 {α : Sort*} {p : α → Sort*} [∀ x, subsingleton (p x)]
  {q : Π (x : α) (hx : p x), Prop} (h : ∃! x (hx : p x), q x hx)
  {y₁ y₂ : α} (hpy₁ : p y₁) (hqy₁ : q y₁ hpy₁)
  (hpy₂ : p y₂) (hqy₂ : q y₂ hpy₂) : y₁ = y₂ :=
begin
  simp only [exists_unique_iff_exists] at h,
  exact h.unique ⟨hpy₁, hqy₁⟩ ⟨hpy₂, hqy₂⟩
end

end quantifiers

/-! ### Classical versions of earlier lemmas -/

namespace classical
variables {α : Sort*} {p : α → Prop}

local attribute [instance] prop_decidable

@[simp] protected theorem not_forall : (¬ ∀ x, p x) ↔ (∃ x, ¬ p x) := not_forall

@[simp] protected theorem not_exists_not : (¬ ∃ x, ¬ p x) ↔ ∀ x, p x := not_exists_not

protected theorem forall_or_distrib_left {q : Prop} {p : α → Prop} :
  (∀x, q ∨ p x) ↔ q ∨ (∀x, p x) :=
forall_or_distrib_left

protected theorem forall_or_distrib_right {q : Prop} {p : α → Prop} :
  (∀x, p x ∨ q) ↔ (∀x, p x) ∨ q :=
forall_or_distrib_right

protected theorem forall_or_distrib {β} {p : α → Prop} {q : β → Prop} :
  (∀x y, p x ∨ q y) ↔ (∀ x, p x) ∨ (∀ y, q y) :=
by rw ← forall_or_distrib_right; simp [forall_or_distrib_left.symm]

theorem cases {p : Prop → Prop} (h1 : p true) (h2 : p false) : ∀a, p a :=
assume a, cases_on a h1 h2

theorem or_not {p : Prop} : p ∨ ¬ p :=
by_cases or.inl or.inr

protected theorem or_iff_not_imp_left {p q : Prop} : p ∨ q ↔ (¬ p → q) :=
or_iff_not_imp_left

protected theorem or_iff_not_imp_right {p q : Prop} : q ∨ p ↔ (¬ p → q) :=
or_iff_not_imp_right

@[simp] protected lemma not_not {p : Prop} : ¬¬p ↔ p := not_not

@[simp] protected lemma not_imp {p q : Prop} : ¬(p → q) ↔ p ∧ ¬q :=
not_imp

protected theorem not_imp_not {p q : Prop} : (¬ p → ¬ q) ↔ (q → p) := not_imp_not

protected lemma not_and_distrib {p q : Prop}: ¬(p ∧ q) ↔ ¬p ∨ ¬q := not_and_distrib

protected lemma imp_iff_not_or {a b : Prop} : a → b ↔ ¬a ∨ b := imp_iff_not_or

lemma iff_iff_not_or_and_or_not {a b : Prop} : (a ↔ b) ↔ ((¬a ∨ b) ∧ (a ∨ ¬b)) :=
begin
  rw [iff_iff_implies_and_implies a b],
  simp only [imp_iff_not_or, or.comm]
end

/- use shortened names to avoid conflict when classical namespace is open. -/
noncomputable lemma dec (p : Prop) : decidable p := -- see Note [classical lemma]
by apply_instance
noncomputable lemma dec_pred (p : α → Prop) : decidable_pred p := -- see Note [classical lemma]
by apply_instance
noncomputable lemma dec_rel (p : α → α → Prop) : decidable_rel p := -- see Note [classical lemma]
by apply_instance
noncomputable lemma dec_eq (α : Sort*) : decidable_eq α := -- see Note [classical lemma]
by apply_instance

/--
We make decidability results that depends on `classical.choice` noncomputable lemmas.
* We have to mark them as noncomputable, because otherwise Lean will try to generate bytecode
  for them, and fail because it depends on `classical.choice`.
* We make them lemmas, and not definitions, because otherwise later definitions will raise
  \"failed to generate bytecode\" errors when writing something like
  `letI := classical.dec_eq _`.
Cf. <https://leanprover-community.github.io/archive/113488general/08268noncomputabletheorem.html>
-/
library_note "classical lemma"

@[elab_as_eliminator]
noncomputable def {u} exists_cases {C : Sort u} (H0 : C) (H : ∀ a, p a → C) : C :=
if h : ∃ a, p a then H (classical.some h) (classical.some_spec h) else H0

lemma some_spec2 {α : Sort*} {p : α → Prop} {h : ∃a, p a}
  (q : α → Prop) (hpq : ∀a, p a → q a) : q (some h) :=
hpq _ $ some_spec _

/-- A version of classical.indefinite_description which is definitionally equal to a pair -/
noncomputable def subtype_of_exists {α : Type*} {P : α → Prop} (h : ∃ x, P x) : {x // P x} :=
⟨classical.some h, classical.some_spec h⟩

end classical

@[elab_as_eliminator]
noncomputable def {u} exists.classical_rec_on
 {α} {p : α → Prop} (h : ∃ a, p a) {C : Sort u} (H : ∀ a, p a → C) : C :=
H (classical.some h) (classical.some_spec h)

/-! ### Declarations about bounded quantifiers -/

section bounded_quantifiers
variables {α : Sort*} {r p q : α → Prop} {P Q : ∀ x, p x → Prop} {b : Prop}

theorem bex_def : (∃ x (h : p x), q x) ↔ ∃ x, p x ∧ q x :=
⟨λ ⟨x, px, qx⟩, ⟨x, px, qx⟩, λ ⟨x, px, qx⟩, ⟨x, px, qx⟩⟩

theorem bex.elim {b : Prop} : (∃ x h, P x h) → (∀ a h, P a h → b) → b
| ⟨a, h₁, h₂⟩ h' := h' a h₁ h₂

theorem bex.intro (a : α) (h₁ : p a) (h₂ : P a h₁) : ∃ x (h : p x), P x h :=
⟨a, h₁, h₂⟩

theorem ball_congr (H : ∀ x h, P x h ↔ Q x h) :
  (∀ x h, P x h) ↔ (∀ x h, Q x h) :=
forall_congr $ λ x, forall_congr (H x)

theorem bex_congr (H : ∀ x h, P x h ↔ Q x h) :
  (∃ x h, P x h) ↔ (∃ x h, Q x h) :=
exists_congr $ λ x, exists_congr (H x)

theorem ball.imp_right (H : ∀ x h, (P x h → Q x h))
  (h₁ : ∀ x h, P x h) (x h) : Q x h :=
H _ _ $ h₁ _ _

theorem bex.imp_right (H : ∀ x h, (P x h → Q x h)) :
  (∃ x h, P x h) → ∃ x h, Q x h
| ⟨x, h, h'⟩ := ⟨_, _, H _ _ h'⟩

theorem ball.imp_left (H : ∀ x, p x → q x)
  (h₁ : ∀ x, q x → r x) (x) (h : p x) : r x :=
h₁ _ $ H _ h

theorem bex.imp_left (H : ∀ x, p x → q x) :
  (∃ x (_ : p x), r x) → ∃ x (_ : q x), r x
| ⟨x, hp, hr⟩ := ⟨x, H _ hp, hr⟩

theorem ball_of_forall (h : ∀ x, p x) (x) : p x :=
h x

theorem forall_of_ball (H : ∀ x, p x) (h : ∀ x, p x → q x) (x) : q x :=
h x $ H x

theorem bex_of_exists (H : ∀ x, p x) : (∃ x, q x) → ∃ x (_ : p x), q x
| ⟨x, hq⟩ := ⟨x, H x, hq⟩

theorem exists_of_bex : (∃ x (_ : p x), q x) → ∃ x, q x
| ⟨x, _, hq⟩ := ⟨x, hq⟩

@[simp] theorem bex_imp_distrib : ((∃ x h, P x h) → b) ↔ (∀ x h, P x h → b) :=
by simp

theorem not_bex : (¬ ∃ x h, P x h) ↔ ∀ x h, ¬ P x h :=
bex_imp_distrib

theorem not_ball_of_bex_not : (∃ x h, ¬ P x h) → ¬ ∀ x h, P x h
| ⟨x, h, hp⟩ al := hp $ al x h

theorem not_ball [decidable (∃ x h, ¬ P x h)] [∀ x h, decidable (P x h)] :
  (¬ ∀ x h, P x h) ↔ (∃ x h, ¬ P x h) :=
⟨not.imp_symm $ λ nx x h, nx.imp_symm $ λ h', ⟨x, h, h'⟩,
 not_ball_of_bex_not⟩

theorem ball_true_iff (p : α → Prop) : (∀ x, p x → true) ↔ true :=
iff_true_intro (λ h hrx, trivial)

theorem ball_and_distrib : (∀ x h, P x h ∧ Q x h) ↔ (∀ x h, P x h) ∧ (∀ x h, Q x h) :=
iff.trans (forall_congr $ λ x, forall_and_distrib) forall_and_distrib

theorem bex_or_distrib : (∃ x h, P x h ∨ Q x h) ↔ (∃ x h, P x h) ∨ (∃ x h, Q x h) :=
iff.trans (exists_congr $ λ x, exists_or_distrib) exists_or_distrib

end bounded_quantifiers

namespace classical
local attribute [instance] prop_decidable

theorem not_ball {α : Sort*} {p : α → Prop} {P : Π (x : α), p x → Prop} :
  (¬ ∀ x h, P x h) ↔ (∃ x h, ¬ P x h) := _root_.not_ball

end classical

lemma ite_eq_iff {α} {p : Prop} [decidable p] {a b c : α} :
  (if p then a else b) = c ↔ p ∧ a = c ∨ ¬p ∧ b = c :=
by by_cases p; simp *

/-! ### Declarations about `nonempty` -/

section nonempty
universe variables u v w
variables {α : Type u} {β : Type v} {γ : α → Type w}

attribute [simp] nonempty_of_inhabited

@[priority 20]
instance has_zero.nonempty [has_zero α] : nonempty α := ⟨0⟩
@[priority 20]
instance has_one.nonempty [has_one α] : nonempty α := ⟨1⟩

lemma exists_true_iff_nonempty {α : Sort*} : (∃a:α, true) ↔ nonempty α :=
iff.intro (λ⟨a, _⟩, ⟨a⟩) (λ⟨a⟩, ⟨a, trivial⟩)

@[simp] lemma nonempty_Prop {p : Prop} : nonempty p ↔ p :=
iff.intro (assume ⟨h⟩, h) (assume h, ⟨h⟩)

lemma not_nonempty_iff_imp_false : ¬ nonempty α ↔ α → false :=
⟨λ h a, h ⟨a⟩, λ h ⟨a⟩, h a⟩

@[simp] lemma nonempty_sigma : nonempty (Σa:α, γ a) ↔ (∃a:α, nonempty (γ a)) :=
iff.intro (assume ⟨⟨a, c⟩⟩, ⟨a, ⟨c⟩⟩) (assume ⟨a, ⟨c⟩⟩, ⟨⟨a, c⟩⟩)

@[simp] lemma nonempty_subtype {α : Sort u} {p : α → Prop} : nonempty (subtype p) ↔ (∃a:α, p a) :=
iff.intro (assume ⟨⟨a, h⟩⟩, ⟨a, h⟩) (assume ⟨a, h⟩, ⟨⟨a, h⟩⟩)

@[simp] lemma nonempty_prod : nonempty (α × β) ↔ (nonempty α ∧ nonempty β) :=
iff.intro (assume ⟨⟨a, b⟩⟩, ⟨⟨a⟩, ⟨b⟩⟩) (assume ⟨⟨a⟩, ⟨b⟩⟩, ⟨⟨a, b⟩⟩)

@[simp] lemma nonempty_pprod {α : Sort u} {β : Sort v} :
  nonempty (pprod α β) ↔ (nonempty α ∧ nonempty β) :=
iff.intro (assume ⟨⟨a, b⟩⟩, ⟨⟨a⟩, ⟨b⟩⟩) (assume ⟨⟨a⟩, ⟨b⟩⟩, ⟨⟨a, b⟩⟩)

@[simp] lemma nonempty_sum : nonempty (α ⊕ β) ↔ (nonempty α ∨ nonempty β) :=
iff.intro
  (assume ⟨h⟩, match h with sum.inl a := or.inl ⟨a⟩ | sum.inr b := or.inr ⟨b⟩ end)
  (assume h, match h with or.inl ⟨a⟩ := ⟨sum.inl a⟩ | or.inr ⟨b⟩ := ⟨sum.inr b⟩ end)

@[simp] lemma nonempty_psum {α : Sort u} {β : Sort v} :
  nonempty (psum α β) ↔ (nonempty α ∨ nonempty β) :=
iff.intro
  (assume ⟨h⟩, match h with psum.inl a := or.inl ⟨a⟩ | psum.inr b := or.inr ⟨b⟩ end)
  (assume h, match h with or.inl ⟨a⟩ := ⟨psum.inl a⟩ | or.inr ⟨b⟩ := ⟨psum.inr b⟩ end)

@[simp] lemma nonempty_psigma {α : Sort u} {β : α → Sort v} :
  nonempty (psigma β) ↔ (∃a:α, nonempty (β a)) :=
iff.intro (assume ⟨⟨a, c⟩⟩, ⟨a, ⟨c⟩⟩) (assume ⟨a, ⟨c⟩⟩, ⟨⟨a, c⟩⟩)

@[simp] lemma nonempty_empty : ¬ nonempty empty :=
assume ⟨h⟩, h.elim

@[simp] lemma nonempty_ulift : nonempty (ulift α) ↔ nonempty α :=
iff.intro (assume ⟨⟨a⟩⟩, ⟨a⟩) (assume ⟨a⟩, ⟨⟨a⟩⟩)

@[simp] lemma nonempty_plift {α : Sort u} : nonempty (plift α) ↔ nonempty α :=
iff.intro (assume ⟨⟨a⟩⟩, ⟨a⟩) (assume ⟨a⟩, ⟨⟨a⟩⟩)

@[simp] lemma nonempty.forall {α : Sort u} {p : nonempty α → Prop} :
  (∀h:nonempty α, p h) ↔ (∀a, p ⟨a⟩) :=
iff.intro (assume h a, h _) (assume h ⟨a⟩, h _)

@[simp] lemma nonempty.exists {α : Sort u} {p : nonempty α → Prop} :
  (∃h:nonempty α, p h) ↔ (∃a, p ⟨a⟩) :=
iff.intro (assume ⟨⟨a⟩, h⟩, ⟨a, h⟩) (assume ⟨a, h⟩, ⟨⟨a⟩, h⟩)

lemma classical.nonempty_pi {α : Sort u} {β : α → Sort v} :
  nonempty (Πa:α, β a) ↔ (∀a:α, nonempty (β a)) :=
iff.intro (assume ⟨f⟩ a, ⟨f a⟩) (assume f, ⟨assume a, classical.choice $ f a⟩)

/-- Using `classical.choice`, lifts a (`Prop`-valued) `nonempty` instance to a (`Type`-valued)
  `inhabited` instance. `classical.inhabited_of_nonempty` already exists, in
  `core/init/classical.lean`, but the assumption is not a type class argument,
  which makes it unsuitable for some applications. -/
noncomputable def classical.inhabited_of_nonempty' {α : Sort u} [h : nonempty α] : inhabited α :=
⟨classical.choice h⟩

/-- Given `f : α → β`, if `α` is nonempty then `β` is also nonempty.
  `nonempty` cannot be a `functor`, because `functor` is restricted to `Type`. -/
lemma nonempty.map {α : Sort u} {β : Sort v} (f : α → β) : nonempty α → nonempty β
| ⟨h⟩ := ⟨f h⟩

protected lemma nonempty.map2 {α β γ : Sort*} (f : α → β → γ) : nonempty α → nonempty β → nonempty γ
| ⟨x⟩ ⟨y⟩ := ⟨f x y⟩

protected lemma nonempty.congr {α : Sort u} {β : Sort v} (f : α → β) (g : β → α) :
  nonempty α ↔ nonempty β :=
⟨nonempty.map f, nonempty.map g⟩

lemma nonempty.elim_to_inhabited {α : Sort*} [h : nonempty α] {p : Prop}
  (f : inhabited α → p) : p :=
h.elim $ f ∘ inhabited.mk

instance {α β} [h : nonempty α] [h2 : nonempty β] : nonempty (α × β) :=
h.elim $ λ g, h2.elim $ λ g2, ⟨⟨g, g2⟩⟩

end nonempty
