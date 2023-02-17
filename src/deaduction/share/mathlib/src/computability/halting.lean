/-
Copyright (c) 2018 Mario Carneiro. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Author: Mario Carneiro
-/
import computability.partrec_code

/-!
# Computability theory and the halting problem

A universal partial recursive function, Rice's theorem, and the halting problem.

## References

* [Mario Carneiro, *Formalizing computability theory via partial recursive functions*][carneiro2019]
-/

open encodable denumerable

namespace nat.partrec
open computable roption

theorem merge' {f g}
  (hf : nat.partrec f) (hg : nat.partrec g) :
  ∃ h, nat.partrec h ∧ ∀ a,
    (∀ x ∈ h a, x ∈ f a ∨ x ∈ g a) ∧
    ((h a).dom ↔ (f a).dom ∨ (g a).dom) :=
begin
  rcases code.exists_code.1 hf with ⟨cf, rfl⟩,
  rcases code.exists_code.1 hg with ⟨cg, rfl⟩,
  have : nat.partrec (λ n,
    (nat.rfind_opt (λ k, cf.evaln k n <|> cg.evaln k n))) :=
  partrec.nat_iff.1 (partrec.rfind_opt $
    primrec.option_orelse.to_comp.comp
      (code.evaln_prim.to_comp.comp $ (snd.pair (const cf)).pair fst)
      (code.evaln_prim.to_comp.comp $ (snd.pair (const cg)).pair fst)),
  refine ⟨_, this, λ n, _⟩,
  suffices, refine ⟨this,
    ⟨λ h, (this _ ⟨h, rfl⟩).imp Exists.fst Exists.fst, _⟩⟩,
  { intro h, rw nat.rfind_opt_dom,
    simp [dom_iff_mem, code.evaln_complete] at h,
    rcases h with ⟨x, k, e⟩ | ⟨x, k, e⟩,
    { refine ⟨k, x, _⟩, simp [e] },
    { refine ⟨k, _⟩,
      cases cf.evaln k n with y,
      { exact ⟨x, by simp [e]⟩ },
      { exact ⟨y, by simp⟩ } } },
  { intros x h,
    rcases nat.rfind_opt_spec h with ⟨k, e⟩,
    revert e,
    simp; cases e' : cf.evaln k n with y; simp; intro,
    { exact or.inr (code.evaln_sound e) },
    { subst y,
        exact or.inl (code.evaln_sound e') } }
end

end nat.partrec

namespace partrec
variables {α : Type*} {β : Type*} {γ : Type*} {σ : Type*}
variables [primcodable α] [primcodable β] [primcodable γ] [primcodable σ]

open computable roption nat.partrec (code) nat.partrec.code

theorem merge' {f g : α →. σ}
  (hf : partrec f) (hg : partrec g) :
  ∃ k : α →. σ, partrec k ∧ ∀ a,
    (∀ x ∈ k a, x ∈ f a ∨ x ∈ g a) ∧
    ((k a).dom ↔ (f a).dom ∨ (g a).dom) :=
let ⟨k, hk, H⟩ :=
  nat.partrec.merge' (bind_decode2_iff.1 hf) (bind_decode2_iff.1 hg) in
begin
  let k' := λ a, (k (encode a)).bind (λ n, decode σ n),
  refine ⟨k', ((nat_iff.2 hk).comp computable.encode).bind
    (computable.decode.of_option.comp snd).to₂, λ a, _⟩,
  suffices, refine ⟨this,
    ⟨λ h, (this _ ⟨h, rfl⟩).imp Exists.fst Exists.fst, _⟩⟩,
  { intro h, simp [k'],
    have hk : (k (encode a)).dom :=
      (H _).2.2 (by simpa [encodek2] using h),
    existsi hk,
    cases (H _).1 _ ⟨hk, rfl⟩ with h h;
    { simp at h,
      rcases h with ⟨a', ha', y, hy, e⟩,
      simp [e.symm, encodek] } },
  { intros x h', simp [k'] at h',
    rcases h' with ⟨n, hn, hx⟩,
    have := (H _).1 _ hn,
    simp [mem_decode2, encode_injective.eq_iff] at this,
    cases this with h h;
    { rcases h with ⟨a', ha, rfl⟩,
      simp [encodek] at hx, subst a',
      simp [ha] } },
end

theorem merge {f g : α →. σ}
  (hf : partrec f) (hg : partrec g)
  (H : ∀ a (x ∈ f a) (y ∈ g a), x = y) :
  ∃ k : α →. σ, partrec k ∧ ∀ a x, x ∈ k a ↔ x ∈ f a ∨ x ∈ g a :=
let ⟨k, hk, K⟩ := merge' hf hg in
⟨k, hk, λ a x, ⟨(K _).1 _, λ h, begin
  have : (k a).dom := (K _).2.2 (h.imp Exists.fst Exists.fst),
  refine ⟨this, _⟩,
  cases h with h h; cases (K _).1 _ ⟨this, rfl⟩ with h' h',
  { exact mem_unique h' h },
  { exact (H _ _ h _ h').symm },
  { exact H _ _ h' _ h },
  { exact mem_unique h' h }
end⟩⟩

theorem cond {c : α → bool} {f : α →. σ} {g : α →. σ}
  (hc : computable c) (hf : partrec f) (hg : partrec g) :
  partrec (λ a, cond (c a) (f a) (g a)) :=
let ⟨cf, ef⟩ := exists_code.1 hf,
    ⟨cg, eg⟩ := exists_code.1 hg in
((eval_part.comp
    (computable.cond hc (const cf) (const cg)) computable.id).bind
  ((@computable.decode σ _).comp snd).of_option.to₂).of_eq $
λ a, by cases c a; simp [ef, eg, encodek]

theorem sum_cases
  {f : α → β ⊕ γ} {g : α → β →. σ} {h : α → γ →. σ}
  (hf : computable f) (hg : partrec₂ g) (hh : partrec₂ h) :
  @partrec _ σ _ _ (λ a, sum.cases_on (f a) (g a) (h a)) :=
option_some_iff.1 $ (cond
  (sum_cases hf (const tt).to₂ (const ff).to₂)
  (sum_cases_left hf (option_some_iff.2 hg).to₂ (const option.none).to₂)
  (sum_cases_right hf (const option.none).to₂ (option_some_iff.2 hh).to₂))
.of_eq $ λ a, by cases f a; simp

end partrec

def computable_pred {α} [primcodable α] (p : α → Prop) :=
∃ [D : decidable_pred p],
by exactI computable (λ a, to_bool (p a))

/- recursively enumerable predicate -/
def re_pred {α} [primcodable α] (p : α → Prop) :=
partrec (λ a, roption.assert (p a) (λ _, roption.some ()))

theorem computable_pred.of_eq {α} [primcodable α]
  {p q : α → Prop}
  (hp : computable_pred p) (H : ∀ a, p a ↔ q a) : computable_pred q :=
(funext (λ a, propext (H a)) : p = q) ▸ hp

namespace computable_pred
variables {α : Type*} {σ : Type*}
variables [primcodable α] [primcodable σ]
open nat.partrec (code) nat.partrec.code computable

theorem computable_iff {p : α → Prop} :
  computable_pred p ↔ ∃ f : α → bool, computable f ∧ p = λ a, f a :=
⟨λ ⟨D, h⟩, by exactI ⟨_, h, funext $ λ a, propext (to_bool_iff _).symm⟩,
 by rintro ⟨f, h, rfl⟩; exact ⟨by apply_instance, by simpa using h⟩⟩

protected theorem not {p : α → Prop}
  (hp : computable_pred p) : computable_pred (λ a, ¬ p a) :=
by rcases computable_iff.1 hp with ⟨f, hf, rfl⟩; exact
  ⟨by apply_instance,
    (cond hf (const ff) (const tt)).of_eq
      (λ n, by {dsimp, cases f n; refl})⟩

theorem to_re {p : α → Prop} (hp : computable_pred p) : re_pred p :=
begin
  rcases computable_iff.1 hp with ⟨f, hf, rfl⟩,
  unfold re_pred,
  refine (partrec.cond hf (partrec.const' (roption.some ())) partrec.none).of_eq
    (λ n, roption.ext $ λ a, _),
  cases a, cases f n; simp
end

theorem rice (C : set (ℕ →. ℕ))
  (h : computable_pred (λ c, eval c ∈ C))
  {f g} (hf : nat.partrec f) (hg : nat.partrec g)
  (fC : f ∈ C) : g ∈ C :=
begin
  cases h with _ h, resetI,
  rcases fixed_point₂ (partrec.cond (h.comp fst)
    ((partrec.nat_iff.2 hg).comp snd).to₂
    ((partrec.nat_iff.2 hf).comp snd).to₂).to₂ with ⟨c, e⟩,
  simp at e,
  by_cases eval c ∈ C,
  { simp [h] at e, rwa ← e },
  { simp at h, simp [h] at e,
    rw e at h, contradiction }
end

theorem rice₂ (C : set code)
  (H : ∀ cf cg, eval cf = eval cg → (cf ∈ C ↔ cg ∈ C)) :
  computable_pred (λ c, c ∈ C) ↔ C = ∅ ∨ C = set.univ :=
by haveI := classical.dec; exact
have hC : ∀ f, f ∈ C ↔ eval f ∈ eval '' C,
from λ f, ⟨set.mem_image_of_mem _, λ ⟨g, hg, e⟩, (H _ _ e).1 hg⟩,
⟨λ h, or_iff_not_imp_left.2 $ λ C0,
  set.eq_univ_of_forall $ λ cg,
  let ⟨cf, fC⟩ := set.ne_empty_iff_nonempty.1 C0 in
  (hC _).2 $ rice (eval '' C) (h.of_eq hC)
    (partrec.nat_iff.1 $ eval_part.comp (const cf) computable.id)
    (partrec.nat_iff.1 $ eval_part.comp (const cg) computable.id)
    ((hC _).1 fC),
λ h, by rcases h with rfl | rfl; simp [computable_pred];
  exact ⟨by apply_instance, computable.const _⟩⟩

theorem halting_problem (n) : ¬ computable_pred (λ c, (eval c n).dom)
| h := rice {f | (f n).dom} h nat.partrec.zero nat.partrec.none trivial

-- Post's theorem on the equivalence of r.e., co-r.e. sets and
-- computable sets. The assumption that p is decidable is required
-- unless we assume Markov's principle or LEM.
@[nolint decidable_classical]
theorem computable_iff_re_compl_re {p : α → Prop} [decidable_pred p] :
  computable_pred p ↔ re_pred p ∧ re_pred (λ a, ¬ p a) :=
⟨λ h, ⟨h.to_re, h.not.to_re⟩, λ ⟨h₁, h₂⟩, ⟨‹_›, begin
  rcases partrec.merge
    (h₁.map (computable.const tt).to₂)
    (h₂.map (computable.const ff).to₂) _ with ⟨k, pk, hk⟩,
  { refine partrec.of_eq pk (λ n, roption.eq_some_iff.2 _),
    rw hk, simp, apply decidable.em },
  { intros a x hx y hy, simp at hx hy, cases hy.1 hx.1 }
end⟩⟩

end computable_pred

namespace nat
open vector roption

/-- A simplified basis for `partrec`. -/
inductive partrec' : ∀ {n}, (vector ℕ n →. ℕ) → Prop
| prim {n f} : @primrec' n f → @partrec' n f
| comp {m n f} (g : fin n → vector ℕ m →. ℕ) :
  partrec' f → (∀ i, partrec' (g i)) →
  partrec' (λ v, m_of_fn (λ i, g i v) >>= f)
| rfind {n} {f : vector ℕ (n+1) → ℕ} : @partrec' (n+1) f →
  partrec' (λ v, rfind (λ n, some (f (n :: v) = 0)))

end nat

namespace nat.partrec'
open vector partrec computable nat (partrec') nat.partrec'

theorem to_part {n f} (pf : @partrec' n f) : partrec f :=
begin
  induction pf,
  case nat.partrec'.prim : n f hf { exact hf.to_prim.to_comp },
  case nat.partrec'.comp : m n f g _ _ hf hg {
    exact (vector_m_of_fn (λ i, hg i)).bind (hf.comp snd) },
  case nat.partrec'.rfind : n f _ hf {
    have := ((primrec.eq.comp primrec.id (primrec.const 0)).to_comp.comp
      (hf.comp (vector_cons.comp snd fst))).to₂.part,
    exact this.rfind },
end

theorem of_eq {n} {f g : vector ℕ n →. ℕ}
  (hf : partrec' f) (H : ∀ i, f i = g i) : partrec' g :=
(funext H : f = g) ▸ hf

theorem of_prim {n} {f : vector ℕ n → ℕ} (hf : primrec f) : @partrec' n f :=
prim (nat.primrec'.of_prim hf)

theorem head {n : ℕ} : @partrec' n.succ (@head ℕ n) :=
prim nat.primrec'.head

theorem tail {n f} (hf : @partrec' n f) : @partrec' n.succ (λ v, f v.tail) :=
(hf.comp _ (λ i, @prim _ _ $ nat.primrec'.nth i.succ)).of_eq $
λ v, by simp; rw [← of_fn_nth v.tail]; congr; funext i; simp

protected theorem bind {n f g}
  (hf : @partrec' n f) (hg : @partrec' (n+1) g) :
  @partrec' n (λ v, (f v).bind (λ a, g (a :: v))) :=
(@comp n (n+1) g
  (λ i, fin.cases f (λ i v, some (v.nth i)) i) hg
  (λ i, begin
    refine fin.cases _ (λ i, _) i; simp *,
    exact prim (nat.primrec'.nth _)
  end)).of_eq $
λ v, by simp [m_of_fn, roption.bind_assoc, pure]

protected theorem map {n f} {g : vector ℕ (n+1) → ℕ}
  (hf : @partrec' n f) (hg : @partrec' (n+1) g) :
  @partrec' n (λ v, (f v).map (λ a, g (a :: v))) :=
by simp [(roption.bind_some_eq_map _ _).symm];
   exact hf.bind hg

def vec {n m} (f : vector ℕ n → vector ℕ m) :=
∀ i, partrec' (λ v, (f v).nth i)

theorem vec.prim {n m f} (hf : @nat.primrec'.vec n m f) : vec f :=
λ i, prim $ hf i

protected theorem nil {n} : @vec n 0 (λ _, nil) := λ i, i.elim0

protected theorem cons {n m} {f : vector ℕ n → ℕ} {g}
  (hf : @partrec' n f) (hg : @vec n m g) :
  vec (λ v, f v :: g v) :=
λ i, fin.cases (by simp *) (λ i, by simp [hg i]) i

theorem idv {n} : @vec n n id := vec.prim nat.primrec'.idv

theorem comp' {n m f g} (hf : @partrec' m f) (hg : @vec n m g) :
  partrec' (λ v, f (g v)) :=
(hf.comp _ hg).of_eq $ λ v, by simp

theorem comp₁ {n} (f : ℕ →. ℕ) {g : vector ℕ n → ℕ}
  (hf : @partrec' 1 (λ v, f v.head)) (hg : @partrec' n g) :
  @partrec' n (λ v, f (g v)) :=
by simpa using hf.comp' (partrec'.cons hg partrec'.nil)

theorem rfind_opt {n} {f : vector ℕ (n+1) → ℕ}
  (hf : @partrec' (n+1) f) :
  @partrec' n (λ v, nat.rfind_opt (λ a, of_nat (option ℕ) (f (a :: v)))) :=
((rfind $ (of_prim (primrec.nat_sub.comp (primrec.const 1) primrec.vector_head))
   .comp₁ (λ n, roption.some (1 - n)) hf)
   .bind ((prim nat.primrec'.pred).comp₁ nat.pred hf)).of_eq $
λ v, roption.ext $ λ b, begin
  simp [nat.rfind_opt, -nat.mem_rfind],
  refine exists_congr (λ a,
    (and_congr (iff_of_eq _) iff.rfl).trans (and_congr_right (λ h, _))),
  { congr; funext n,
    simp, cases f (n :: v); simp [nat.succ_ne_zero]; refl },
  { have := nat.rfind_spec h,
    simp at this,
    cases f (a :: v) with c, {cases this},
    rw [← option.some_inj, eq_comm], refl }
end

open nat.partrec.code
theorem of_part : ∀ {n f}, partrec f → @partrec' n f :=
suffices ∀ f, nat.partrec f → @partrec' 1 (λ v, f v.head), from
λ n f hf, begin
  let g, swap,
  exact (comp₁ g (this g hf) (prim nat.primrec'.encode)).of_eq
    (λ i, by dsimp [g]; simp [encodek, roption.map_id']),
end,
λ f hf, begin
  rcases exists_code.1 hf with ⟨c, rfl⟩,
  simpa [eval_eq_rfind_opt] using
    (rfind_opt $ of_prim $ primrec.encode_iff.2 $ evaln_prim.comp $
      (primrec.vector_head.pair (primrec.const c)).pair $
      primrec.vector_head.comp primrec.vector_tail)
end

theorem part_iff {n f} : @partrec' n f ↔ partrec f := ⟨to_part, of_part⟩

theorem part_iff₁ {f : ℕ →. ℕ} :
  @partrec' 1 (λ v, f v.head) ↔ partrec f :=
part_iff.trans ⟨
  λ h, (h.comp $ (primrec.vector_of_fn $
    λ i, primrec.id).to_comp).of_eq (λ v, by simp),
  λ h, h.comp vector_head⟩

theorem part_iff₂ {f : ℕ → ℕ →. ℕ} :
  @partrec' 2 (λ v, f v.head v.tail.head) ↔ partrec₂ f :=
part_iff.trans ⟨
  λ h, (h.comp $ vector_cons.comp fst $
    vector_cons.comp snd (const nil)).of_eq (λ v, by simp),
  λ h, h.comp vector_head (vector_head.comp vector_tail)⟩

theorem vec_iff {m n f} : @vec m n f ↔ computable f :=
⟨λ h, by simpa using vector_of_fn (λ i, to_part (h i)),
 λ h i, of_part $ vector_nth.comp h (const i)⟩

end nat.partrec'
