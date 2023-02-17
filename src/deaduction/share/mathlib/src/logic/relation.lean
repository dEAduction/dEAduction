/-
Copyright (c) 2018 Johannes Hölzl. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Johannes Hölzl

Transitive reflexive as well as reflexive closure of relations.
-/
import tactic.basic
variables {α : Type*} {β : Type*} {γ : Type*} {δ : Type*}

namespace relation

section comp
variables {r : α → β → Prop} {p : β → γ → Prop} {q : γ → δ → Prop}

def comp (r : α → β → Prop) (p : β → γ → Prop) (a : α) (c : γ) : Prop := ∃b, r a b ∧ p b c

local infixr ` ∘r ` : 80 := relation.comp

lemma comp_eq : r ∘r (=) = r :=
funext $ assume a, funext $ assume b, propext $ iff.intro
  (assume ⟨c, h, eq⟩, eq ▸ h)
  (assume h, ⟨b, h, rfl⟩)

lemma eq_comp : (=) ∘r r = r :=
funext $ assume a, funext $ assume b, propext $ iff.intro
  (assume ⟨c, eq, h⟩, eq.symm ▸ h)
  (assume h, ⟨a, rfl, h⟩)

lemma iff_comp {r : Prop → α → Prop} : (↔) ∘r r = r :=
have (↔) = (=), by funext a b; exact iff_eq_eq,
by rw [this, eq_comp]

lemma comp_iff {r : α → Prop → Prop} : r ∘r (↔) = r :=
have (↔) = (=), by funext a b; exact iff_eq_eq,
by rw [this, comp_eq]

lemma comp_assoc : (r ∘r p) ∘r q = r ∘r p ∘r q :=
begin
  funext a d, apply propext,
  split,
  exact assume ⟨c, ⟨b, hab, hbc⟩, hcd⟩, ⟨b, hab, c, hbc, hcd⟩,
  exact assume ⟨b, hab, c, hbc, hcd⟩, ⟨c, ⟨b, hab, hbc⟩, hcd⟩
end

lemma flip_comp : flip (r ∘r p) = (flip p) ∘r (flip r) :=
begin
  funext c a, apply propext,
  split,
  exact assume ⟨b, hab, hbc⟩, ⟨b, hbc, hab⟩,
  exact assume ⟨b, hbc, hab⟩, ⟨b, hab, hbc⟩
end

end comp

protected def map (r : α → β → Prop) (f : α → γ) (g : β → δ) : γ → δ → Prop :=
λc d, ∃a b, r a b ∧ f a = c ∧ g b = d

variables {r : α → α → Prop} {a b c d : α}

/-- `refl_trans_gen r`: reflexive transitive closure of `r` -/
inductive refl_trans_gen (r : α → α → Prop) (a : α) : α → Prop
| refl : refl_trans_gen a
| tail {b c} : refl_trans_gen b → r b c → refl_trans_gen c

attribute [refl] refl_trans_gen.refl

mk_iff_of_inductive_prop relation.refl_trans_gen relation.refl_trans_gen.cases_tail_iff

/-- `refl_gen r`: reflexive closure of `r` -/
inductive refl_gen (r : α → α → Prop) (a : α) : α → Prop
| refl : refl_gen a
| single {b} : r a b → refl_gen b

mk_iff_of_inductive_prop relation.refl_gen relation.refl_gen_iff

/-- `trans_gen r`: transitive closure of `r` -/
inductive trans_gen (r : α → α → Prop) (a : α) : α → Prop
| single {b} : r a b → trans_gen b
| tail {b c} : trans_gen b → r b c → trans_gen c

mk_iff_of_inductive_prop relation.trans_gen relation.trans_gen_iff

attribute [refl] refl_gen.refl

lemma refl_gen.to_refl_trans_gen : ∀{a b}, refl_gen r a b → refl_trans_gen r a b
| a _ refl_gen.refl := by refl
| a b (refl_gen.single h) := refl_trans_gen.tail refl_trans_gen.refl h

namespace refl_trans_gen

@[trans]
lemma trans (hab : refl_trans_gen r a b) (hbc : refl_trans_gen r b c) : refl_trans_gen r a c :=
begin
  induction hbc,
  case refl_trans_gen.refl { assumption },
  case refl_trans_gen.tail : c d hbc hcd hac { exact hac.tail hcd }
end

lemma single (hab : r a b) : refl_trans_gen r a b :=
refl.tail hab

lemma head (hab : r a b) (hbc : refl_trans_gen r b c) : refl_trans_gen r a c :=
begin
  induction hbc,
  case refl_trans_gen.refl { exact refl.tail hab },
  case refl_trans_gen.tail : c d hbc hcd hac { exact hac.tail hcd }
end

lemma symmetric (h : symmetric r) : symmetric (refl_trans_gen r) :=
begin
  intros x y h,
  induction h with z w a b c,
  { refl },
  { apply relation.refl_trans_gen.head (h b) c }
end

lemma cases_tail : refl_trans_gen r a b → b = a ∨ (∃c, refl_trans_gen r a c ∧ r c b) :=
(cases_tail_iff r a b).1

@[elab_as_eliminator]
lemma head_induction_on
  {P : ∀(a:α), refl_trans_gen r a b → Prop}
  {a : α} (h : refl_trans_gen r a b)
  (refl : P b refl)
  (head : ∀{a c} (h' : r a c) (h : refl_trans_gen r c b), P c h → P a (h.head h')) :
  P a h :=
begin
  induction h generalizing P,
  case refl_trans_gen.refl { exact refl },
  case refl_trans_gen.tail : b c hab hbc ih {
    apply ih,
    show P b _, from head hbc _ refl,
    show ∀a a', r a a' → refl_trans_gen r a' b → P a' _ → P a _,
      from assume a a' hab hbc, head hab _ }
end

@[elab_as_eliminator]
lemma trans_induction_on
  {P : ∀{a b : α}, refl_trans_gen r a b → Prop}
  {a b : α} (h : refl_trans_gen r a b)
  (ih₁ : ∀a, @P a a refl)
  (ih₂ : ∀{a b} (h : r a b), P (single h))
  (ih₃ : ∀{a b c} (h₁ : refl_trans_gen r a b) (h₂ : refl_trans_gen r b c),
    P h₁ → P h₂ → P (h₁.trans h₂)) :
  P h :=
begin
  induction h,
  case refl_trans_gen.refl { exact ih₁ a },
  case refl_trans_gen.tail : b c hab hbc ih { exact ih₃ hab (single hbc) ih (ih₂ hbc) }
end

lemma cases_head (h : refl_trans_gen r a b) : a = b ∨ (∃c, r a c ∧ refl_trans_gen r c b) :=
begin
  induction h using relation.refl_trans_gen.head_induction_on,
  { left, refl },
  { right, existsi _, split; assumption }
end

lemma cases_head_iff : refl_trans_gen r a b ↔ a = b ∨ (∃c, r a c ∧ refl_trans_gen r c b) :=
begin
  split,
  { exact cases_head },
  { assume h,
    rcases h with rfl | ⟨c, hac, hcb⟩,
    { refl },
    { exact head hac hcb } }
end

lemma total_of_right_unique (U : relator.right_unique r)
  (ab : refl_trans_gen r a b) (ac : refl_trans_gen r a c) :
  refl_trans_gen r b c ∨ refl_trans_gen r c b :=
begin
  induction ab with b d ab bd IH,
  { exact or.inl ac },
  { rcases IH with IH | IH,
    { rcases cases_head IH with rfl | ⟨e, be, ec⟩,
      { exact or.inr (single bd) },
      { cases U bd be, exact or.inl ec } },
    { exact or.inr (IH.tail bd) } }
end

end refl_trans_gen

namespace trans_gen

lemma to_refl {a b} (h : trans_gen r a b) : refl_trans_gen r a b :=
begin
  induction h with b h b c _ bc ab,
  exact refl_trans_gen.single h,
  exact refl_trans_gen.tail ab bc
end

@[trans] lemma trans_left (hab : trans_gen r a b) (hbc : refl_trans_gen r b c) : trans_gen r a c :=
begin
  induction hbc,
  case refl_trans_gen.refl : { assumption },
  case refl_trans_gen.tail : c d hbc hcd hac { exact hac.tail hcd }
end

@[trans] lemma trans (hab : trans_gen r a b) (hbc : trans_gen r b c) : trans_gen r a c :=
trans_left hab hbc.to_refl

lemma head' (hab : r a b) (hbc : refl_trans_gen r b c) : trans_gen r a c :=
trans_left (single hab) hbc

lemma tail' (hab : refl_trans_gen r a b) (hbc : r b c) : trans_gen r a c :=
begin
  induction hab generalizing c,
  case refl_trans_gen.refl : c hac { exact single hac },
  case refl_trans_gen.tail : d b hab hdb IH { exact tail (IH hdb) hbc }
end

@[trans] lemma trans_right (hab : refl_trans_gen r a b) (hbc : trans_gen r b c) : trans_gen r a c :=
begin
  induction hbc,
  case trans_gen.single : c hbc { exact tail' hab hbc },
  case trans_gen.tail : c d hbc hcd hac { exact hac.tail hcd }
end

lemma head (hab : r a b) (hbc : trans_gen r b c) : trans_gen r a c :=
head' hab hbc.to_refl

lemma tail'_iff : trans_gen r a c ↔ ∃ b, refl_trans_gen r a b ∧ r b c :=
begin
  refine ⟨λ h, _, λ ⟨b, hab, hbc⟩, tail' hab hbc⟩,
  cases h with _ hac b _ hab hbc,
  { exact ⟨_, by refl, hac⟩ },
  { exact ⟨_, hab.to_refl, hbc⟩ }
end

lemma head'_iff : trans_gen r a c ↔ ∃ b, r a b ∧ refl_trans_gen r b c :=
begin
  refine ⟨λ h, _, λ ⟨b, hab, hbc⟩, head' hab hbc⟩,
  induction h,
  case trans_gen.single : c hac { exact ⟨_, hac, by refl⟩ },
  case trans_gen.tail : b c hab hbc IH {
    rcases IH with ⟨d, had, hdb⟩, exact ⟨_, had, hdb.tail hbc⟩ }
end

end trans_gen

section refl_trans_gen
open refl_trans_gen

lemma refl_trans_gen_iff_eq (h : ∀b, ¬ r a b) : refl_trans_gen r a b ↔ b = a :=
by rw [cases_head_iff]; simp [h, eq_comm]

lemma refl_trans_gen_iff_eq_or_trans_gen :
  refl_trans_gen r a b ↔ b = a ∨ trans_gen r a b :=
begin
  refine ⟨λ h, _, λ h, _⟩,
  { cases h with c _ hac hcb,
    { exact or.inl rfl },
    { exact or.inr (trans_gen.tail' hac hcb) } },
  { rcases h with rfl | h, {refl}, {exact h.to_refl} }
end

lemma refl_trans_gen_lift {p : β → β → Prop} {a b : α} (f : α → β)
  (h : ∀a b, r a b → p (f a) (f b)) (hab : refl_trans_gen r a b) : refl_trans_gen p (f a) (f b) :=
refl_trans_gen.trans_induction_on hab (assume a, refl)
  (assume a b, refl_trans_gen.single ∘ h _ _) (assume a b c _ _, trans)

lemma refl_trans_gen_mono {p : α → α → Prop} :
  (∀a b, r a b → p a b) → refl_trans_gen r a b → refl_trans_gen p a b :=
refl_trans_gen_lift id

lemma refl_trans_gen_eq_self (refl : reflexive r) (trans : transitive r) :
  refl_trans_gen r = r :=
funext $ λ a, funext $ λ b, propext $
⟨λ h, begin
  induction h with b c h₁ h₂ IH, {apply refl},
  exact trans IH h₂,
end, single⟩

lemma reflexive_refl_trans_gen : reflexive (refl_trans_gen r) :=
assume a, refl

lemma transitive_refl_trans_gen : transitive (refl_trans_gen r) :=
assume a b c, trans

lemma refl_trans_gen_idem :
  refl_trans_gen (refl_trans_gen r) = refl_trans_gen r :=
refl_trans_gen_eq_self reflexive_refl_trans_gen transitive_refl_trans_gen

lemma refl_trans_gen_lift' {p : β → β → Prop} {a b : α} (f : α → β)
  (h : ∀a b, r a b → refl_trans_gen p (f a) (f b))
  (hab : refl_trans_gen r a b) : refl_trans_gen p (f a) (f b) :=
by simpa [refl_trans_gen_idem] using refl_trans_gen_lift f h hab

lemma refl_trans_gen_closed {p : α → α → Prop} :
  (∀ a b, r a b → refl_trans_gen p a b) → refl_trans_gen r a b → refl_trans_gen p a b :=
refl_trans_gen_lift' id

end refl_trans_gen

def join (r : α → α → Prop) : α → α → Prop := λa b, ∃c, r a c ∧ r b c

section join
open refl_trans_gen refl_gen

lemma church_rosser
  (h : ∀a b c, r a b → r a c → ∃d, refl_gen r b d ∧ refl_trans_gen r c d)
  (hab : refl_trans_gen r a b) (hac : refl_trans_gen r a c) : join (refl_trans_gen r) b c :=
begin
  induction hab,
  case refl_trans_gen.refl { exact ⟨c, hac, refl⟩ },
  case refl_trans_gen.tail : d e had hde ih {
    clear hac had a,
    rcases ih with ⟨b, hdb, hcb⟩,
    have : ∃a, refl_trans_gen r e a ∧ refl_gen r b a,
    { clear hcb, induction hdb,
      case refl_trans_gen.refl { exact ⟨e, refl, refl_gen.single hde⟩ },
      case refl_trans_gen.tail : f b hdf hfb ih {
        rcases ih with ⟨a, hea, hfa⟩,
        cases hfa with _ hfa,
        { exact ⟨b, hea.tail hfb, refl_gen.refl⟩ },
        { rcases h _ _ _ hfb hfa with ⟨c, hbc, hac⟩,
          exact ⟨c, hea.trans hac, hbc⟩ } } },
    rcases this with ⟨a, hea, hba⟩, cases hba with _ hba,
    { exact ⟨b, hea, hcb⟩ },
    { exact ⟨a, hea, hcb.tail hba⟩ } }
end

lemma join_of_single (h : reflexive r) (hab : r a b) : join r a b :=
⟨b, hab, h b⟩

lemma symmetric_join : symmetric (join r) :=
assume a b ⟨c, hac, hcb⟩, ⟨c, hcb, hac⟩

lemma reflexive_join (h : reflexive r) : reflexive (join r) :=
assume a, ⟨a, h a, h a⟩

lemma transitive_join (ht : transitive r) (h : ∀a b c, r a b → r a c → join r b c) :
  transitive (join r) :=
assume a b c ⟨x, hax, hbx⟩ ⟨y, hby, hcy⟩,
let ⟨z, hxz, hyz⟩ := h b x y hbx hby in
⟨z, ht hax hxz, ht hcy hyz⟩

lemma equivalence_join (hr : reflexive r) (ht : transitive r)
  (h : ∀a b c, r a b → r a c → join r b c) :
  equivalence (join r) :=
⟨reflexive_join hr, symmetric_join, transitive_join ht h⟩

lemma equivalence_join_refl_trans_gen
  (h : ∀a b c, r a b → r a c → ∃d, refl_gen r b d ∧ refl_trans_gen r c d) :
  equivalence (join (refl_trans_gen r)) :=
equivalence_join reflexive_refl_trans_gen transitive_refl_trans_gen (assume a b c, church_rosser h)

lemma join_of_equivalence {r' : α → α → Prop} (hr : equivalence r)
  (h : ∀a b, r' a b → r a b) : join r' a b → r a b
| ⟨c, hac, hbc⟩ := hr.2.2 (h _ _ hac) (hr.2.1 $ h _ _ hbc)

lemma refl_trans_gen_of_transitive_reflexive {r' : α → α → Prop} (hr : reflexive r)
  (ht : transitive r) (h : ∀a b, r' a b → r a b) (h' : refl_trans_gen r' a b) :
  r a b :=
begin
  induction h' with b c hab hbc ih,
  { exact hr _ },
  { exact ht ih (h _ _ hbc) }
end

lemma refl_trans_gen_of_equivalence {r' : α → α → Prop} (hr : equivalence r) :
  (∀a b, r' a b → r a b) → refl_trans_gen r' a b → r a b :=
refl_trans_gen_of_transitive_reflexive hr.1 hr.2.2

end join

section eqv_gen

lemma eqv_gen_iff_of_equivalence (h : equivalence r) : eqv_gen r a b ↔ r a b :=
iff.intro
  begin
    assume h,
    induction h,
    case eqv_gen.rel { assumption },
    case eqv_gen.refl { exact h.1 _ },
    case eqv_gen.symm { apply h.2.1, assumption },
    case eqv_gen.trans : a b c _ _ hab hbc {  exact h.2.2 hab hbc }
  end
  (eqv_gen.rel a b)

lemma eqv_gen_mono {r p : α → α → Prop}
  (hrp : ∀a b, r a b → p a b) (h : eqv_gen r a b) : eqv_gen p a b :=
begin
  induction h,
  case eqv_gen.rel : a b h { exact eqv_gen.rel _ _ (hrp _ _ h) },
  case eqv_gen.refl : { exact eqv_gen.refl _ },
  case eqv_gen.symm : a b h ih { exact eqv_gen.symm _ _ ih },
  case eqv_gen.trans : a b c ih1 ih2 hab hbc { exact eqv_gen.trans _ _ _ hab hbc }
end

end eqv_gen

end relation
