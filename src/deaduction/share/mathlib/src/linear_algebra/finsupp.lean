/-
Copyright (c) 2019 Johannes Hölzl. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Author: Johannes Hölzl

Linear structures on function with finite support `α →₀ M`.
-/
import data.monoid_algebra

noncomputable theory

open set linear_map submodule

open_locale classical

namespace finsupp

variables {α : Type*} {M : Type*} {N : Type*} {R : Type*}
variables [ring R] [add_comm_group M] [module R M] [add_comm_group N] [module R N]

def lsingle (a : α) : M →ₗ[R] (α →₀ M) :=
⟨single a, assume a b, single_add, assume c b, (smul_single _ _ _).symm⟩

def lapply (a : α) : (α →₀ M) →ₗ[R] M := ⟨λg, g a, assume a b, rfl, assume a b, rfl⟩

section lsubtype_domain
variables (s : set α)

def lsubtype_domain : (α →₀ M) →ₗ[R] (s →₀ M) :=
⟨subtype_domain (λx, x ∈ s), assume a b, subtype_domain_add, assume c a, ext $ assume a, rfl⟩

lemma lsubtype_domain_apply (f : α →₀ M) :
  (lsubtype_domain s : (α →₀ M) →ₗ[R] (s →₀ M)) f = subtype_domain (λx, x ∈ s) f := rfl

end lsubtype_domain

@[simp] lemma lsingle_apply (a : α) (b : M) : (lsingle a : M →ₗ[R] (α →₀ M)) b = single a b  :=
rfl

@[simp] lemma lapply_apply (a : α) (f : α →₀ M) : (lapply a : (α →₀ M) →ₗ[R] M) f = f a  :=
rfl

@[simp] lemma ker_lsingle (a : α) : (lsingle a : M →ₗ[R] (α →₀ M)).ker = ⊥ :=
ker_eq_bot.2 (single_injective a)

lemma lsingle_range_le_ker_lapply (s t : set α) (h : disjoint s t) :
  (⨆a∈s, (lsingle a : M →ₗ[R] (α →₀ M)).range) ≤ (⨅a∈t, ker (lapply a)) :=
begin
  refine supr_le (assume a₁, supr_le $ assume h₁, range_le_iff_comap.2 _),
  simp only [(ker_comp _ _).symm, eq_top_iff, le_def', mem_ker, comap_infi, mem_infi],
  assume b hb a₂ h₂,
  have : a₁ ≠ a₂ := assume eq, h ⟨h₁, eq.symm ▸ h₂⟩,
  exact single_eq_of_ne this
end

lemma infi_ker_lapply_le_bot : (⨅a, ker (lapply a : (α →₀ M) →ₗ[R] M)) ≤ ⊥ :=
begin
  simp only [le_def', mem_infi, mem_ker, mem_bot, lapply_apply],
  exact assume a h, finsupp.ext h
end

lemma supr_lsingle_range : (⨆a, (lsingle a : M →ₗ[R] (α →₀ M)).range) = ⊤ :=
begin
  refine (eq_top_iff.2 $ le_def'.2 $ assume f _, _),
  rw [← sum_single f],
  refine sum_mem _ (assume a ha, submodule.mem_supr_of_mem _ a $ set.mem_image_of_mem _ trivial)
end

lemma disjoint_lsingle_lsingle (s t : set α) (hs : disjoint s t) :
  disjoint (⨆a∈s, (lsingle a : M →ₗ[R] (α →₀ M)).range) (⨆a∈t, (lsingle a).range) :=
begin
  refine disjoint.mono
    (lsingle_range_le_ker_lapply _ _ $ disjoint_compl s)
    (lsingle_range_le_ker_lapply _ _ $ disjoint_compl t)
    (le_trans (le_infi $ assume i, _) infi_ker_lapply_le_bot),
  classical,
  by_cases his : i ∈ s,
  { by_cases hit : i ∈ t,
    { exact (hs ⟨his, hit⟩).elim },
    exact inf_le_right_of_le (infi_le_of_le i $ infi_le _ hit) },
  exact inf_le_left_of_le (infi_le_of_le i $ infi_le _ his)
end

lemma span_single_image (s : set M) (a : α) :
  submodule.span R (single a '' s) = (submodule.span R s).map (lsingle a) :=
by rw ← span_image; refl

variables (M R)

def supported (s : set α) : submodule R (α →₀ M) :=
begin
  refine ⟨ {p | ↑p.support ⊆ s }, _, _, _ ⟩,
  { simp only [subset_def, finset.mem_coe, set.mem_set_of_eq, mem_support_iff, zero_apply],
    assume h ha, exact (ha rfl).elim },
  { assume p q hp hq,
    refine subset.trans
      (subset.trans (finset.coe_subset.2 support_add) _) (union_subset hp hq),
    rw [finset.coe_union] },
  { assume a p hp,
    refine subset.trans (finset.coe_subset.2 support_smul) hp }
end

variables {M}

lemma mem_supported {s : set α} (p : α →₀ M) : p ∈ (supported M R s) ↔ ↑p.support ⊆ s :=
iff.rfl

lemma mem_supported' {s : set α}  (p : α →₀ M) :
  p ∈ supported M R s ↔ ∀ x ∉ s, p x = 0 :=
by haveI := classical.dec_pred (λ (x : α), x ∈ s);
   simp [mem_supported, set.subset_def, not_imp_comm]

lemma single_mem_supported {s : set α} {a : α} (b : M) (h : a ∈ s) :
  single a b ∈ supported M R s :=
set.subset.trans support_single_subset (finset.singleton_subset_set_iff.2 h)

lemma supported_eq_span_single (s : set α) :
  supported R R s = span R ((λ i, single i 1) '' s) :=
begin
  refine (span_eq_of_le _ _ (le_def'.2 $ λ l hl, _)).symm,
  { rintro _ ⟨_, hp, rfl ⟩ , exact single_mem_supported R 1 hp },
  { rw ← l.sum_single,
    refine sum_mem _ (λ i il, _),
    convert @smul_mem R (α →₀ R) _ _ _ _ (single i 1) (l i) _,
    { simp },
    apply subset_span,
    apply set.mem_image_of_mem _ (hl il) }
end

variables (M R)

def restrict_dom (s : set α) : (α →₀ M) →ₗ supported M R s :=
linear_map.cod_restrict _
  { to_fun := filter (∈ s),
    map_add' := λ l₁ l₂, filter_add,
    map_smul' := λ a l, filter_smul }
  (λ l, (mem_supported' _ _).2 $ λ x, filter_apply_neg (∈ s) l)

variables {M R}

section
@[simp] theorem restrict_dom_apply (s : set α) (l : α →₀ M) :
  ((restrict_dom M R s : (α →₀ M) →ₗ supported M R s) l : α →₀ M) = finsupp.filter (∈ s) l := rfl
end

theorem restrict_dom_comp_subtype (s : set α) :
  (restrict_dom M R s).comp (submodule.subtype _) = linear_map.id :=
begin
  ext l,
  apply subtype.coe_ext.2,
  simp,
  ext a,
  by_cases a ∈ s,
  { simp [h] },
  { rw [filter_apply_neg (λ x, x ∈ s) _ h],
    exact ((mem_supported' R l.1).1 l.2 a h).symm }
end

theorem range_restrict_dom (s : set α) :
  (restrict_dom M R s).range = ⊤ :=
begin
  have := linear_map.range_comp (submodule.subtype _) (restrict_dom M R s),
  rw [restrict_dom_comp_subtype, linear_map.range_id] at this,
  exact eq_top_mono (submodule.map_mono le_top) this.symm
end

theorem supported_mono {s t : set α} (st : s ⊆ t) :
  supported M R s ≤ supported M R t :=
λ l h, set.subset.trans h st

@[simp] theorem supported_empty : supported M R (∅ : set α) = ⊥ :=
eq_bot_iff.2 $ λ l h, (submodule.mem_bot R).2 $
by ext; simp [*, mem_supported'] at *

@[simp] theorem supported_univ : supported M R (set.univ : set α) = ⊤ :=
eq_top_iff.2 $ λ l _, set.subset_univ _

theorem supported_Union {δ : Type*} (s : δ → set α) :
  supported M R (⋃ i, s i) = ⨆ i, supported M R (s i) :=
begin
  refine le_antisymm _ (supr_le $ λ i, supported_mono $ set.subset_Union _ _),
  haveI := classical.dec_pred (λ x, x ∈ (⋃ i, s i)),
  suffices : ((submodule.subtype _).comp (restrict_dom M R (⋃ i, s i))).range ≤ ⨆ i, supported M R (s i),
  { rwa [linear_map.range_comp, range_restrict_dom, map_top, range_subtype] at this },
  rw [range_le_iff_comap, eq_top_iff],
  rintro l ⟨⟩,
  apply finsupp.induction l, {exact zero_mem _},
  refine λ x a l hl a0, add_mem _ _,
  haveI := classical.dec_pred (λ x, ∃ i, x ∈ s i),
  by_cases (∃ i, x ∈ s i); simp [h],
  { cases h with i hi,
    exact le_supr (λ i, supported M R (s i)) i (single_mem_supported R _ hi) },
  { rw filter_single_of_neg,
    { simp },
    { exact h } }
end

theorem supported_union (s t : set α) :
  supported M R (s ∪ t) = supported M R s ⊔ supported M R t :=
by erw [set.union_eq_Union, supported_Union, supr_bool_eq]; refl

theorem supported_Inter {ι : Type*} (s : ι → set α) :
  supported M R (⋂ i, s i) = ⨅ i, supported M R (s i) :=
begin
  refine le_antisymm (le_infi $ λ i, supported_mono $ set.Inter_subset _ _) _,
  simp [le_def, infi_coe, set.subset_def],
  exact λ l, set.subset_Inter
end

def supported_equiv_finsupp (s : set α) : (supported M R s) ≃ₗ[R] (s →₀ M) :=
begin
  let F : (supported M R s) ≃ (s →₀ M) := restrict_support_equiv s M,
  refine F.to_linear_equiv _,
  have : (F : (supported M R s) → (↥s →₀ M)) = ((lsubtype_domain s : (α →₀ M) →ₗ[R] (s →₀ M)).comp
    (submodule.subtype (supported M R s))) := rfl,
  rw this,
  exact linear_map.is_linear _
end

/-- finsupp.sum as a linear map. -/
def lsum (f : α → M →ₗ[R] N) : (α →₀ M) →ₗ[R] N :=
⟨λ d, d.sum (λ i, f i),
  assume d₁ d₂, by simp [sum_add_index],
  assume a d, by simp [sum_smul_index', smul_sum]⟩

@[simp] lemma coe_lsum (f : α → M →ₗ[R] N) : (lsum f : (α →₀ M) → N) = λ d, d.sum (λ i, f i) := rfl

theorem lsum_apply (f : α → M →ₗ[R] N) (l : α →₀ M) :
  finsupp.lsum f l = l.sum (λ b, f b) := rfl

theorem lsum_single (f : α → M →ₗ[R] N) (i : α) (m : M) :
  finsupp.lsum f (finsupp.single i m) = f i m :=
finsupp.sum_single_index (f i).map_zero

section lmap_domain
variables {α' : Type*} {α'' : Type*} (M R)

def lmap_domain (f : α → α') : (α →₀ M) →ₗ[R] (α' →₀ M) :=
⟨map_domain f, assume a b, map_domain_add, map_domain_smul⟩

@[simp] theorem lmap_domain_apply (f : α → α') (l : α →₀ M) :
  (lmap_domain M R f : (α →₀ M) →ₗ[R] (α' →₀ M)) l = map_domain f l := rfl

@[simp] theorem lmap_domain_id : (lmap_domain M R id : (α →₀ M) →ₗ[R] α →₀ M) = linear_map.id :=
linear_map.ext $ λ l, map_domain_id

theorem lmap_domain_comp (f : α → α') (g : α' → α'') :
  lmap_domain M R (g ∘ f) = (lmap_domain M R g).comp (lmap_domain M R f) :=
linear_map.ext $ λ l, map_domain_comp

theorem supported_comap_lmap_domain (f : α → α') (s : set α') :
  supported M R (f ⁻¹' s) ≤ (supported M R s).comap (lmap_domain M R f) :=
λ l (hl : ↑l.support ⊆ f ⁻¹' s),
show ↑(map_domain f l).support ⊆ s, begin
  rw [← set.image_subset_iff, ← finset.coe_image] at hl,
  exact set.subset.trans map_domain_support hl
end

theorem lmap_domain_supported [nonempty α] (f : α → α') (s : set α) :
  (supported M R s).map (lmap_domain M R f) = supported M R (f '' s) :=
begin
  inhabit α,
  refine le_antisymm (map_le_iff_le_comap.2 $
    le_trans (supported_mono $ set.subset_preimage_image _ _)
       (supported_comap_lmap_domain _ _ _ _)) _,
  intros l hl,
  refine ⟨(lmap_domain M R (function.inv_fun_on f s) : (α' →₀ M) →ₗ α →₀ M) l, λ x hx, _, _⟩,
  { rcases finset.mem_image.1 (map_domain_support hx) with ⟨c, hc, rfl⟩,
    exact function.inv_fun_on_mem (by simpa using hl hc) },
  { rw [← linear_map.comp_apply, ← lmap_domain_comp],
    refine (map_domain_congr $ λ c hc, _).trans map_domain_id,
    exact function.inv_fun_on_eq (by simpa using hl hc) }
end

theorem lmap_domain_disjoint_ker (f : α → α') {s : set α}
  (H : ∀ a b ∈ s, f a = f b → a = b) :
  disjoint (supported M R s) (lmap_domain M R f).ker :=
begin
  rintro l ⟨h₁, h₂⟩,
  rw [mem_coe, mem_ker, lmap_domain_apply, map_domain] at h₂,
  simp, ext x,
  haveI := classical.dec_pred (λ x, x ∈ s),
  by_cases xs : x ∈ s,
  { have : finsupp.sum l (λ a, finsupp.single (f a)) (f x) = 0, {rw h₂, refl},
    rw [finsupp.sum_apply, finsupp.sum, finset.sum_eq_single x] at this,
    { simpa [finsupp.single_apply] },
    { intros y hy xy, simp [mt (H _ _ (h₁ hy) xs) xy] },
    { simp {contextual := tt} } },
  { by_contra h, exact xs (h₁ $ finsupp.mem_support_iff.2 h) }
end

end lmap_domain

section total
variables (α) {α' : Type*} (M) {M' : Type*} (R)
          [add_comm_group M'] [module R M']
          (v : α → M) {v' : α' → M'}

/-- Interprets (l : α →₀ R) as linear combination of the elements in the family (v : α → M) and
    evaluates this linear combination. -/
protected def total : (α →₀ R) →ₗ M := finsupp.lsum (λ i, linear_map.id.smul_right (v i))

variables {α M v}

theorem total_apply (l : α →₀ R) :
  finsupp.total α M R v l = l.sum (λ i a, a • v i) := rfl

@[simp] theorem total_single (c : R) (a : α) :
  finsupp.total α M R v (single a c) = c • (v a) :=
by simp [total_apply, sum_single_index]

theorem total_range (h : function.surjective v) : (finsupp.total α M R v).range = ⊤ :=
begin
  apply range_eq_top.2,
  intros x,
  apply exists.elim (h x),
  exact λ i hi, ⟨single i 1, by simp [hi]⟩
end

lemma range_total : (finsupp.total α M R v).range = span R (range v) :=
begin
  ext x,
  split,
  { intros hx,
    rw [linear_map.mem_range] at hx,
    rcases hx with ⟨l, hl⟩,
    rw ← hl,
    rw finsupp.total_apply,
    unfold finsupp.sum,
    apply sum_mem (span R (range v)),
    exact λ i hi, submodule.smul_mem _ _ (subset_span (mem_range_self i)) },
  { apply span_le.2,
    intros x hx,
    rcases hx with ⟨i, hi⟩,
    rw [mem_coe, linear_map.mem_range],
    use finsupp.single i 1,
    simp [hi] }
end

theorem lmap_domain_total (f : α → α') (g : M →ₗ[R] M') (h : ∀ i, g (v i) = v' (f i)) :
  (finsupp.total α' M' R v').comp (lmap_domain R R f) = g.comp (finsupp.total α M R v) :=
by ext l; simp [total_apply, finsupp.sum_map_domain_index, add_smul, h]

theorem total_emb_domain (f : α ↪ α') (l : α →₀ R) :
  (finsupp.total α' M' R v') (emb_domain f l) = (finsupp.total α M' R (v' ∘ f)) l :=
by simp [total_apply, finsupp.sum, support_emb_domain, emb_domain_apply]

theorem total_map_domain (f : α → α') (hf : function.injective f) (l : α →₀ R) :
  (finsupp.total α' M' R v') (map_domain f l) = (finsupp.total α M' R (v' ∘ f)) l :=
begin
  have : map_domain f l = emb_domain ⟨f, hf⟩ l,
  { rw emb_domain_eq_map_domain ⟨f, hf⟩,
    refl },
  rw this,
  apply total_emb_domain R ⟨f, hf⟩ l
end

theorem span_eq_map_total (s : set α):
  span R (v '' s) = submodule.map (finsupp.total α M R v) (supported R R s) :=
begin
  apply span_eq_of_le,
  { intros x hx,
    rw set.mem_image at hx,
    apply exists.elim hx,
    intros i hi,
    exact ⟨_, finsupp.single_mem_supported R 1 hi.1, by simp [hi.2]⟩ },
  { refine map_le_iff_le_comap.2 (λ z hz, _),
    have : ∀i, z i • v i ∈ span R (v '' s),
    { intro c,
      haveI := classical.dec_pred (λ x, x ∈ s),
      by_cases c ∈ s,
      { exact smul_mem _ _ (subset_span (set.mem_image_of_mem _ h)) },
      { simp [(finsupp.mem_supported' R _).1 hz _ h] } },
    refine sum_mem _ _, simp [this] }
end

theorem mem_span_iff_total {s : set α} {x : M} :
  x ∈ span R (v '' s) ↔ ∃ l ∈ supported R R s, finsupp.total α M R v l = x :=
by rw span_eq_map_total; simp

variables (α) (M) (v)

protected def total_on (s : set α) : supported R R s →ₗ[R] span R (v '' s) :=
linear_map.cod_restrict _ ((finsupp.total _ _ _ v).comp (submodule.subtype (supported R R s))) $
  λ ⟨l, hl⟩, (mem_span_iff_total _).2 ⟨l, hl, rfl⟩

variables {α} {M} {v}

theorem total_on_range (s : set α) : (finsupp.total_on α M R v s).range = ⊤ :=
by rw [finsupp.total_on, linear_map.range, linear_map.map_cod_restrict, ← linear_map.range_le_iff_comap,
  range_subtype, map_top, linear_map.range_comp, range_subtype]; exact le_of_eq (span_eq_map_total _ _)

theorem total_comp (f : α' → α) :
  (finsupp.total α' M R (v ∘ f)) = (finsupp.total α M R v).comp (lmap_domain R R f) :=
begin
 ext l,
 simp [total_apply],
 rw sum_map_domain_index; simp [add_smul],
end

lemma total_comap_domain
 (f : α → α') (l : α' →₀ R) (hf : set.inj_on f (f ⁻¹' ↑l.support)) :
 finsupp.total α M R v (finsupp.comap_domain f l hf) = (l.support.preimage hf).sum (λ i, (l (f i)) • (v i)) :=
by rw finsupp.total_apply; refl

end total

/-- An equivalence of domains induces a linear equivalence of finitely supported functions. -/
protected def dom_lcongr
  {α₁ : Type*} {α₂ : Type*} (e : α₁ ≃ α₂) :
  (α₁ →₀ M) ≃ₗ[R] (α₂ →₀ M) :=
(finsupp.dom_congr e).to_linear_equiv
begin
  change is_linear_map R (lmap_domain M R e : (α₁ →₀ M) →ₗ[R] (α₂ →₀ M)),
  exact linear_map.is_linear _
end

@[simp] theorem dom_lcongr_single {α₁ : Type*} {α₂ : Type*} (e : α₁ ≃ α₂) (i : α₁) (m : M) :
  (finsupp.dom_lcongr e : _ ≃ₗ[R] _) (finsupp.single i m) = finsupp.single (e i) m :=
by simp [finsupp.dom_lcongr, equiv.to_linear_equiv, finsupp.dom_congr, map_domain_single]

noncomputable def congr {α' : Type*} (s : set α) (t : set α') (e : s ≃ t) :
  supported M R s ≃ₗ[R] supported M R t :=
begin
  haveI := classical.dec_pred (λ x, x ∈ s),
  haveI := classical.dec_pred (λ x, x ∈ t),
  refine linear_equiv.trans (finsupp.supported_equiv_finsupp s)
      (linear_equiv.trans _ (finsupp.supported_equiv_finsupp t).symm),
  exact finsupp.dom_lcongr e
end

/-- An equivalence of domain and a linear equivalence of codomain induce a linear equivalence of the
corresponding finitely supported functions. -/
def lcongr {ι κ : Sort*} (e₁ : ι ≃ κ) (e₂ : M ≃ₗ[R] N) : (ι →₀ M) ≃ₗ[R] (κ →₀ N) :=
(finsupp.dom_lcongr e₁).trans
{ to_fun := map_range e₂ e₂.map_zero,
  inv_fun := map_range e₂.symm e₂.symm.map_zero,
  left_inv := λ f, finsupp.induction f (by simp_rw map_range_zero) $ λ a b f ha hb ih,
    by rw [map_range_add e₂.map_add, map_range_add e₂.symm.map_add,
      map_range_single, map_range_single, e₂.symm_apply_apply, ih],
  right_inv := λ f, finsupp.induction f (by simp_rw map_range_zero) $ λ a b f ha hb ih,
    by rw [map_range_add e₂.symm.map_add, map_range_add e₂.map_add,
      map_range_single, map_range_single, e₂.apply_symm_apply, ih],
  map_add' := map_range_add e₂.map_add,
  map_smul' := λ c f, finsupp.induction f
    (by rw [smul_zero, map_range_zero, smul_zero]) $ λ a b f ha hb ih,
    by rw [smul_add, smul_single, map_range_add e₂.map_add, map_range_single, e₂.map_smul, ih,
      map_range_add e₂.map_add, smul_add, map_range_single, smul_single] }

@[simp] theorem lcongr_single {ι κ : Sort*} (e₁ : ι ≃ κ) (e₂ : M ≃ₗ[R] N)
  (i : ι) (m : M) : lcongr e₁ e₂ (finsupp.single i m) = finsupp.single (e₁ i) (e₂ m) :=
by simp [lcongr]

end finsupp

variables {R : Type*} {M : Type*} {N : Type*}
variables [ring R] [add_comm_group M] [module R M] [add_comm_group N] [module R N]

lemma linear_map.map_finsupp_total
  (f : M →ₗ[R] N) {ι : Type*} {g : ι → M} (l : ι →₀ R) :
  f (finsupp.total ι M R g l) = finsupp.total ι N R (f ∘ g) l :=
by simp only [finsupp.total_apply, finsupp.total_apply, finsupp.sum, f.map_sum, f.map_smul]

lemma submodule.exists_finset_of_mem_supr
  {ι : Sort*} (p : ι → submodule R M) {m : M} (hm : m ∈ ⨆ i, p i) :
  ∃ s : finset ι, m ∈ ⨆ i ∈ s, p i :=
begin
  obtain ⟨f, hf, rfl⟩ : ∃ f ∈ finsupp.supported R R (⋃ i, ↑(p i)), finsupp.total M M R id f = m,
  { have aux : (id : M → M) '' (⋃ (i : ι), ↑(p i)) = (⋃ (i : ι), ↑(p i)) := set.image_id _,
    rwa [supr_eq_span, ← aux, finsupp.mem_span_iff_total R] at hm },
  let t : finset M := f.support,
  have ht : ∀ x : {x // x ∈ t}, ∃ i, ↑x ∈ p i,
  { intros x,
    rw finsupp.mem_supported at hf,
    specialize hf x.2,
    rwa set.mem_Union at hf },
  choose g hg using ht,
  let s : finset ι := finset.univ.image g,
  use s,
  simp only [mem_supr, supr_le_iff],
  assume N hN,
  rw [finsupp.total_apply, finsupp.sum, ← submodule.mem_coe],
  apply N.sum_mem,
  assume x hx,
  apply submodule.smul_mem,
  let i : ι := g ⟨x, hx⟩,
  have hi : i ∈ s, { rw finset.mem_image, exact ⟨⟨x, hx⟩, finset.mem_univ _, rfl⟩ },
  exact hN i hi (hg _),
end

section finsupp_lequiv_direct_sum

variables (R M) (ι : Type*) [decidable_eq ι]

/-- The finitely supported functions ι →₀ M are in linear equivalence with the direct sum of
copies of M indexed by ι. -/
def finsupp_lequiv_direct_sum : (ι →₀ M) ≃ₗ[R] direct_sum ι (λ i, M) :=
linear_equiv.of_linear
  (finsupp.lsum $ direct_sum.lof R ι (λ _, M))
  (direct_sum.to_module _ _ _ finsupp.lsingle)
  (linear_map.ext $ direct_sum.to_module.ext _ $ λ i,
    linear_map.ext $ λ x, by simp [finsupp.sum_single_index])
  (linear_map.ext $ λ f, finsupp.ext $ λ i, by simp [finsupp.lsum_apply])

@[simp] theorem finsupp_lequiv_direct_sum_single (i : ι) (m : M) :
  finsupp_lequiv_direct_sum R M ι (finsupp.single i m) = direct_sum.lof R ι _ i m :=
finsupp.sum_single_index $ direct_sum.of_zero i

@[simp] theorem finsupp_lequiv_direct_sum_symm_lof (i : ι) (m : M) :
  (finsupp_lequiv_direct_sum R M ι).symm (direct_sum.lof R ι _ i m) = finsupp.single i m :=
direct_sum.to_module_lof _ _ _

end finsupp_lequiv_direct_sum

section tensor_product

open_locale tensor_product

/-- The tensor product of ι →₀ M and κ →₀ N is linearly equivalent to (ι × κ) →₀ (M ⊗ N). -/
def finsupp_tensor_finsupp (R M N ι κ : Sort*) [comm_ring R]
  [add_comm_group M] [module R M] [add_comm_group N] [module R N] :
  (ι →₀ M) ⊗[R] (κ →₀ N) ≃ₗ[R] (ι × κ) →₀ (M ⊗[R] N) :=
linear_equiv.trans
  (tensor_product.congr (finsupp_lequiv_direct_sum R M ι) (finsupp_lequiv_direct_sum R N κ)) $
linear_equiv.trans
  (tensor_product.direct_sum R ι κ (λ _, M) (λ _, N))
  (finsupp_lequiv_direct_sum R (M ⊗[R] N) (ι × κ)).symm

@[simp] theorem finsupp_tensor_finsupp_single (R M N ι κ : Sort*) [comm_ring R]
  [add_comm_group M] [module R M] [add_comm_group N] [module R N]
  (i : ι) (m : M) (k : κ) (n : N) :
  finsupp_tensor_finsupp R M N ι κ (finsupp.single i m ⊗ₜ finsupp.single k n) =
  finsupp.single (i, k) (m ⊗ₜ n) :=
by simp [finsupp_tensor_finsupp]

@[simp] theorem finsupp_tensor_finsupp_symm_single (R M N ι κ : Sort*) [comm_ring R]
  [add_comm_group M] [module R M] [add_comm_group N] [module R N]
  (i : ι × κ) (m : M) (n : N) :
  (finsupp_tensor_finsupp R M N ι κ).symm (finsupp.single i (m ⊗ₜ n)) =
  (finsupp.single i.1 m ⊗ₜ finsupp.single i.2 n) :=
prod.cases_on i $ λ i k, (linear_equiv.symm_apply_eq _).2
  (finsupp_tensor_finsupp_single _ _ _ _ _ _ _ _ _).symm

end tensor_product
