/-
Copyright (c) 2017 Johannes Hölzl. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Johannes Hölzl, Sébastien Gouëzel, Patrick Massot

Uniform embeddings of uniform spaces. Extension of uniform continuous functions.
-/
import topology.uniform_space.cauchy
import topology.uniform_space.separation
import topology.dense_embedding

open filter topological_space set classical
open_locale classical uniformity topological_space filter

section
variables {α : Type*} {β : Type*} {γ : Type*}
          [uniform_space α] [uniform_space β] [uniform_space γ]
universe u

structure uniform_inducing (f : α → β) : Prop :=
(comap_uniformity : comap (λx:α×α, (f x.1, f x.2)) (𝓤 β) = 𝓤 α)

lemma uniform_inducing.mk' {f : α → β} (h : ∀ s, s ∈ 𝓤 α ↔
    ∃ t ∈ 𝓤 β, ∀ x y : α, (f x, f y) ∈ t → (x, y) ∈ s) : uniform_inducing f :=
⟨by simp [eq_comm, filter.ext_iff, subset_def, h]⟩

lemma uniform_inducing.comp {g : β → γ} (hg : uniform_inducing g)
  {f : α → β} (hf : uniform_inducing f) : uniform_inducing (g ∘ f) :=
⟨ by rw [show (λ (x : α × α), ((g ∘ f) x.1, (g ∘ f) x.2)) =
         (λ y : β × β, (g y.1, g y.2)) ∘ (λ x : α × α, (f x.1, f x.2)), by ext ; simp,
        ← filter.comap_comap_comp, hg.1, hf.1]⟩

structure uniform_embedding (f : α → β) extends uniform_inducing f : Prop :=
(inj : function.injective f)

lemma uniform_embedding_subtype_val {p : α → Prop} :
  uniform_embedding (subtype.val : subtype p → α) :=
{ comap_uniformity := rfl,
  inj := subtype.val_injective }

lemma uniform_embedding_subtype_coe {p : α → Prop} :
  uniform_embedding (coe : subtype p → α) :=
uniform_embedding_subtype_val

lemma uniform_embedding_set_inclusion {s t : set α} (hst : s ⊆ t) :
  uniform_embedding (inclusion hst) :=
{ comap_uniformity :=
    by { erw [uniformity_subtype, uniformity_subtype, comap_comap_comp], congr },
  inj := inclusion_injective hst }

lemma uniform_embedding.comp {g : β → γ} (hg : uniform_embedding g)
  {f : α → β} (hf : uniform_embedding f) : uniform_embedding (g ∘ f) :=
{ inj := hg.inj.comp hf.inj,
  ..hg.to_uniform_inducing.comp hf.to_uniform_inducing }

theorem uniform_embedding_def {f : α → β} :
  uniform_embedding f ↔ function.injective f ∧ ∀ s, s ∈ 𝓤 α ↔
    ∃ t ∈ 𝓤 β, ∀ x y : α, (f x, f y) ∈ t → (x, y) ∈ s :=
begin
  split,
  { rintro ⟨⟨h⟩, h'⟩,
    rw [eq_comm, filter.ext_iff] at h,
    simp [*, subset_def] },
  { rintro ⟨h, h'⟩,
    refine uniform_embedding.mk ⟨_⟩ h,
    rw [eq_comm, filter.ext_iff],
    simp [*, subset_def] }
end

theorem uniform_embedding_def' {f : α → β} :
  uniform_embedding f ↔ function.injective f ∧ uniform_continuous f ∧
    ∀ s, s ∈ 𝓤 α →
      ∃ t ∈ 𝓤 β, ∀ x y : α, (f x, f y) ∈ t → (x, y) ∈ s :=
by simp [uniform_embedding_def, uniform_continuous_def]; exact
⟨λ ⟨I, H⟩, ⟨I, λ s su, (H _).2 ⟨s, su, λ x y, id⟩, λ s, (H s).1⟩,
 λ ⟨I, H₁, H₂⟩, ⟨I, λ s, ⟨H₂ s,
   λ ⟨t, tu, h⟩, sets_of_superset _ (H₁ t tu) (λ ⟨a, b⟩, h a b)⟩⟩⟩

lemma uniform_inducing.uniform_continuous {f : α → β}
  (hf : uniform_inducing f) : uniform_continuous f :=
by simp [uniform_continuous, hf.comap_uniformity.symm, tendsto_comap]

lemma uniform_inducing.uniform_continuous_iff {f : α → β} {g : β → γ} (hg : uniform_inducing g) :
  uniform_continuous f ↔ uniform_continuous (g ∘ f) :=
by simp [uniform_continuous, tendsto]; rw [← hg.comap_uniformity, ← map_le_iff_le_comap, filter.map_map]

lemma uniform_inducing.inducing {f : α → β} (h : uniform_inducing f) : inducing f :=
begin
  refine ⟨eq_of_nhds_eq_nhds $ assume a, _ ⟩,
  rw [nhds_induced, nhds_eq_uniformity, nhds_eq_uniformity, ← h.comap_uniformity,
    comap_lift'_eq, comap_lift'_eq2];
    { refl <|> exact monotone_preimage }
end

lemma uniform_inducing.prod {α' : Type*} {β' : Type*} [uniform_space α'] [uniform_space β']
  {e₁ : α → α'} {e₂ : β → β'} (h₁ : uniform_inducing e₁) (h₂ : uniform_inducing e₂) :
  uniform_inducing (λp:α×β, (e₁ p.1, e₂ p.2)) :=
⟨by simp [(∘), uniformity_prod, h₁.comap_uniformity.symm, h₂.comap_uniformity.symm,
           comap_inf, comap_comap_comp]⟩

lemma uniform_inducing.dense_inducing {f : α → β} (h : uniform_inducing f) (hd : dense_range f) :
  dense_inducing f :=
{ dense   := hd,
  induced := h.inducing.induced }

lemma uniform_embedding.embedding {f : α → β} (h : uniform_embedding f) : embedding f :=
{ induced := h.to_uniform_inducing.inducing.induced,
  inj := h.inj }

lemma uniform_embedding.dense_embedding {f : α → β} (h : uniform_embedding f) (hd : dense_range f) :
  dense_embedding f :=
{ dense   := hd,
  inj     := h.inj,
  induced := h.embedding.induced }

lemma closure_image_mem_nhds_of_uniform_inducing
  {s : set (α×α)} {e : α → β} (b : β)
  (he₁ : uniform_inducing e) (he₂ : dense_inducing e) (hs : s ∈ 𝓤 α) :
  ∃a, closure (e '' {a' | (a, a') ∈ s}) ∈ 𝓝 b :=
have s ∈ comap (λp:α×α, (e p.1, e p.2)) (𝓤 β),
  from he₁.comap_uniformity.symm ▸ hs,
let ⟨t₁, ht₁u, ht₁⟩ := this in
have ht₁ : ∀p:α×α, (e p.1, e p.2) ∈ t₁ → p ∈ s, from ht₁,
let ⟨t₂, ht₂u, ht₂s, ht₂c⟩ := comp_symm_of_uniformity ht₁u in
let ⟨t, htu, hts, htc⟩ := comp_symm_of_uniformity ht₂u in
have preimage e {b' | (b, b') ∈ t₂} ∈ comap e (𝓝 b),
  from preimage_mem_comap $ mem_nhds_left b ht₂u,
let ⟨a, (ha : (b, e a) ∈ t₂)⟩ := nonempty_of_mem_sets (he₂.comap_nhds_ne_bot) this in
have ∀b' (s' : set (β × β)), (b, b') ∈ t → s' ∈ 𝓤 β →
  ({y : β | (b', y) ∈ s'} ∩ e '' {a' : α | (a, a') ∈ s}).nonempty,
  from assume b' s' hb' hs',
  have preimage e {b'' | (b', b'') ∈ s' ∩ t} ∈ comap e (𝓝 b'),
    from preimage_mem_comap $ mem_nhds_left b' $ inter_mem_sets hs' htu,
  let ⟨a₂, ha₂s', ha₂t⟩ := nonempty_of_mem_sets (he₂.comap_nhds_ne_bot) this in
  have (e a, e a₂) ∈ t₁,
    from ht₂c $ prod_mk_mem_comp_rel (ht₂s ha) $ htc $ prod_mk_mem_comp_rel hb' ha₂t,
  have e a₂ ∈ {b'':β | (b', b'') ∈ s'} ∩ e '' {a' | (a, a') ∈ s},
    from ⟨ha₂s', mem_image_of_mem _ $ ht₁ (a, a₂) this⟩,
  ⟨_, this⟩,
have ∀b', (b, b') ∈ t → 𝓝 b' ⊓ 𝓟 (e '' {a' | (a, a') ∈ s}) ≠ ⊥,
begin
  intros b' hb',
  rw [nhds_eq_uniformity, lift'_inf_principal_eq, lift'_ne_bot_iff],
  exact assume s, this b' s hb',
  exact monotone_inter monotone_preimage monotone_const
end,
have ∀b', (b, b') ∈ t → b' ∈ closure (e '' {a' | (a, a') ∈ s}),
  from assume b' hb', by rw [closure_eq_cluster_pts]; exact this b' hb',
⟨a, (𝓝 b).sets_of_superset (mem_nhds_left b htu) this⟩

lemma uniform_embedding_subtype_emb (p : α → Prop) {e : α → β} (ue : uniform_embedding e)
  (de : dense_embedding e) : uniform_embedding (dense_embedding.subtype_emb p e) :=
{ comap_uniformity := by simp [comap_comap_comp, (∘), dense_embedding.subtype_emb,
           uniformity_subtype, ue.comap_uniformity.symm],
  inj := (de.subtype p).inj }

lemma uniform_embedding.prod {α' : Type*} {β' : Type*} [uniform_space α'] [uniform_space β']
  {e₁ : α → α'} {e₂ : β → β'} (h₁ : uniform_embedding e₁) (h₂ : uniform_embedding e₂) :
  uniform_embedding (λp:α×β, (e₁ p.1, e₂ p.2)) :=
{ inj := h₁.inj.prod h₂.inj,
  ..h₁.to_uniform_inducing.prod h₂.to_uniform_inducing }

lemma is_complete_of_complete_image {m : α → β} {s : set α} (hm : uniform_inducing m)
  (hs : is_complete (m '' s)) : is_complete s :=
begin
  intros f hf hfs,
  rw le_principal_iff at hfs,
  obtain ⟨_, ⟨x, hx, rfl⟩, hyf⟩ : ∃ y ∈ m '' s, map m f ≤ 𝓝 y,
    from hs (f.map m) (cauchy_map hm.uniform_continuous hf)
      (le_principal_iff.2 (image_mem_map hfs)),
  rw [map_le_iff_le_comap, ← nhds_induced, ← hm.inducing.induced] at hyf,
  exact ⟨x, hx, hyf⟩
end

/-- A set is complete iff its image under a uniform embedding is complete. -/
lemma is_complete_image_iff {m : α → β} {s : set α} (hm : uniform_embedding m) :
  is_complete (m '' s) ↔ is_complete s :=
begin
  refine ⟨is_complete_of_complete_image hm.to_uniform_inducing, λ c f hf fs, _⟩,
  rw filter.le_principal_iff at fs,
  let f' := comap m f,
  have cf' : cauchy f',
  { have : comap m f ≠ ⊥,
    { refine comap_ne_bot (λt ht, _),
      have A : t ∩ m '' s ∈ f := filter.inter_mem_sets ht fs,
      obtain ⟨x, ⟨xt, ⟨y, ys, rfl⟩⟩⟩ : (t ∩ m '' s).nonempty,
        from nonempty_of_mem_sets hf.1 A,
      exact ⟨y, xt⟩ },
    apply cauchy_comap _ hf this,
    simp only [hm.comap_uniformity, le_refl] },
  have : f' ≤ 𝓟 s := by simp [f']; exact
    ⟨m '' s, by simpa using fs, by simp [preimage_image_eq s hm.inj]⟩,
  rcases c f' cf' this with ⟨x, xs, hx⟩,
  existsi [m x, mem_image_of_mem m xs],
  rw [(uniform_embedding.embedding hm).induced, nhds_induced] at hx,
  calc f = map m f' : (map_comap $ filter.mem_sets_of_superset fs $ image_subset_range _ _).symm
    ... ≤ map m (comap m (𝓝 (m x))) : map_mono hx
    ... ≤ 𝓝 (m x) : map_comap_le
end

lemma complete_space_iff_is_complete_range {f : α → β} (hf : uniform_embedding f) :
  complete_space α ↔ is_complete (range f) :=
by rw [complete_space_iff_is_complete_univ, ← is_complete_image_iff hf, image_univ]

lemma complete_space_congr {e : α ≃ β} (he : uniform_embedding e) :
  complete_space α ↔ complete_space β :=
by rw [complete_space_iff_is_complete_range he, e.range_eq_univ,
  complete_space_iff_is_complete_univ]

lemma complete_space_coe_iff_is_complete {s : set α} :
  complete_space s ↔ is_complete s :=
(complete_space_iff_is_complete_range uniform_embedding_subtype_coe).trans $
  by rw [range_coe_subtype]

lemma is_complete.complete_space_coe {s : set α} (hs : is_complete s) :
  complete_space s :=
complete_space_coe_iff_is_complete.2 hs

lemma is_closed.complete_space_coe [complete_space α] {s : set α} (hs : is_closed s) :
  complete_space s :=
(is_complete_of_is_closed hs).complete_space_coe

lemma complete_space_extension {m : β → α} (hm : uniform_inducing m) (dense : dense_range m)
  (h : ∀f:filter β, cauchy f → ∃x:α, map m f ≤ 𝓝 x) : complete_space α :=
⟨assume (f : filter α), assume hf : cauchy f,
let
  p : set (α × α) → set α → set α := λs t, {y : α| ∃x:α, x ∈ t ∧ (x, y) ∈ s},
  g := (𝓤 α).lift (λs, f.lift' (p s))
in
have mp₀ : monotone p,
  from assume a b h t s ⟨x, xs, xa⟩, ⟨x, xs, h xa⟩,
have mp₁ : ∀{s}, monotone (p s),
  from assume s a b h x ⟨y, ya, yxs⟩, ⟨y, h ya, yxs⟩,

have f ≤ g, from
  le_infi $ assume s, le_infi $ assume hs, le_infi $ assume t, le_infi $ assume ht,
  le_principal_iff.mpr $
  mem_sets_of_superset ht $ assume x hx, ⟨x, hx, refl_mem_uniformity hs⟩,

have g ≠ ⊥, from ne_bot_of_le_ne_bot hf.left this,

have comap m g ≠ ⊥, from comap_ne_bot $ assume t ht,
  let ⟨t', ht', ht_mem⟩ := (mem_lift_sets $ monotone_lift' monotone_const mp₀).mp ht in
  let ⟨t'', ht'', ht'_sub⟩ := (mem_lift'_sets mp₁).mp ht_mem in
  let ⟨x, (hx : x ∈ t'')⟩ := nonempty_of_mem_sets hf.left ht'' in
  have h₀ : 𝓝 x ⊓ 𝓟 (range m) ≠ ⊥,
    by simpa [dense_range, closure_eq_cluster_pts] using dense x,
  have h₁ : {y | (x, y) ∈ t'} ∈ 𝓝 x ⊓ 𝓟 (range m),
    from @mem_inf_sets_of_left α (𝓝 x) (𝓟 (range m)) _ $ mem_nhds_left x ht',
  have h₂ : range m ∈ 𝓝 x ⊓ 𝓟 (range m),
    from @mem_inf_sets_of_right α (𝓝 x) (𝓟 (range m)) _ $ subset.refl _,
  have {y | (x, y) ∈ t'} ∩ range m ∈ 𝓝 x ⊓ 𝓟 (range m),
    from @inter_mem_sets α (𝓝 x ⊓ 𝓟 (range m)) _ _ h₁ h₂,
  let ⟨y, xyt', b, b_eq⟩ := nonempty_of_mem_sets h₀ this in
  ⟨b, b_eq.symm ▸ ht'_sub ⟨x, hx, xyt'⟩⟩,

have cauchy g, from
  ⟨‹g ≠ ⊥›, assume s hs,
  let
    ⟨s₁, hs₁, (comp_s₁ : comp_rel s₁ s₁ ⊆ s)⟩ := comp_mem_uniformity_sets hs,
    ⟨s₂, hs₂, (comp_s₂ : comp_rel s₂ s₂ ⊆ s₁)⟩ := comp_mem_uniformity_sets hs₁,
    ⟨t, ht, (prod_t : set.prod t t ⊆ s₂)⟩ := mem_prod_same_iff.mp (hf.right hs₂)
  in
  have hg₁ : p (preimage prod.swap s₁) t ∈ g,
    from mem_lift (symm_le_uniformity hs₁) $ @mem_lift' α α f _ t ht,
  have hg₂ : p s₂ t ∈ g,
    from mem_lift hs₂ $ @mem_lift' α α f _ t ht,
  have hg : set.prod (p (preimage prod.swap s₁) t) (p s₂ t) ∈ filter.prod g g,
    from @prod_mem_prod α α _ _ g g hg₁ hg₂,
  (filter.prod g g).sets_of_superset hg
    (assume ⟨a, b⟩ ⟨⟨c₁, c₁t, hc₁⟩, ⟨c₂, c₂t, hc₂⟩⟩,
      have (c₁, c₂) ∈ set.prod t t, from ⟨c₁t, c₂t⟩,
      comp_s₁ $ prod_mk_mem_comp_rel hc₁ $
      comp_s₂ $ prod_mk_mem_comp_rel (prod_t this) hc₂)⟩,

have cauchy (filter.comap m g),
  from cauchy_comap (le_of_eq hm.comap_uniformity) ‹cauchy g› (by assumption),

let ⟨x, (hx : map m (filter.comap m g) ≤ 𝓝 x)⟩ := h _ this in
have cluster_pt x (map m (filter.comap m g)),
  from (le_nhds_iff_adhp_of_cauchy (cauchy_map hm.uniform_continuous this)).mp hx,
have cluster_pt x g,
  from  this.mono map_comap_le,

⟨x, calc f ≤ g : by assumption
  ... ≤ 𝓝 x : le_nhds_of_cauchy_adhp ‹cauchy g› this⟩⟩

lemma totally_bounded_preimage {f : α → β} {s : set β} (hf : uniform_embedding f)
  (hs : totally_bounded s) : totally_bounded (f ⁻¹' s) :=
λ t ht, begin
  rw ← hf.comap_uniformity at ht,
  rcases mem_comap_sets.2 ht with ⟨t', ht', ts⟩,
  rcases totally_bounded_iff_subset.1
    (totally_bounded_subset (image_preimage_subset f s) hs) _ ht' with ⟨c, cs, hfc, hct⟩,
  refine ⟨f ⁻¹' c, hfc.preimage (hf.inj.inj_on _), λ x h, _⟩,
  have := hct (mem_image_of_mem f h), simp at this ⊢,
  rcases this with ⟨z, zc, zt⟩,
  rcases cs zc with ⟨y, yc, rfl⟩,
  exact ⟨y, zc, ts (by exact zt)⟩
end

end

lemma uniform_embedding_comap {α : Type*} {β : Type*} {f : α → β} [u : uniform_space β]
  (hf : function.injective f) : @uniform_embedding α β (uniform_space.comap f u) u f :=
@uniform_embedding.mk _ _ (uniform_space.comap f u) _ _
  (@uniform_inducing.mk _ _ (uniform_space.comap f u) _ _ rfl) hf

section uniform_extension

variables {α : Type*} {β : Type*} {γ : Type*}
          [uniform_space α] [uniform_space β] [uniform_space γ]
          {e : β → α}
          (h_e : uniform_inducing e)
          (h_dense : dense_range e)
          {f : β → γ}
          (h_f : uniform_continuous f)

local notation `ψ` := (h_e.dense_inducing h_dense).extend f

lemma uniformly_extend_exists [complete_space γ] (a : α) :
  ∃c, tendsto f (comap e (𝓝 a)) (𝓝 c) :=
let de := (h_e.dense_inducing h_dense) in
have cauchy (𝓝 a), from cauchy_nhds,
have cauchy (comap e (𝓝 a)), from
  cauchy_comap (le_of_eq h_e.comap_uniformity) this de.comap_nhds_ne_bot,
have cauchy (map f (comap e (𝓝 a))), from
  cauchy_map h_f this,
complete_space.complete this

lemma uniform_extend_subtype [complete_space γ]
  {p : α → Prop} {e : α → β} {f : α → γ} {b : β} {s : set α}
  (hf : uniform_continuous (λx:subtype p, f x.val))
  (he : uniform_embedding e) (hd : ∀x:β, x ∈ closure (range e))
  (hb : closure (e '' s) ∈ 𝓝 b) (hs : is_closed s) (hp : ∀x∈s, p x) :
  ∃c, tendsto f (comap e (𝓝 b)) (𝓝 c) :=
have de : dense_embedding e,
  from he.dense_embedding hd,
have de' : dense_embedding (dense_embedding.subtype_emb p e),
  by exact de.subtype p,
have ue' : uniform_embedding (dense_embedding.subtype_emb p e),
  from uniform_embedding_subtype_emb _ he de,
have b ∈ closure (e '' {x | p x}),
  from (closure_mono $ monotone_image $ hp) (mem_of_nhds hb),
let ⟨c, (hc : tendsto (f ∘ subtype.val) (comap (dense_embedding.subtype_emb p e) (𝓝 ⟨b, this⟩)) (𝓝 c))⟩ :=
  uniformly_extend_exists ue'.to_uniform_inducing de'.dense hf _ in
begin
  rw [nhds_subtype_eq_comap] at hc,
  simp [comap_comap_comp] at hc,
  change (tendsto (f ∘ @subtype.val α p) (comap (e ∘ @subtype.val α p) (𝓝 b)) (𝓝 c)) at hc,
  rw [←comap_comap_comp, tendsto_comap'_iff] at hc,
  exact ⟨c, hc⟩,
  exact ⟨_, hb, assume x,
    begin
      change e x ∈ (closure (e '' s)) → x ∈ range subtype.val,
      rw [←closure_induced, closure_eq_cluster_pts, mem_set_of_eq, cluster_pt,
          (≠), nhds_induced, ← de.to_dense_inducing.nhds_eq_comap],
      change x ∈ {y | cluster_pt y (𝓟 s)} → x ∈ range subtype.val,
      rw [←closure_eq_cluster_pts, closure_eq_of_is_closed hs],
      exact assume hxs, ⟨⟨x, hp x hxs⟩, rfl⟩,
      exact de.inj
    end⟩
end

variables [separated_space γ]

lemma uniformly_extend_of_ind (b : β) : ψ (e b) = f b :=
dense_inducing.extend_e_eq _ b (continuous_iff_continuous_at.1 h_f.continuous b)

include h_f

lemma uniformly_extend_spec [complete_space γ] (a : α) :
  tendsto f (comap e (𝓝 a)) (𝓝 (ψ a)) :=
let de := (h_e.dense_inducing h_dense) in
begin
  by_cases ha : a ∈ range e,
  { rcases ha with ⟨b, rfl⟩,
    rw [uniformly_extend_of_ind _ _ h_f, ← de.nhds_eq_comap],
    exact h_f.continuous.tendsto _ },
  { simp only [dense_inducing.extend, dif_neg ha],
    exact lim_spec (uniformly_extend_exists h_e h_dense h_f _) }
end


lemma uniform_continuous_uniformly_extend [cγ : complete_space γ] : uniform_continuous ψ :=
assume d hd,
let ⟨s, hs, hs_comp⟩ := (mem_lift'_sets $
  monotone_comp_rel monotone_id $ monotone_comp_rel monotone_id monotone_id).mp (comp_le_uniformity3 hd) in
have h_pnt : ∀{a m}, m ∈ 𝓝 a → ∃c, c ∈ f '' preimage e m ∧ (c, ψ a) ∈ s ∧ (ψ a, c) ∈ s,
  from assume a m hm,
  have nb : map f (comap e (𝓝 a)) ≠ ⊥,
    from map_ne_bot (h_e.dense_inducing h_dense).comap_nhds_ne_bot,
  have (f '' preimage e m) ∩ ({c | (c, ψ a) ∈ s } ∩ {c | (ψ a, c) ∈ s }) ∈ map f (comap e (𝓝 a)),
    from inter_mem_sets (image_mem_map $ preimage_mem_comap $ hm)
      (uniformly_extend_spec h_e h_dense h_f _ (inter_mem_sets (mem_nhds_right _ hs) (mem_nhds_left _ hs))),
  nonempty_of_mem_sets nb this,
have preimage (λp:β×β, (f p.1, f p.2)) s ∈ 𝓤 β,
  from h_f hs,
have preimage (λp:β×β, (f p.1, f p.2)) s ∈ comap (λx:β×β, (e x.1, e x.2)) (𝓤 α),
  by rwa [h_e.comap_uniformity.symm] at this,
let ⟨t, ht, ts⟩ := this in
show preimage (λp:(α×α), (ψ p.1, ψ p.2)) d ∈ 𝓤 α,
  from (𝓤 α).sets_of_superset (interior_mem_uniformity ht) $
  assume ⟨x₁, x₂⟩ hx_t,
  have 𝓝 (x₁, x₂) ≤ 𝓟 (interior t),
    from is_open_iff_nhds.mp is_open_interior (x₁, x₂) hx_t,
  have interior t ∈ filter.prod (𝓝 x₁) (𝓝 x₂),
    by rwa [nhds_prod_eq, le_principal_iff] at this,
  let ⟨m₁, hm₁, m₂, hm₂, (hm : set.prod m₁ m₂ ⊆ interior t)⟩ := mem_prod_iff.mp this in
  let ⟨a, ha₁, _, ha₂⟩ := h_pnt hm₁ in
  let ⟨b, hb₁, hb₂, _⟩ := h_pnt hm₂ in
  have set.prod (preimage e m₁) (preimage e m₂) ⊆ preimage (λp:(β×β), (f p.1, f p.2)) s,
    from calc _ ⊆ preimage (λp:(β×β), (e p.1, e p.2)) (interior t) : preimage_mono hm
    ... ⊆ preimage (λp:(β×β), (e p.1, e p.2)) t : preimage_mono interior_subset
    ... ⊆ preimage (λp:(β×β), (f p.1, f p.2)) s : ts,
  have set.prod (f '' preimage e m₁) (f '' preimage e m₂) ⊆ s,
    from calc set.prod (f '' preimage e m₁) (f '' preimage e m₂) =
      (λp:(β×β), (f p.1, f p.2)) '' (set.prod (preimage e m₁) (preimage e m₂)) : prod_image_image_eq
    ... ⊆ (λp:(β×β), (f p.1, f p.2)) '' preimage (λp:(β×β), (f p.1, f p.2)) s : monotone_image this
    ... ⊆ s : image_subset_iff.mpr $ subset.refl _,
  have (a, b) ∈ s, from @this (a, b) ⟨ha₁, hb₁⟩,
  hs_comp $ show (ψ x₁, ψ x₂) ∈ comp_rel s (comp_rel s s),
    from ⟨a, ha₂, ⟨b, this, hb₂⟩⟩
end uniform_extension
