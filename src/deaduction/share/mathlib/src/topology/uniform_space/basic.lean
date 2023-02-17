/-
Copyright (c) 2017 Johannes Hölzl. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Johannes Hölzl, Mario Carneiro, Patrick Massot
-/
import order.filter.lift
import topology.separation
/-!
# Uniform spaces

Uniform spaces are a generalization of metric spaces and topological groups. Many concepts directly
generalize to uniform spaces, e.g.

* uniform continuity (in this file)
* completeness (in `cauchy.lean`)
* extension of uniform continuous functions to complete spaces (in `uniform_embedding.lean`)
* totally bounded sets (in `cauchy.lean`)
* totally bounded complete sets are compact (in `cauchy.lean`)

A uniform structure on a type `X` is a filter `𝓤 X` on `X × X` satisfying some conditions
which makes it reasonable to say that `∀ᶠ (p : X × X) in 𝓤 X, ...` means
"for all p.1 and p.2 in X close enough, ...". Elements of this filter are called entourages
of `X`. The two main examples are:

* If `X` is a metric space, `V ∈ 𝓤 X ↔ ∃ ε > 0, { p | dist p.1 p.2 < ε } ⊆ V`
* If `G` is an additive topological group, `V ∈ 𝓤 G ↔ ∃ U ∈ 𝓝 (0 : G), {p | p.2 - p.1 ∈ U} ⊆ V`

Those examples are generalizations in two different directions of the elementary example where
`X = ℝ` and `V ∈ 𝓤 ℝ ↔ ∃ ε > 0, { p | |p.2 - p.1| < ε } ⊆ V` which features both the topological
group structure on `ℝ` and its metric space structure.

Each uniform structure on `X` induces a topology on `X` characterized by

> `nhds_eq_comap_uniformity : ∀ {x : X}, 𝓝 x = comap (prod.mk x) (𝓤 X)`

where `prod.mk x : X → X × X := (λ y, (x, y))` is the partial evaluation of the product
constructor.

The dictionary with metric spaces includes:
* an upper bound for `dist x y` translates into `(x, y) ∈ V` for some `V ∈ 𝓤 X`
* a ball `ball x r` roughly corresponds to `uniform_space.ball x V := {y | (x, y) ∈ V}`
  for some `V ∈ 𝓤 X`, but the later is more general (it includes in
  particular both open and closed balls for suitable `V`).
  In particular we have:
  `is_open_iff_ball_subset {s : set X} : is_open s ↔ ∀ x ∈ s, ∃ V ∈ 𝓤 X, ball x V ⊆ s`

The triangle inequality is abstracted to a statement involving the composition of relations in `X`.
First note that the triangle inequality in a metric space is equivalent to
`∀ (x y z : X) (r r' : ℝ), dist x y ≤ r → dist y z ≤ r' → dist x z ≤ r + r'`.
Then, for any `V` and `W` with type `set (X × X)`, the composition `V ○ W : set (X × X)` is
defined as `{ p : X × X | ∃ z, (p.1, z) ∈ V ∧ (z, p.2) ∈ W }`.
In the metric space case, if `V = { p | dist p.1 p.2 ≤ r }` and `W = { p | dist p.1 p.2 ≤ r' }`
then the triangle inequality, as reformulated above, says `V ○ W` is contained in
`{p | dist p.1 p.2 ≤ r + r'}` which is the entourage associated to the radius `r + r'`.
In general we have `mem_ball_comp (h : y ∈ ball x V) (h' : z ∈ ball y W) : z ∈ ball x (V ○ W)`.
Note that this discussion does not depend on any axiom imposed on the uniformity filter,
it is simply captured by the definition of composition.

The uniform space axioms ask the filter `𝓤 X` to satisfy the following:
* every `V ∈ 𝓤 X` contains the diagonal `id_rel = { p | p.1 = p.2 }`. This abstracts the fact
  that `dist x x ≤ r` for every non-negative radius `r` in the metric space case and also that
  `x - x` belongs to every neighborhood of zero in the topological group case.
* `V ∈ 𝓤 X → prod.swap '' V ∈ 𝓤 X`. This is tightly related the fact that `dist x y = dist y x`
  in a metric space, and to continuity of negation in the topological group case.
* `∀ V ∈ 𝓤 X, ∃ W ∈ 𝓤 X, W ○ W ⊆ V`. In the metric space case, it corresponds
  to cutting the radius of a ball in half and applying the triangle inequality.
  In the topological group case, it comes from continuity of addition at `(0, 0)`.

These three axioms are stated more abstractly in the definition below, in terms of
operations on filters, without directly manipulating entourages.

## Main definitions

* `uniform_space X` is a uniform space structure on a type `X`
* `uniform_continuous f` is a predicate saying a function `f : α → β` between uniform spaces
  is uniformly continuous : `∀ r ∈ 𝓤 β, ∀ᶠ (x : α × α) in 𝓤 α, (f x.1, f x.2) ∈ r`

In this file we also define a complete lattice structure on the type `uniform_space X`
of uniform structures on `X`, as well as the pullback (`uniform_space.comap`) of uniform structures
coming from the pullback of filters.
Like distance functions, uniform structures cannot be pushed forward in general.

## Notations

Localized in `uniformity`, we have the notation `𝓤 X` for the uniformity on a uniform space `X`,
and `○` for composition of relations, seen as terms with type `set (X × X)`.

## Implementation notes

There is already a theory of relations in `data/rel.lean` where the main definition is
`def rel (α β : Type*) := α → β → Prop`.
The relations used in the current file involve only one type, but this is not the reason why
we don't reuse `data/rel.lean`. We use `set (α × α)`
instead of `rel α α` because we really need sets to use the filter library, and elements
of filters on `α × α` have type `set (α × α)`.

The structure `uniform_space X` bundles a uniform structure on `X`, a topology on `X` and
an assumption saying those are compatible. This may not seem mathematically reasonable at first,
but is in fact an instance of the forgetful inheritance pattern. See Note [forgetful inheritance]
below.

## References

The formalization uses the books:

* [N. Bourbaki, *General Topology*][bourbaki1966]
* [I. M. James, *Topologies and Uniformities*][james1999]

But it makes a more systematic use of the filter library.
-/

open set filter classical
open_locale classical topological_space filter

set_option eqn_compiler.zeta true

universes u

/-!
### Relations, seen as `set (α × α)`
-/
variables {α : Type*} {β : Type*} {γ : Type*} {δ : Type*} {ι : Sort*}

/-- The identity relation, or the graph of the identity function -/
def id_rel {α : Type*} := {p : α × α | p.1 = p.2}

@[simp] theorem mem_id_rel {a b : α} : (a, b) ∈ @id_rel α ↔ a = b := iff.rfl

@[simp] theorem id_rel_subset {s : set (α × α)} : id_rel ⊆ s ↔ ∀ a, (a, a) ∈ s :=
by simp [subset_def]; exact forall_congr (λ a, by simp)

/-- The composition of relations -/
def comp_rel {α : Type u} (r₁ r₂ : set (α×α)) := {p : α × α | ∃z:α, (p.1, z) ∈ r₁ ∧ (z, p.2) ∈ r₂}

localized "infix ` ○ `:55 := comp_rel" in uniformity

@[simp] theorem mem_comp_rel {r₁ r₂ : set (α×α)}
  {x y : α} : (x, y) ∈ r₁ ○ r₂ ↔ ∃ z, (x, z) ∈ r₁ ∧ (z, y) ∈ r₂ := iff.rfl

@[simp] theorem swap_id_rel : prod.swap '' id_rel = @id_rel α :=
set.ext $ assume ⟨a, b⟩, by simp [image_swap_eq_preimage_swap]; exact eq_comm

theorem monotone_comp_rel [preorder β] {f g : β → set (α×α)}
  (hf : monotone f) (hg : monotone g) : monotone (λx, (f x) ○ (g x)) :=
assume a b h p ⟨z, h₁, h₂⟩, ⟨z, hf h h₁, hg h h₂⟩

@[mono]
lemma comp_rel_mono {f g h k: set (α×α)} (h₁ : f ⊆ h) (h₂ : g ⊆ k) : f ○ g ⊆ h ○ k :=
λ ⟨x, y⟩ ⟨z, h, h'⟩, ⟨z, h₁ h, h₂ h'⟩

lemma prod_mk_mem_comp_rel {a b c : α} {s t : set (α×α)} (h₁ : (a, c) ∈ s) (h₂ : (c, b) ∈ t) :
  (a, b) ∈ s ○ t :=
⟨c, h₁, h₂⟩

@[simp] lemma id_comp_rel {r : set (α×α)} : id_rel ○ r = r :=
set.ext $ assume ⟨a, b⟩, by simp

lemma comp_rel_assoc {r s t : set (α×α)} :
  (r ○ s) ○ t = r ○ (s ○ t) :=
by ext p; cases p; simp only [mem_comp_rel]; tauto

lemma subset_comp_self {α : Type*} {s : set (α × α)} (h : id_rel ⊆ s) : s ⊆ s ○ s :=
λ ⟨x, y⟩ xy_in, ⟨x, h (by rw mem_id_rel), xy_in⟩

/-- The relation is invariant under swapping factors. -/
def symmetric_rel (V : set (α × α)) : Prop := prod.swap ⁻¹' V = V

/-- The maximal symmetric relation contained in a given relation. -/
def symmetrize_rel (V : set (α × α)) : set (α × α) := V ∩ prod.swap ⁻¹' V

lemma symmetric_symmetrize_rel (V : set (α × α)) : symmetric_rel (symmetrize_rel V) :=
by simp [symmetric_rel, symmetrize_rel, preimage_inter, inter_comm, ← preimage_comp]

lemma symmetrize_rel_subset_self (V : set (α × α)) : symmetrize_rel V ⊆ V :=
sep_subset _ _

@[mono]
lemma symmetrize_mono {V W: set (α × α)} (h : V ⊆ W) : symmetrize_rel V ⊆ symmetrize_rel W :=
inter_subset_inter h $ preimage_mono h

lemma symmetric_rel_inter {U V : set (α × α)} (hU : symmetric_rel U) (hV : symmetric_rel V) :
symmetric_rel (U ∩ V) :=
begin
  unfold symmetric_rel at *,
  rw [preimage_inter, hU, hV],
end

/-- This core description of a uniform space is outside of the type class hierarchy. It is useful
  for constructions of uniform spaces, when the topology is derived from the uniform space. -/
structure uniform_space.core (α : Type u) :=
(uniformity : filter (α × α))
(refl       : 𝓟 id_rel ≤ uniformity)
(symm       : tendsto prod.swap uniformity uniformity)
(comp       : uniformity.lift' (λs, s ○ s) ≤ uniformity)

/-- An alternative constructor for `uniform_space.core`. This version unfolds various
`filter`-related definitions. -/
def uniform_space.core.mk' {α : Type u} (U : filter (α × α))
  (refl : ∀ (r ∈ U) x, (x, x) ∈ r)
  (symm : ∀ r ∈ U, prod.swap ⁻¹' r ∈ U)
  (comp : ∀ r ∈ U, ∃ t ∈ U, t ○ t ⊆ r) : uniform_space.core α :=
⟨U, λ r ru, id_rel_subset.2 (refl _ ru), symm,
  begin
    intros r ru,
    rw [mem_lift'_sets],
    exact comp _ ru,
    apply monotone_comp_rel; exact monotone_id,
  end⟩

/-- A uniform space generates a topological space -/
def uniform_space.core.to_topological_space {α : Type u} (u : uniform_space.core α) :
  topological_space α :=
{ is_open        := λs, ∀x∈s, { p : α × α | p.1 = x → p.2 ∈ s } ∈ u.uniformity,
  is_open_univ   := by simp; intro; exact univ_mem_sets,
  is_open_inter  :=
    assume s t hs ht x ⟨xs, xt⟩, by filter_upwards [hs x xs, ht x xt]; simp {contextual := tt},
  is_open_sUnion :=
    assume s hs x ⟨t, ts, xt⟩, by filter_upwards [hs t ts x xt] assume p ph h, ⟨t, ts, ph h⟩ }

lemma uniform_space.core_eq : ∀{u₁ u₂ : uniform_space.core α}, u₁.uniformity = u₂.uniformity → u₁ = u₂
| ⟨u₁, _, _, _⟩  ⟨u₂, _, _, _⟩ h := have u₁ = u₂, from h, by simp [*]

section prio

/-- Suppose that one can put two mathematical structures on a type, a rich one `R` and a poor one
`P`, and that one can deduce the poor structure from the rich structure through a map `F` (called a
forgetful functor) (think `R = metric_space` and `P = topological_space`). A possible
implementation would be to have a type class `rich` containing a field `R`, a type class `poor`
containing a field `P`, and an instance from `rich` to `poor`. However, this creates diamond
problems, and a better approach is to let `rich` extend `poor` and have a field saying that
`F R = P`.

To illustrate this, consider the pair `metric_space` / `topological_space`. Consider the topology
on a product of two metric spaces. With the first approach, it could be obtained by going first from
each metric space to its topology, and then taking the product topology. But it could also be
obtained by considering the product metric space (with its sup distance) and then the topology
coming from this distance. These would be the same topology, but not definitionally, which means
that from the point of view of Lean's kernel, there would be two different `topological_space`
instances on the product. This is not compatible with the way instances are designed and used:
there should be at most one instance of a kind on each type. This approach has created an instance
diamond that does not commute definitionally.

The second approach solves this issue. Now, a metric space contains both a distance, a topology, and
a proof that the topology coincides with the one coming from the distance. When one defines the
product of two metric spaces, one uses the sup distance and the product topology, and one has to
give the proof that the sup distance induces the product topology. Following both sides of the
instance diamond then gives rise (definitionally) to the product topology on the product space.

Another approach would be to have the rich type class take the poor type class as an instance
parameter. It would solve the diamond problem, but it would lead to a blow up of the number
of type classes one would need to declare to work with complicated classes, say a real inner
product space, and would create exponential complexity when working with products of
such complicated spaces, that are avoided by bundling things carefully as above.

Note that this description of this specific case of the product of metric spaces is oversimplified
compared to mathlib, as there is an intermediate typeclass between `metric_space` and
`topological_space` called `uniform_space`. The above scheme is used at both levels, embedding a
topology in the uniform space structure, and a uniform structure in the metric space structure.

Note also that, when `P` is a proposition, there is no such issue as any two proofs of `P` are
definitionally equivalent in Lean.

To avoid boilerplate, there are some designs that can automatically fill the poor fields when
creating a rich structure if one doesn't want to do something special about them. For instance,
in the definition of metric spaces, default tactics fill the uniform space fields if they are
not given explicitly. One can also have a helper function creating the rich structure from a
structure with less fields, where the helper function fills the remaining fields. See for instance
`uniform_space.of_core` or `real_inner_product.of_core`.

For more details on this question, called the forgetful inheritance pattern, see [Competing
inheritance paths in dependent type theory: a case study in functional
analysis](https://hal.inria.fr/hal-02463336).
-/
library_note "forgetful inheritance"

set_option default_priority 100 -- see Note [default priority]
/-- A uniform space is a generalization of the "uniform" topological aspects of a
  metric space. It consists of a filter on `α × α` called the "uniformity", which
  satisfies properties analogous to the reflexivity, symmetry, and triangle properties
  of a metric.

  A metric space has a natural uniformity, and a uniform space has a natural topology.
  A topological group also has a natural uniformity, even when it is not metrizable. -/
class uniform_space (α : Type u) extends topological_space α, uniform_space.core α :=
(is_open_uniformity : ∀s, is_open s ↔ (∀x∈s, { p : α × α | p.1 = x → p.2 ∈ s } ∈ uniformity))
end prio

/-- Alternative constructor for `uniform_space α` when a topology is already given. -/
@[pattern] def uniform_space.mk' {α} (t : topological_space α)
  (c : uniform_space.core α)
  (is_open_uniformity : ∀s:set α, t.is_open s ↔
    (∀x∈s, { p : α × α | p.1 = x → p.2 ∈ s } ∈ c.uniformity)) :
  uniform_space α := ⟨c, is_open_uniformity⟩

/-- Construct a `uniform_space` from a `uniform_space.core`. -/
def uniform_space.of_core {α : Type u} (u : uniform_space.core α) : uniform_space α :=
{ to_core := u,
  to_topological_space := u.to_topological_space,
  is_open_uniformity := assume a, iff.rfl }

/-- Construct a `uniform_space` from a `u : uniform_space.core` and a `topological_space` structure
that is equal to `u.to_topological_space`. -/
def uniform_space.of_core_eq {α : Type u} (u : uniform_space.core α) (t : topological_space α)
  (h : t = u.to_topological_space) : uniform_space α :=
{ to_core := u,
  to_topological_space := t,
  is_open_uniformity := assume a, h.symm ▸ iff.rfl }

lemma uniform_space.to_core_to_topological_space (u : uniform_space α) :
  u.to_core.to_topological_space = u.to_topological_space :=
topological_space_eq $ funext $ assume s,
  by rw [uniform_space.core.to_topological_space, uniform_space.is_open_uniformity]

@[ext]
lemma uniform_space_eq : ∀{u₁ u₂ : uniform_space α}, u₁.uniformity = u₂.uniformity → u₁ = u₂
| (uniform_space.mk' t₁ u₁ o₁)  (uniform_space.mk' t₂ u₂ o₂) h :=
  have u₁ = u₂, from uniform_space.core_eq h,
  have t₁ = t₂, from topological_space_eq $ funext $ assume s, by rw [o₁, o₂]; simp [this],
  by simp [*]

lemma uniform_space.of_core_eq_to_core
  (u : uniform_space α) (t : topological_space α) (h : t = u.to_core.to_topological_space) :
  uniform_space.of_core_eq u.to_core t h = u :=
uniform_space_eq rfl

section uniform_space
variables [uniform_space α]

/-- The uniformity is a filter on α × α (inferred from an ambient uniform space
  structure on α). -/
def uniformity (α : Type u) [uniform_space α] : filter (α × α) :=
  (@uniform_space.to_core α _).uniformity

localized "notation `𝓤` := uniformity" in uniformity

lemma is_open_uniformity {s : set α} :
  is_open s ↔ (∀x∈s, { p : α × α | p.1 = x → p.2 ∈ s } ∈ 𝓤 α) :=
uniform_space.is_open_uniformity s

lemma refl_le_uniformity : 𝓟 id_rel ≤ 𝓤 α :=
(@uniform_space.to_core α _).refl

lemma refl_mem_uniformity {x : α} {s : set (α × α)} (h : s ∈ 𝓤 α) :
  (x, x) ∈ s :=
refl_le_uniformity h rfl

lemma symm_le_uniformity : map (@prod.swap α α) (𝓤 _) ≤ (𝓤 _) :=
(@uniform_space.to_core α _).symm

lemma comp_le_uniformity : (𝓤 α).lift' (λs:set (α×α), s ○ s) ≤ 𝓤 α :=
(@uniform_space.to_core α _).comp

lemma tendsto_swap_uniformity : tendsto (@prod.swap α α) (𝓤 α) (𝓤 α) :=
symm_le_uniformity

lemma comp_mem_uniformity_sets {s : set (α × α)} (hs : s ∈ 𝓤 α) :
  ∃ t ∈ 𝓤 α, t ○ t ⊆ s :=
have s ∈ (𝓤 α).lift' (λt:set (α×α), t ○ t),
  from comp_le_uniformity hs,
(mem_lift'_sets $ monotone_comp_rel monotone_id monotone_id).mp this

/-- Relation `λ f g, tendsto (λ x, (f x, g x)) l (𝓤 α)` is transitive. -/
lemma filter.tendsto.uniformity_trans {l : filter β} {f₁ f₂ f₃ : β → α}
  (h₁₂ : tendsto (λ x, (f₁ x, f₂ x)) l (𝓤 α)) (h₂₃ : tendsto (λ x, (f₂ x, f₃ x)) l (𝓤 α)) :
  tendsto (λ x, (f₁ x, f₃ x)) l (𝓤 α) :=
begin
  refine le_trans (le_lift' $ λ s hs, mem_map.2 _) comp_le_uniformity,
  filter_upwards [h₁₂ hs, h₂₃ hs],
  exact λ x hx₁₂ hx₂₃, ⟨_, hx₁₂, hx₂₃⟩
end

/-- Relation `λ f g, tendsto (λ x, (f x, g x)) l (𝓤 α)` is symmetric -/
lemma filter.tendsto.uniformity_symm {l : filter β} {f : β → α × α}
  (h : tendsto f l (𝓤 α)) :
  tendsto (λ x, ((f x).2, (f x).1)) l (𝓤 α) :=
tendsto_swap_uniformity.comp h

/-- Relation `λ f g, tendsto (λ x, (f x, g x)) l (𝓤 α)` is reflexive. -/
lemma tendsto_diag_uniformity (f : β → α) (l : filter β) :
  tendsto (λ x, (f x, f x)) l (𝓤 α) :=
assume s hs, mem_map.2 $ univ_mem_sets' $ λ x, refl_mem_uniformity hs

lemma tendsto_const_uniformity {a : α} {f : filter β} : tendsto (λ _, (a, a)) f (𝓤 α) :=
tendsto_diag_uniformity (λ _, a) f

lemma symm_of_uniformity {s : set (α × α)} (hs : s ∈ 𝓤 α) :
  ∃ t ∈ 𝓤 α, (∀a b, (a, b) ∈ t → (b, a) ∈ t) ∧ t ⊆ s :=
have preimage prod.swap s ∈ 𝓤 α, from symm_le_uniformity hs,
⟨s ∩ preimage prod.swap s, inter_mem_sets hs this, assume a b ⟨h₁, h₂⟩, ⟨h₂, h₁⟩, inter_subset_left _ _⟩

lemma comp_symm_of_uniformity {s : set (α × α)} (hs : s ∈ 𝓤 α) :
  ∃ t ∈ 𝓤 α, (∀{a b}, (a, b) ∈ t → (b, a) ∈ t) ∧ t ○ t ⊆ s :=
let ⟨t, ht₁, ht₂⟩ := comp_mem_uniformity_sets hs in
let ⟨t', ht', ht'₁, ht'₂⟩ := symm_of_uniformity ht₁ in
⟨t', ht', ht'₁, subset.trans (monotone_comp_rel monotone_id monotone_id ht'₂) ht₂⟩

lemma uniformity_le_symm : 𝓤 α ≤ (@prod.swap α α) <$> 𝓤 α :=
by rw [map_swap_eq_comap_swap];
from map_le_iff_le_comap.1 tendsto_swap_uniformity

lemma uniformity_eq_symm : 𝓤 α = (@prod.swap α α) <$> 𝓤 α :=
le_antisymm uniformity_le_symm symm_le_uniformity

lemma symmetrize_mem_uniformity {V : set (α × α)} (h : V ∈ 𝓤 α) : symmetrize_rel V ∈ 𝓤 α :=
begin
  apply (𝓤 α).inter_sets h,
  rw [← image_swap_eq_preimage_swap, uniformity_eq_symm],
  exact image_mem_map h,
end

theorem uniformity_lift_le_swap {g : set (α×α) → filter β} {f : filter β} (hg : monotone g)
  (h : (𝓤 α).lift (λs, g (preimage prod.swap s)) ≤ f) : (𝓤 α).lift g ≤ f :=
calc (𝓤 α).lift g ≤ (filter.map (@prod.swap α α) $ 𝓤 α).lift g :
    lift_mono uniformity_le_symm (le_refl _)
  ... ≤ _ :
    by rw [map_lift_eq2 hg, image_swap_eq_preimage_swap]; exact h

lemma uniformity_lift_le_comp {f : set (α×α) → filter β} (h : monotone f) :
  (𝓤 α).lift (λs, f (s ○ s)) ≤ (𝓤 α).lift f :=
calc (𝓤 α).lift (λs, f (s ○ s)) =
    ((𝓤 α).lift' (λs:set (α×α), s ○ s)).lift f :
  begin
    rw [lift_lift'_assoc],
    exact monotone_comp_rel monotone_id monotone_id,
    exact h
  end
  ... ≤ (𝓤 α).lift f : lift_mono comp_le_uniformity (le_refl _)

lemma comp_le_uniformity3 :
  (𝓤 α).lift' (λs:set (α×α), s ○ (s ○ s)) ≤ (𝓤 α) :=
calc (𝓤 α).lift' (λd, d ○ (d ○ d)) =
  (𝓤 α).lift (λs, (𝓤 α).lift' (λt:set(α×α), s ○ (t ○ t))) :
  begin
    rw [lift_lift'_same_eq_lift'],
    exact (assume x, monotone_comp_rel monotone_const $ monotone_comp_rel monotone_id monotone_id),
    exact (assume x, monotone_comp_rel monotone_id monotone_const),
  end
  ... ≤ (𝓤 α).lift (λs, (𝓤 α).lift' (λt:set(α×α), s ○ t)) :
    lift_mono' $ assume s hs, @uniformity_lift_le_comp α _ _ (𝓟 ∘ (○) s) $
      monotone_principal.comp (monotone_comp_rel monotone_const monotone_id)
  ... = (𝓤 α).lift' (λs:set(α×α), s ○ s) :
    lift_lift'_same_eq_lift'
      (assume s, monotone_comp_rel monotone_const monotone_id)
      (assume s, monotone_comp_rel monotone_id monotone_const)
  ... ≤ (𝓤 α) : comp_le_uniformity

lemma comp_symm_mem_uniformity_sets {s : set (α × α)} (hs : s ∈ 𝓤 α) :
  ∃ t ∈ 𝓤 α, symmetric_rel t ∧ t ○ t ⊆ s :=
begin
  obtain ⟨w, w_in, w_sub⟩ : ∃ w ∈ 𝓤 α, w ○ w ⊆ s := comp_mem_uniformity_sets hs,
  use [symmetrize_rel w, symmetrize_mem_uniformity w_in, symmetric_symmetrize_rel w],
  have : symmetrize_rel w ⊆ w := symmetrize_rel_subset_self w,
  calc symmetrize_rel w ○ symmetrize_rel w ⊆ w ○ w : by mono
                                       ... ⊆ s     : w_sub,
end

lemma subset_comp_self_of_mem_uniformity {s : set (α × α)} (h : s ∈ 𝓤 α) : s ⊆ s ○ s :=
subset_comp_self (refl_le_uniformity h)

lemma comp_comp_symm_mem_uniformity_sets {s : set (α × α)} (hs : s ∈ 𝓤 α) :
  ∃ t ∈ 𝓤 α, symmetric_rel t ∧ t ○ t ○ t ⊆ s :=
begin
  rcases comp_symm_mem_uniformity_sets hs with ⟨w, w_in, w_symm, w_sub⟩,
  rcases comp_symm_mem_uniformity_sets w_in with ⟨t, t_in, t_symm, t_sub⟩,
  use [t, t_in, t_symm],
  have : t ⊆ t ○ t :=  subset_comp_self_of_mem_uniformity t_in,
  calc
  t ○ t ○ t ⊆ w ○ t       : by mono
        ... ⊆ w ○ (t ○ t) : by mono
        ... ⊆ w ○ w       : by mono
        ... ⊆ s           : w_sub,
end

/-!
### Balls in uniform spaces
-/

/-- The ball around `(x : β)` with respect to `(V : set (β × β))`. Intended to be
used for `V ∈ 𝓤 β`, but this is not needed for the definition. Recovers the
notions of metric space ball when `V = {p | dist p.1 p.2 < r }`.  -/
def uniform_space.ball (x : β) (V : set (β × β)) : set β := (prod.mk x) ⁻¹' V

open uniform_space (ball)

/-- The triangle inequality for `uniform_space.ball` -/
lemma mem_ball_comp {V W : set (β × β)} {x y z} (h : y ∈ ball x V) (h' : z ∈ ball y W) :
  z ∈ ball x (V ○ W) :=
prod_mk_mem_comp_rel h h'

lemma ball_subset_of_comp_subset {V W : set (β × β)} {x y} (h : x ∈ ball y W) (h' : W ○ W ⊆ V) :
  ball x W ⊆ ball y V :=
λ z z_in, h' (mem_ball_comp h z_in)

lemma ball_mono {V W : set (β × β)} (h : V ⊆ W) (x : β) : ball x V ⊆ ball x W :=
by tauto

lemma mem_ball_symmetry {V : set (β × β)} (hV : symmetric_rel V) {x y} :
  x ∈ ball y V ↔ y ∈ ball x V :=
show (x, y) ∈ prod.swap ⁻¹' V ↔ (x, y) ∈ V, by { unfold symmetric_rel at hV, rw hV }

lemma ball_eq_of_symmetry {V : set (β × β)} (hV : symmetric_rel V) {x} :
  ball x V = {y | (y, x) ∈ V} :=
by { ext y, rw mem_ball_symmetry hV, exact iff.rfl }

lemma mem_comp_of_mem_ball {V W : set (β × β)} {x y z : β} (hV : symmetric_rel V)
  (hx : x ∈ ball z V) (hy : y ∈ ball z W) : (x, y) ∈ V ○ W :=
begin
  rw mem_ball_symmetry hV at hx,
  exact ⟨z, hx, hy⟩
end

lemma mem_comp_comp {V W M : set (β × β)} (hW' : symmetric_rel W) {p : β × β} :
  p ∈ V ○ M ○ W ↔ ((ball p.1 V).prod (ball p.2 W) ∩ M).nonempty :=
begin
  cases p with x y,
  split,
  { rintros ⟨z, ⟨w, hpw, hwz⟩, hzy⟩,
    exact ⟨(w, z), ⟨hpw, by rwa mem_ball_symmetry hW'⟩, hwz⟩, },
  { rintro ⟨⟨w, z⟩, ⟨w_in, z_in⟩, hwz⟩,
    rwa mem_ball_symmetry hW' at z_in,
    use [z, w] ; tauto },
end

/-!
### Neighborhoods in uniform spaces
-/

lemma mem_nhds_uniformity_iff_right {x : α} {s : set α} :
  s ∈ 𝓝 x ↔ {p : α × α | p.1 = x → p.2 ∈ s} ∈ 𝓤 α :=
⟨ begin
    simp only [mem_nhds_sets_iff, is_open_uniformity, and_imp, exists_imp_distrib],
    exact assume t ts ht xt, by filter_upwards [ht x xt] assume ⟨x', y⟩ h eq, ts $ h eq
  end,

  assume hs,
  mem_nhds_sets_iff.mpr ⟨{x | {p : α × α | p.1 = x → p.2 ∈ s} ∈ 𝓤 α},
    assume x' hx', refl_mem_uniformity hx' rfl,
    is_open_uniformity.mpr $ assume x' hx',
      let ⟨t, ht, tr⟩ := comp_mem_uniformity_sets hx' in
      by filter_upwards [ht] assume ⟨a, b⟩ hp' (hax' : a = x'),
      by filter_upwards [ht] assume ⟨a, b'⟩ hp'' (hab : a = b),
      have hp : (x', b) ∈ t, from hax' ▸ hp',
      have (b, b') ∈ t, from hab ▸ hp'',
      have (x', b') ∈ t ○ t, from ⟨b, hp, this⟩,
      show b' ∈ s,
        from tr this rfl,
    hs⟩⟩

lemma mem_nhds_uniformity_iff_left {x : α} {s : set α} :
  s ∈ 𝓝 x ↔ {p : α × α | p.2 = x → p.1 ∈ s} ∈ 𝓤 α :=
by { rw [uniformity_eq_symm, mem_nhds_uniformity_iff_right], refl }

lemma nhds_eq_comap_uniformity {x : α} : 𝓝 x = (𝓤 α).comap (prod.mk x) :=
by ext s; rw [mem_nhds_uniformity_iff_right, mem_comap_sets]; from iff.intro
  (assume hs, ⟨_, hs, assume x hx, hx rfl⟩)
  (assume ⟨t, h, ht⟩, (𝓤 α).sets_of_superset h $
    assume ⟨p₁, p₂⟩ hp (h : p₁ = x), ht $ by simp [h.symm, hp])

lemma is_open_iff_ball_subset {s : set α} : is_open s ↔ ∀ x ∈ s, ∃ V ∈ 𝓤 α, ball x V ⊆ s :=
begin
  simp_rw [is_open_iff_mem_nhds, nhds_eq_comap_uniformity],
  exact iff.rfl,
end

lemma nhds_basis_uniformity' {p : β → Prop} {s : β → set (α × α)} (h : (𝓤 α).has_basis p s) {x : α} :
  (𝓝 x).has_basis p (λ i, {y | (x, y) ∈ s i}) :=
by { rw [nhds_eq_comap_uniformity], exact h.comap (prod.mk x) }

lemma nhds_basis_uniformity {p : β → Prop} {s : β → set (α × α)} (h : (𝓤 α).has_basis p s) {x : α} :
  (𝓝 x).has_basis p (λ i, {y | (y, x) ∈ s i}) :=
begin
  replace h := h.comap prod.swap,
  rw [← map_swap_eq_comap_swap, ← uniformity_eq_symm] at h,
  exact nhds_basis_uniformity' h
end

lemma uniform_space.mem_nhds_iff {x : α} {s : set α} : s ∈ 𝓝 x ↔ ∃ V ∈ 𝓤 α, ball x V ⊆ s :=
begin
  rw [nhds_eq_comap_uniformity, mem_comap_sets],
  exact iff.rfl,
end

lemma uniform_space.ball_mem_nhds (x : α) ⦃V : set (α × α)⦄ (V_in : V ∈ 𝓤 α) : ball x V ∈ 𝓝 x :=
begin
  rw uniform_space.mem_nhds_iff,
  exact ⟨V, V_in, subset.refl _⟩
end

lemma uniform_space.mem_nhds_iff_symm {x : α} {s : set α} :
  s ∈ 𝓝 x ↔ ∃ V ∈ 𝓤 α, symmetric_rel V ∧ ball x V ⊆ s :=
begin
  rw uniform_space.mem_nhds_iff,
  split,
  { rintros ⟨V, V_in, V_sub⟩,
    use [symmetrize_rel V, symmetrize_mem_uniformity V_in, symmetric_symmetrize_rel V],
    exact subset.trans (ball_mono (symmetrize_rel_subset_self V) x) V_sub },
  { rintros ⟨V, V_in, V_symm, V_sub⟩,
    exact ⟨V, V_in, V_sub⟩ }
end

lemma uniform_space.has_basis_nhds (x : α) :
  has_basis (𝓝 x) (λ s : set (α × α), s ∈ 𝓤 α ∧ symmetric_rel s) (λ s, ball x s) :=
⟨λ t, by simp [uniform_space.mem_nhds_iff_symm, and_assoc]⟩

open uniform_space

lemma uniform_space.has_basis_nhds_prod (x y : α) :
  has_basis (𝓝 (x, y)) (λ s, s ∈ 𝓤 α ∧ symmetric_rel s) $ λ s, (ball x s).prod (ball y s) :=
begin
  rw nhds_prod_eq,
  apply (has_basis_nhds x).prod' (has_basis_nhds y),
  rintro U V ⟨U_in, U_symm⟩ ⟨V_in, V_symm⟩,
  exact ⟨U ∩ V, ⟨(𝓤 α).inter_sets U_in V_in, symmetric_rel_inter U_symm V_symm⟩,
         ball_mono (inter_subset_left U V) x, ball_mono (inter_subset_right U V) y⟩,
end

lemma nhds_eq_uniformity {x : α} : 𝓝 x = (𝓤 α).lift' (λs:set (α×α), {y | (x, y) ∈ s}) :=
(nhds_basis_uniformity' (𝓤 α).basis_sets).eq_binfi

lemma mem_nhds_left (x : α) {s : set (α×α)} (h : s ∈ 𝓤 α) :
  {y : α | (x, y) ∈ s} ∈ 𝓝 x :=
(nhds_basis_uniformity' (𝓤 α).basis_sets).mem_of_mem h

lemma mem_nhds_right (y : α) {s : set (α×α)} (h : s ∈ 𝓤 α) :
  {x : α | (x, y) ∈ s} ∈ 𝓝 y :=
mem_nhds_left _ (symm_le_uniformity h)

lemma tendsto_right_nhds_uniformity {a : α} : tendsto (λa', (a', a)) (𝓝 a) (𝓤 α) :=
assume s, mem_nhds_right a

lemma tendsto_left_nhds_uniformity {a : α} : tendsto (λa', (a, a')) (𝓝 a) (𝓤 α) :=
assume s, mem_nhds_left a

lemma lift_nhds_left {x : α} {g : set α → filter β} (hg : monotone g) :
  (𝓝 x).lift g = (𝓤 α).lift (λs:set (α×α), g {y | (x, y) ∈ s}) :=
eq.trans
  begin
    rw [nhds_eq_uniformity],
    exact (filter.lift_assoc $ monotone_principal.comp $ monotone_preimage.comp monotone_preimage )
  end
  (congr_arg _ $ funext $ assume s, filter.lift_principal hg)

lemma lift_nhds_right {x : α} {g : set α → filter β} (hg : monotone g) :
  (𝓝 x).lift g = (𝓤 α).lift (λs:set (α×α), g {y | (y, x) ∈ s}) :=
calc (𝓝 x).lift g = (𝓤 α).lift (λs:set (α×α), g {y | (x, y) ∈ s}) : lift_nhds_left hg
  ... = ((@prod.swap α α) <$> (𝓤 α)).lift (λs:set (α×α), g {y | (x, y) ∈ s}) : by rw [←uniformity_eq_symm]
  ... = (𝓤 α).lift (λs:set (α×α), g {y | (x, y) ∈ image prod.swap s}) :
    map_lift_eq2 $ hg.comp monotone_preimage
  ... = _ : by simp [image_swap_eq_preimage_swap]

lemma nhds_nhds_eq_uniformity_uniformity_prod {a b : α} :
  filter.prod (𝓝 a) (𝓝 b) =
  (𝓤 α).lift (λs:set (α×α), (𝓤 α).lift' (λt:set (α×α),
    set.prod {y : α | (y, a) ∈ s} {y : α | (b, y) ∈ t})) :=
begin
  rw [prod_def],
  show (𝓝 a).lift (λs:set α, (𝓝 b).lift (λt:set α, 𝓟 (set.prod s t))) = _,
  rw [lift_nhds_right],
  apply congr_arg, funext s,
  rw [lift_nhds_left],
  refl,
  exact monotone_principal.comp (monotone_prod monotone_const monotone_id),
  exact (monotone_lift' monotone_const $ monotone_lam $
    assume x, monotone_prod monotone_id monotone_const)
end

lemma nhds_eq_uniformity_prod {a b : α} :
  𝓝 (a, b) =
  (𝓤 α).lift' (λs:set (α×α), set.prod {y : α | (y, a) ∈ s} {y : α | (b, y) ∈ s}) :=
begin
  rw [nhds_prod_eq, nhds_nhds_eq_uniformity_uniformity_prod, lift_lift'_same_eq_lift'],
  { intro s, exact monotone_prod monotone_const monotone_preimage },
  { intro t, exact monotone_prod monotone_preimage monotone_const }
end

lemma nhdset_of_mem_uniformity {d : set (α×α)} (s : set (α×α)) (hd : d ∈ 𝓤 α) :
  ∃(t : set (α×α)), is_open t ∧ s ⊆ t ∧ t ⊆ {p | ∃x y, (p.1, x) ∈ d ∧ (x, y) ∈ s ∧ (y, p.2) ∈ d} :=
let cl_d := {p:α×α | ∃x y, (p.1, x) ∈ d ∧ (x, y) ∈ s ∧ (y, p.2) ∈ d} in
have ∀p ∈ s, ∃t ⊆ cl_d, is_open t ∧ p ∈ t, from
  assume ⟨x, y⟩ hp, mem_nhds_sets_iff.mp $
  show cl_d ∈ 𝓝 (x, y),
  begin
    rw [nhds_eq_uniformity_prod, mem_lift'_sets],
    exact ⟨d, hd, assume ⟨a, b⟩ ⟨ha, hb⟩, ⟨x, y, ha, hp, hb⟩⟩,
    exact monotone_prod monotone_preimage monotone_preimage
  end,
have ∃t:(Π(p:α×α) (h:p ∈ s), set (α×α)),
    ∀p, ∀h:p ∈ s, t p h ⊆ cl_d ∧ is_open (t p h) ∧ p ∈ t p h,
  by simp [classical.skolem] at this; simp; assumption,
match this with
| ⟨t, ht⟩ :=
  ⟨(⋃ p:α×α, ⋃ h : p ∈ s, t p h : set (α×α)),
    is_open_Union $ assume (p:α×α), is_open_Union $ assume hp, (ht p hp).right.left,
    assume ⟨a, b⟩ hp, begin simp; exact ⟨a, b, hp, (ht (a,b) hp).right.right⟩ end,
    Union_subset $ assume p, Union_subset $ assume hp, (ht p hp).left⟩
end

/-!
### Closure and interior in uniform spaces
-/

lemma closure_eq_uniformity (s : set $ α × α) :
  closure s = ⋂ V ∈ {V | V ∈ 𝓤 α ∧ symmetric_rel V}, V ○ s ○ V :=
begin
  ext ⟨x, y⟩,
  simp_rw [mem_closure_iff_nhds_basis (uniform_space.has_basis_nhds_prod x y),
           mem_Inter, mem_set_of_eq],
  apply forall_congr,
  intro V,
  apply forall_congr,
  rintros ⟨V_in, V_symm⟩,
  simp_rw [mem_comp_comp V_symm, inter_comm, exists_prop],
  exact iff.rfl,
end

lemma uniformity_has_basis_closed : has_basis (𝓤 α) (λ V : set (α × α), V ∈ 𝓤 α ∧ is_closed V) id :=
begin
  rw filter.has_basis_self,
  intro t,
  split,
  { intro h,
    rcases comp_comp_symm_mem_uniformity_sets h with ⟨w, w_in, w_symm, r⟩,
    refine ⟨closure w, _,  is_closed_closure, _⟩,
    apply mem_sets_of_superset w_in subset_closure,
    refine subset.trans _ r,
    rw closure_eq_uniformity,
    apply Inter_subset_of_subset,
    apply Inter_subset,
    exact ⟨w_in, w_symm⟩ },
  { rintros ⟨r, r_in, r_closed, r_sub⟩,
    exact mem_sets_of_superset r_in r_sub, }
end

/-- Closed entourages form a basis of the uniformity filter. -/
lemma uniformity_has_basis_closure : has_basis (𝓤 α) (λ V : set (α × α), V ∈ 𝓤 α) closure :=
⟨begin
  intro t,
  rw uniformity_has_basis_closed.mem_iff,
  split,
  { rintros ⟨r, ⟨r_in, r_closed⟩, r_sub⟩,
    use [r, r_in],
    convert r_sub,
    rw closure_eq_of_is_closed r_closed,
    refl },
  { rintros ⟨r, r_in, r_sub⟩,
    exact ⟨closure r, ⟨mem_sets_of_superset r_in subset_closure, is_closed_closure⟩, r_sub⟩ }
end⟩

lemma closure_eq_inter_uniformity {t : set (α×α)} :
  closure t = (⋂ d ∈ 𝓤 α, d ○ (t ○ d)) :=
set.ext $ assume ⟨a, b⟩,
calc (a, b) ∈ closure t ↔ (𝓝 (a, b) ⊓ 𝓟 t ≠ ⊥) : by simp [closure_eq_cluster_pts, cluster_pt]
  ... ↔ (((@prod.swap α α) <$> 𝓤 α).lift'
      (λ (s : set (α × α)), set.prod {x : α | (x, a) ∈ s} {y : α | (b, y) ∈ s}) ⊓ 𝓟 t ≠ ⊥) :
    by rw [←uniformity_eq_symm, nhds_eq_uniformity_prod]
  ... ↔ ((map (@prod.swap α α) (𝓤 α)).lift'
      (λ (s : set (α × α)), set.prod {x : α | (x, a) ∈ s} {y : α | (b, y) ∈ s}) ⊓ 𝓟 t ≠ ⊥) :
    by refl
  ... ↔ ((𝓤 α).lift'
      (λ (s : set (α × α)), set.prod {y : α | (a, y) ∈ s} {x : α | (x, b) ∈ s}) ⊓ 𝓟 t ≠ ⊥) :
  begin
    rw [map_lift'_eq2],
    simp [image_swap_eq_preimage_swap, function.comp],
    exact monotone_prod monotone_preimage monotone_preimage
  end
  ... ↔ (∀s ∈ 𝓤 α, (set.prod {y : α | (a, y) ∈ s} {x : α | (x, b) ∈ s} ∩ t).nonempty) :
  begin
    rw [lift'_inf_principal_eq, lift'_ne_bot_iff],
    exact monotone_inter (monotone_prod monotone_preimage monotone_preimage) monotone_const
  end
  ... ↔ (∀ s ∈ 𝓤 α, (a, b) ∈ s ○ (t ○ s)) :
    forall_congr $ assume s, forall_congr $ assume hs,
    ⟨assume ⟨⟨x, y⟩, ⟨⟨hx, hy⟩, hxyt⟩⟩, ⟨x, hx, y, hxyt, hy⟩,
      assume ⟨x, hx, y, hxyt, hy⟩, ⟨⟨x, y⟩, ⟨⟨hx, hy⟩, hxyt⟩⟩⟩
  ... ↔ _ : by simp

lemma uniformity_eq_uniformity_closure : 𝓤 α = (𝓤 α).lift' closure :=
le_antisymm
  (le_infi $ assume s, le_infi $ assume hs, by simp; filter_upwards [hs] subset_closure)
  (calc (𝓤 α).lift' closure ≤ (𝓤 α).lift' (λd, d ○ (d ○ d)) :
      lift'_mono' (by intros s hs; rw [closure_eq_inter_uniformity]; exact bInter_subset_of_mem hs)
    ... ≤ (𝓤 α) : comp_le_uniformity3)

lemma uniformity_eq_uniformity_interior : 𝓤 α = (𝓤 α).lift' interior :=
le_antisymm
  (le_infi $ assume d, le_infi $ assume hd,
    let ⟨s, hs, hs_comp⟩ := (mem_lift'_sets $
      monotone_comp_rel monotone_id $ monotone_comp_rel monotone_id monotone_id).mp (comp_le_uniformity3 hd) in
    let ⟨t, ht, hst, ht_comp⟩ := nhdset_of_mem_uniformity s hs in
    have s ⊆ interior d, from
      calc s ⊆ t : hst
       ... ⊆ interior d : (subset_interior_iff_subset_of_open ht).mpr $
        assume x, assume : x ∈ t, let ⟨x, y, h₁, h₂, h₃⟩ := ht_comp this in hs_comp ⟨x, h₁, y, h₂, h₃⟩,
    have interior d ∈ 𝓤 α, by filter_upwards [hs] this,
    by simp [this])
  (assume s hs, ((𝓤 α).lift' interior).sets_of_superset (mem_lift' hs) interior_subset)

lemma interior_mem_uniformity {s : set (α × α)} (hs : s ∈ 𝓤 α) :
  interior s ∈ 𝓤 α :=
by rw [uniformity_eq_uniformity_interior]; exact mem_lift' hs

lemma mem_uniformity_is_closed {s : set (α×α)} (h : s ∈ 𝓤 α) :
  ∃t ∈ 𝓤 α, is_closed t ∧ t ⊆ s :=
have s ∈ (𝓤 α).lift' closure, by rwa [uniformity_eq_uniformity_closure] at h,
have ∃ t ∈ 𝓤 α, closure t ⊆ s,
  by rwa [mem_lift'_sets] at this; apply closure_mono,
let ⟨t, ht, hst⟩ := this in
⟨closure t, (𝓤 α).sets_of_superset ht subset_closure, is_closed_closure, hst⟩

/-!
### Uniformity bases
-/

lemma filter.has_basis.mem_uniformity_iff {p : β → Prop} {s : β → set (α×α)}
  (h : (𝓤 α).has_basis p s) {t : set (α × α)} :
  t ∈ 𝓤 α ↔ ∃ i (hi : p i), ∀ a b, (a, b) ∈ s i → (a, b) ∈ t :=
h.mem_iff.trans $ by simp only [prod.forall, subset_def]

/-- Symmetric entourages form a basis of `𝓤 α` -/
lemma uniform_space.has_basis_symmetric :
  (𝓤 α).has_basis (λ s : set (α × α), s ∈ 𝓤 α ∧ symmetric_rel s) id :=
⟨λ t, ⟨λ t_in, ⟨symmetrize_rel t,
           ⟨⟨symmetrize_mem_uniformity t_in, symmetric_symmetrize_rel t⟩,
            symmetrize_rel_subset_self _⟩⟩,
       λ ⟨s, ⟨s_in, h⟩, hst⟩, mem_sets_of_superset s_in hst⟩⟩

lemma uniform_space.has_seq_basis (h : is_countably_generated $ 𝓤 α) :
  ∃ V : ℕ → set (α × α), has_antimono_basis (𝓤 α) (λ _, true) V ∧ ∀ n, symmetric_rel (V n) :=
begin
  rcases h.has_antimono_basis with ⟨U, hbasis, hdec, monotrue⟩, clear monotrue,
  simp only [forall_prop_of_true] at hdec,
  use λ n, symmetrize_rel (U n),
  refine ⟨⟨⟨_⟩, by intros ; mono, by tauto⟩, λ n, symmetric_symmetrize_rel _⟩,
  intros t,
  rw hbasis.mem_iff,
  split,
  { rintro ⟨i, _, hi⟩,
    exact ⟨i, trivial, subset.trans (inter_subset_left _ _) hi⟩ },
  { rintro ⟨i, _, hi⟩,
    rcases hbasis.mem_iff.mp (symmetrize_mem_uniformity $ hbasis.mem_of_mem trivial)
      with ⟨j, _, hj⟩,
    use j,
    tauto }
end

/-! ### Uniform continuity -/

/-- A function `f : α → β` is *uniformly continuous* if `(f x, f y)` tends to the diagonal
as `(x, y)` tends to the diagonal. In other words, if `x` is sufficiently close to `y`, then
`f x` is close to `f y` no matter where `x` and `y` are located in `α`. -/
def uniform_continuous [uniform_space β] (f : α → β) :=
tendsto (λx:α×α, (f x.1, f x.2)) (𝓤 α) (𝓤 β)

theorem uniform_continuous_def [uniform_space β] {f : α → β} :
  uniform_continuous f ↔ ∀ r ∈ 𝓤 β, { x : α × α | (f x.1, f x.2) ∈ r} ∈ 𝓤 α :=
iff.rfl

theorem uniform_continuous_iff_eventually [uniform_space β] {f : α → β} :
  uniform_continuous f ↔ ∀ r ∈ 𝓤 β, ∀ᶠ (x : α × α) in 𝓤 α, (f x.1, f x.2) ∈ r :=
iff.rfl

lemma uniform_continuous_of_const [uniform_space β] {c : α → β} (h : ∀a b, c a = c b) :
  uniform_continuous c :=
have (λ (x : α × α), (c (x.fst), c (x.snd))) ⁻¹' id_rel = univ, from
  eq_univ_iff_forall.2 $ assume ⟨a, b⟩, h a b,
le_trans (map_le_iff_le_comap.2 $ by simp [comap_principal, this, univ_mem_sets]) refl_le_uniformity

lemma uniform_continuous_id : uniform_continuous (@id α) :=
by simp [uniform_continuous]; exact tendsto_id

lemma uniform_continuous_const [uniform_space β] {b : β} : uniform_continuous (λa:α, b) :=
uniform_continuous_of_const $ λ _ _, rfl

lemma uniform_continuous.comp [uniform_space β] [uniform_space γ] {g : β → γ} {f : α → β}
  (hg : uniform_continuous g) (hf : uniform_continuous f) : uniform_continuous (g ∘ f) :=
hg.comp hf

lemma filter.has_basis.uniform_continuous_iff [uniform_space β] {p : γ → Prop} {s : γ → set (α×α)}
  (ha : (𝓤 α).has_basis p s) {q : δ → Prop} {t : δ → set (β×β)} (hb : (𝓤 β).has_basis q t)
  {f : α → β} :
  uniform_continuous f ↔ ∀ i (hi : q i), ∃ j (hj : p j), ∀ x y, (x, y) ∈ s j → (f x, f y) ∈ t i :=
(ha.tendsto_iff hb).trans $ by simp only [prod.forall]

end uniform_space

open_locale uniformity

section constructions

instance : partial_order (uniform_space α) :=
{ le          := λt s, t.uniformity ≤ s.uniformity,
  le_antisymm := assume t s h₁ h₂, uniform_space_eq $ le_antisymm h₁ h₂,
  le_refl     := assume t, le_refl _,
  le_trans    := assume a b c h₁ h₂, le_trans h₁ h₂ }

instance : has_Inf (uniform_space α) :=
⟨assume s, uniform_space.of_core {
  uniformity := (⨅u∈s, @uniformity α u),
  refl       := le_infi $ assume u, le_infi $ assume hu, u.refl,
  symm       := le_infi $ assume u, le_infi $ assume hu,
    le_trans (map_mono $ infi_le_of_le _ $ infi_le _ hu) u.symm,
  comp       := le_infi $ assume u, le_infi $ assume hu,
    le_trans (lift'_mono (infi_le_of_le _ $ infi_le _ hu) $ le_refl _) u.comp }⟩

private lemma Inf_le {tt : set (uniform_space α)} {t : uniform_space α} (h : t ∈ tt) :
  Inf tt ≤ t :=
show (⨅u∈tt, @uniformity α u) ≤ t.uniformity,
  from infi_le_of_le t $ infi_le _ h

private lemma le_Inf {tt : set (uniform_space α)} {t : uniform_space α} (h : ∀t'∈tt, t ≤ t') :
  t ≤ Inf tt :=
show t.uniformity ≤ (⨅u∈tt, @uniformity α u),
  from le_infi $ assume t', le_infi $ assume ht', h t' ht'

instance : has_top (uniform_space α) :=
⟨uniform_space.of_core { uniformity := ⊤, refl := le_top, symm := le_top, comp := le_top }⟩

instance : has_bot (uniform_space α) :=
⟨{ to_topological_space := ⊥,
  uniformity  := 𝓟 id_rel,
  refl        := le_refl _,
  symm        := by simp [tendsto]; apply subset.refl,
  comp        :=
  begin
    rw [lift'_principal], {simp},
    exact monotone_comp_rel monotone_id monotone_id
  end,
  is_open_uniformity :=
    assume s, by simp [is_open_fold, subset_def, id_rel] {contextual := tt } } ⟩

instance : complete_lattice (uniform_space α) :=
{ sup           := λa b, Inf {x | a ≤ x ∧ b ≤ x},
  le_sup_left   := λ a b, le_Inf (λ _ ⟨h, _⟩, h),
  le_sup_right  := λ a b, le_Inf (λ _ ⟨_, h⟩, h),
  sup_le        := λ a b c h₁ h₂, Inf_le ⟨h₁, h₂⟩,
  inf           := λ a b, Inf {a, b},
  le_inf        := λ a b c h₁ h₂, le_Inf (λ u h,
                     by { cases h, exact h.symm ▸ h₁, exact (mem_singleton_iff.1 h).symm ▸ h₂ }),
  inf_le_left   := λ a b, Inf_le (by simp),
  inf_le_right  := λ a b, Inf_le (by simp),
  top           := ⊤,
  le_top        := λ a, show a.uniformity ≤ ⊤, from le_top,
  bot           := ⊥,
  bot_le        := λ u, u.refl,
  Sup           := λ tt, Inf {t | ∀ t' ∈ tt, t' ≤ t},
  le_Sup        := λ s u h, le_Inf (λ u' h', h' u h),
  Sup_le        := λ s u h, Inf_le h,
  Inf           := Inf,
  le_Inf        := λ s a hs, le_Inf hs,
  Inf_le        := λ s a ha, Inf_le ha,
  ..uniform_space.partial_order }

lemma infi_uniformity {ι : Sort*} {u : ι → uniform_space α} :
  (infi u).uniformity = (⨅i, (u i).uniformity) :=
show (⨅a (h : ∃i:ι, u i = a), a.uniformity) = _, from
le_antisymm
  (le_infi $ assume i, infi_le_of_le (u i) $ infi_le _ ⟨i, rfl⟩)
  (le_infi $ assume a, le_infi $ assume ⟨i, (ha : u i = a)⟩, ha ▸ infi_le _ _)

lemma inf_uniformity {u v : uniform_space α} :
  (u ⊓ v).uniformity = u.uniformity ⊓ v.uniformity :=
have (u ⊓ v) = (⨅i (h : i = u ∨ i = v), i), by simp [infi_or, infi_inf_eq],
calc (u ⊓ v).uniformity = ((⨅i (h : i = u ∨ i = v), i) : uniform_space α).uniformity : by rw [this]
  ... = _ : by simp [infi_uniformity, infi_or, infi_inf_eq]

instance inhabited_uniform_space : inhabited (uniform_space α) := ⟨⊥⟩
instance inhabited_uniform_space_core : inhabited (uniform_space.core α) :=
⟨@uniform_space.to_core _ (default _)⟩

/-- Given `f : α → β` and a uniformity `u` on `β`, the inverse image of `u` under `f`
  is the inverse image in the filter sense of the induced function `α × α → β × β`. -/
def uniform_space.comap (f : α → β) (u : uniform_space β) : uniform_space α :=
{ uniformity := u.uniformity.comap (λp:α×α, (f p.1, f p.2)),
  to_topological_space := u.to_topological_space.induced f,
  refl := le_trans (by simp; exact assume ⟨a, b⟩ (h : a = b), h ▸ rfl) (comap_mono u.refl),
  symm := by simp [tendsto_comap_iff, prod.swap, (∘)]; exact tendsto_swap_uniformity.comp tendsto_comap,
  comp := le_trans
    begin
      rw [comap_lift'_eq, comap_lift'_eq2],
      exact (lift'_mono' $ assume s hs ⟨a₁, a₂⟩ ⟨x, h₁, h₂⟩, ⟨f x, h₁, h₂⟩),
      repeat { exact monotone_comp_rel monotone_id monotone_id }
    end
    (comap_mono u.comp),
  is_open_uniformity := λ s, begin
    change (@is_open α (u.to_topological_space.induced f) s ↔ _),
    simp [is_open_iff_nhds, nhds_induced, mem_nhds_uniformity_iff_right, filter.comap, and_comm],
    refine ball_congr (λ x hx, ⟨_, _⟩),
    { rintro ⟨t, hts, ht⟩, refine ⟨_, ht, _⟩,
      rintro ⟨x₁, x₂⟩ h rfl, exact hts (h rfl) },
    { rintro ⟨t, ht, hts⟩,
      exact ⟨{y | (f x, y) ∈ t}, λ y hy, @hts (x, y) hy rfl,
        mem_nhds_uniformity_iff_right.1 $ mem_nhds_left _ ht⟩ }
  end }

lemma uniformity_comap [uniform_space α] [uniform_space β] {f : α → β}
  (h : ‹uniform_space α› = uniform_space.comap f ‹uniform_space β›) :
  𝓤 α = comap (prod.map f f) (𝓤 β) :=
by { rw h, refl }

lemma uniform_space_comap_id {α : Type*} : uniform_space.comap (id : α → α) = id :=
by ext u ; dsimp [uniform_space.comap] ; rw [prod.id_prod, filter.comap_id]

lemma uniform_space.comap_comap_comp {α β γ} [uγ : uniform_space γ] {f : α → β} {g : β → γ} :
  uniform_space.comap (g ∘ f) uγ = uniform_space.comap f (uniform_space.comap g uγ) :=
by ext ; dsimp [uniform_space.comap] ; rw filter.comap_comap_comp

lemma uniform_continuous_iff {α β} [uα : uniform_space α] [uβ : uniform_space β] {f : α → β} :
  uniform_continuous f ↔ uα ≤ uβ.comap f :=
filter.map_le_iff_le_comap

lemma uniform_continuous_comap {f : α → β} [u : uniform_space β] :
  @uniform_continuous α β (uniform_space.comap f u) u f :=
tendsto_comap

theorem to_topological_space_comap {f : α → β} {u : uniform_space β} :
  @uniform_space.to_topological_space _ (uniform_space.comap f u) =
  topological_space.induced f (@uniform_space.to_topological_space β u) := rfl

lemma uniform_continuous_comap' {f : γ → β} {g : α → γ} [v : uniform_space β] [u : uniform_space α]
  (h : uniform_continuous (f ∘ g)) : @uniform_continuous α γ u (uniform_space.comap f v) g :=
tendsto_comap_iff.2 h

lemma to_topological_space_mono {u₁ u₂ : uniform_space α} (h : u₁ ≤ u₂) :
  @uniform_space.to_topological_space _ u₁ ≤ @uniform_space.to_topological_space _ u₂ :=
le_of_nhds_le_nhds $ assume a,
  by rw [@nhds_eq_uniformity α u₁ a, @nhds_eq_uniformity α u₂ a]; exact (lift'_mono h $ le_refl _)

lemma uniform_continuous.continuous [uniform_space α] [uniform_space β] {f : α → β}
  (hf : uniform_continuous f) : continuous f :=
continuous_iff_le_induced.mpr $ to_topological_space_mono $ uniform_continuous_iff.1 hf

lemma to_topological_space_bot : @uniform_space.to_topological_space α ⊥ = ⊥ := rfl

lemma to_topological_space_top : @uniform_space.to_topological_space α ⊤ = ⊤ :=
top_unique $ assume s hs, s.eq_empty_or_nonempty.elim
  (assume : s = ∅, this.symm ▸ @is_open_empty _ ⊤)
  (assume  ⟨x, hx⟩,
    have s = univ, from top_unique $ assume y hy, hs x hx (x, y) rfl,
    this.symm ▸ @is_open_univ _ ⊤)

lemma to_topological_space_infi {ι : Sort*} {u : ι → uniform_space α} :
  (infi u).to_topological_space = ⨅i, (u i).to_topological_space :=
classical.by_cases
  (assume h : nonempty ι,
    eq_of_nhds_eq_nhds $ assume a,
    begin
      rw [nhds_infi, nhds_eq_uniformity],
      change (infi u).uniformity.lift' (preimage $ prod.mk a) = _,
      begin
        rw [infi_uniformity, lift'_infi],
        exact (congr_arg _ $ funext $ assume i, (@nhds_eq_uniformity α (u i) a).symm),
        exact h,
        exact assume a b, rfl
      end
    end)
  (assume : ¬ nonempty ι,
    le_antisymm
      (le_infi $ assume i, to_topological_space_mono $ infi_le _ _)
      (have infi u = ⊤, from top_unique $ le_infi $ assume i, (this ⟨i⟩).elim,
        have @uniform_space.to_topological_space _ (infi u) = ⊤,
          from this.symm ▸ to_topological_space_top,
        this.symm ▸ le_top))

lemma to_topological_space_Inf {s : set (uniform_space α)} :
  (Inf s).to_topological_space = (⨅i∈s, @uniform_space.to_topological_space α i) :=
begin
  rw [Inf_eq_infi, to_topological_space_infi],
  apply congr rfl,
  funext x,
  exact to_topological_space_infi
end

lemma to_topological_space_inf {u v : uniform_space α} :
  (u ⊓ v).to_topological_space = u.to_topological_space ⊓ v.to_topological_space :=
by rw [to_topological_space_Inf, infi_pair]

instance : uniform_space empty := ⊥
instance : uniform_space unit := ⊥
instance : uniform_space bool := ⊥
instance : uniform_space ℕ := ⊥
instance : uniform_space ℤ := ⊥

instance {p : α → Prop} [t : uniform_space α] : uniform_space (subtype p) :=
uniform_space.comap subtype.val t

lemma uniformity_subtype {p : α → Prop} [t : uniform_space α] :
  𝓤 (subtype p) = comap (λq:subtype p × subtype p, (q.1.1, q.2.1)) (𝓤 α) :=
rfl

lemma uniform_continuous_subtype_val {p : α → Prop} [uniform_space α] :
  uniform_continuous (subtype.val : {a : α // p a} → α) :=
uniform_continuous_comap

lemma uniform_continuous_subtype_mk {p : α → Prop} [uniform_space α] [uniform_space β]
  {f : β → α} (hf : uniform_continuous f) (h : ∀x, p (f x)) :
  uniform_continuous (λx, ⟨f x, h x⟩ : β → subtype p) :=
uniform_continuous_comap' hf

lemma tendsto_of_uniform_continuous_subtype
  [uniform_space α] [uniform_space β] {f : α → β} {s : set α} {a : α}
  (hf : uniform_continuous (λx:s, f x.val)) (ha : s ∈ 𝓝 a) :
  tendsto f (𝓝 a) (𝓝 (f a)) :=
by rw [(@map_nhds_subtype_val_eq α _ s a (mem_of_nhds ha) ha).symm]; exact
tendsto_map' (continuous_iff_continuous_at.mp hf.continuous _)


section prod

/- a similar product space is possible on the function space (uniformity of pointwise convergence),
  but we want to have the uniformity of uniform convergence on function spaces -/
instance [u₁ : uniform_space α] [u₂ : uniform_space β] : uniform_space (α × β) :=
uniform_space.of_core_eq
  (u₁.comap prod.fst ⊓ u₂.comap prod.snd).to_core
  prod.topological_space
  (calc prod.topological_space = (u₁.comap prod.fst ⊓ u₂.comap prod.snd).to_topological_space :
      by rw [to_topological_space_inf, to_topological_space_comap, to_topological_space_comap]; refl
    ... = _ : by rw [uniform_space.to_core_to_topological_space])

theorem uniformity_prod [uniform_space α] [uniform_space β] : 𝓤 (α × β) =
  (𝓤 α).comap (λp:(α × β) × α × β, (p.1.1, p.2.1)) ⊓
  (𝓤 β).comap (λp:(α × β) × α × β, (p.1.2, p.2.2)) :=
inf_uniformity

lemma uniformity_prod_eq_prod [uniform_space α] [uniform_space β] :
  𝓤 (α×β) =
    map (λp:(α×α)×(β×β), ((p.1.1, p.2.1), (p.1.2, p.2.2))) (filter.prod (𝓤 α) (𝓤 β)) :=
have map (λp:(α×α)×(β×β), ((p.1.1, p.2.1), (p.1.2, p.2.2))) =
  comap (λp:(α×β)×(α×β), ((p.1.1, p.2.1), (p.1.2, p.2.2))),
  from funext $ assume f, map_eq_comap_of_inverse
    (funext $ assume ⟨⟨_, _⟩, ⟨_, _⟩⟩, rfl) (funext $ assume ⟨⟨_, _⟩, ⟨_, _⟩⟩, rfl),
by rw [this, uniformity_prod, filter.prod, comap_inf, comap_comap_comp, comap_comap_comp]

lemma mem_map_sets_iff' {α : Type*} {β : Type*} {f : filter α} {m : α → β} {t : set β} :
  t ∈ (map m f).sets ↔ (∃s∈f, m '' s ⊆ t) :=
mem_map_sets_iff

lemma mem_uniformity_of_uniform_continuous_invariant [uniform_space α] {s:set (α×α)} {f : α → α → α}
  (hf : uniform_continuous (λp:α×α, f p.1 p.2)) (hs : s ∈ 𝓤 α) :
  ∃u∈𝓤 α, ∀a b c, (a, b) ∈ u → (f a c, f b c) ∈ s :=
begin
  rw [uniform_continuous, uniformity_prod_eq_prod, tendsto_map'_iff, (∘)] at hf,
  rcases mem_map_sets_iff'.1 (hf hs) with ⟨t, ht, hts⟩, clear hf,
  rcases mem_prod_iff.1 ht with ⟨u, hu, v, hv, huvt⟩, clear ht,
  refine ⟨u, hu, assume a b c hab, hts $ (mem_image _ _ _).2 ⟨⟨⟨a, b⟩, ⟨c, c⟩⟩, huvt ⟨_, _⟩, _⟩⟩,
  exact hab,
  exact refl_mem_uniformity hv,
  refl
end

lemma mem_uniform_prod [t₁ : uniform_space α] [t₂ : uniform_space β] {a : set (α × α)} {b : set (β × β)}
  (ha : a ∈ 𝓤 α) (hb : b ∈ 𝓤 β) :
  {p:(α×β)×(α×β) | (p.1.1, p.2.1) ∈ a ∧ (p.1.2, p.2.2) ∈ b } ∈ (@uniformity (α × β) _) :=
by rw [uniformity_prod]; exact inter_mem_inf_sets (preimage_mem_comap ha) (preimage_mem_comap hb)

lemma tendsto_prod_uniformity_fst [uniform_space α] [uniform_space β] :
  tendsto (λp:(α×β)×(α×β), (p.1.1, p.2.1)) (𝓤 (α × β)) (𝓤 α) :=
le_trans (map_mono (@inf_le_left (uniform_space (α×β)) _ _ _)) map_comap_le

lemma tendsto_prod_uniformity_snd [uniform_space α] [uniform_space β] :
  tendsto (λp:(α×β)×(α×β), (p.1.2, p.2.2)) (𝓤 (α × β)) (𝓤 β) :=
le_trans (map_mono (@inf_le_right (uniform_space (α×β)) _ _ _)) map_comap_le

lemma uniform_continuous_fst [uniform_space α] [uniform_space β] : uniform_continuous (λp:α×β, p.1) :=
tendsto_prod_uniformity_fst

lemma uniform_continuous_snd [uniform_space α] [uniform_space β] : uniform_continuous (λp:α×β, p.2) :=
tendsto_prod_uniformity_snd

variables [uniform_space α] [uniform_space β] [uniform_space γ]
lemma uniform_continuous.prod_mk
  {f₁ : α → β} {f₂ : α → γ} (h₁ : uniform_continuous f₁) (h₂ : uniform_continuous f₂) :
  uniform_continuous (λa, (f₁ a, f₂ a)) :=
by rw [uniform_continuous, uniformity_prod]; exact
tendsto_inf.2 ⟨tendsto_comap_iff.2 h₁, tendsto_comap_iff.2 h₂⟩

lemma uniform_continuous.prod_mk_left {f : α × β → γ} (h : uniform_continuous f) (b) :
  uniform_continuous (λ a, f (a,b)) :=
h.comp (uniform_continuous_id.prod_mk uniform_continuous_const)

lemma uniform_continuous.prod_mk_right {f : α × β → γ} (h : uniform_continuous f) (a) :
  uniform_continuous (λ b, f (a,b)) :=
h.comp (uniform_continuous_const.prod_mk  uniform_continuous_id)

lemma uniform_continuous.prod_map [uniform_space δ] {f : α → γ} {g : β → δ}
  (hf : uniform_continuous f) (hg : uniform_continuous g) :
  uniform_continuous (prod.map f g) :=
(hf.comp uniform_continuous_fst).prod_mk (hg.comp uniform_continuous_snd)

lemma to_topological_space_prod {α} {β} [u : uniform_space α] [v : uniform_space β] :
  @uniform_space.to_topological_space (α × β) prod.uniform_space =
    @prod.topological_space α β u.to_topological_space v.to_topological_space := rfl

end prod

section
open uniform_space function
variables {δ' : Type*} [uniform_space α] [uniform_space β] [uniform_space γ] [uniform_space δ]
  [uniform_space δ']

local notation f `∘₂` g := function.bicompr f g

/-- Uniform continuity for functions of two variables. -/
def uniform_continuous₂ (f : α → β → γ) := uniform_continuous (uncurry f)

lemma uniform_continuous₂_def (f : α → β → γ) :
  uniform_continuous₂ f ↔ uniform_continuous (uncurry f) := iff.rfl

lemma uniform_continuous₂.uniform_continuous {f : α → β → γ} (h : uniform_continuous₂ f) :
  uniform_continuous (uncurry f) := h

lemma uniform_continuous₂_curry (f : α × β → γ) :
  uniform_continuous₂ (function.curry f) ↔ uniform_continuous f :=
by rw [uniform_continuous₂, uncurry_curry]

lemma uniform_continuous₂.comp {f : α → β → γ} {g : γ → δ}
  (hg : uniform_continuous g) (hf : uniform_continuous₂ f) :
  uniform_continuous₂ (g ∘₂ f) :=
hg.comp hf

lemma uniform_continuous₂.bicompl {f : α → β → γ} {ga : δ → α} {gb : δ' → β}
  (hf : uniform_continuous₂ f) (hga : uniform_continuous ga) (hgb : uniform_continuous gb) :
  uniform_continuous₂ (bicompl f ga gb) :=
hf.uniform_continuous.comp (hga.prod_map hgb)

end

lemma to_topological_space_subtype [u : uniform_space α] {p : α → Prop} :
  @uniform_space.to_topological_space (subtype p) subtype.uniform_space =
    @subtype.topological_space α p u.to_topological_space := rfl

section sum
variables [uniform_space α] [uniform_space β]
open sum

/-- Uniformity on a disjoint union. Entourages of the diagonal in the union are obtained
by taking independently an entourage of the diagonal in the first part, and an entourage of
the diagonal in the second part. -/
def uniform_space.core.sum : uniform_space.core (α ⊕ β) :=
uniform_space.core.mk'
  (map (λ p : α × α, (inl p.1, inl p.2)) (𝓤 α) ⊔ map (λ p : β × β, (inr p.1, inr p.2)) (𝓤 β))
  (λ r ⟨H₁, H₂⟩ x, by cases x; [apply refl_mem_uniformity H₁, apply refl_mem_uniformity H₂])
  (λ r ⟨H₁, H₂⟩, ⟨symm_le_uniformity H₁, symm_le_uniformity H₂⟩)
  (λ r ⟨Hrα, Hrβ⟩, begin
    rcases comp_mem_uniformity_sets Hrα with ⟨tα, htα, Htα⟩,
    rcases comp_mem_uniformity_sets Hrβ with ⟨tβ, htβ, Htβ⟩,
    refine ⟨_,
      ⟨mem_map_sets_iff.2 ⟨tα, htα, subset_union_left _ _⟩,
       mem_map_sets_iff.2 ⟨tβ, htβ, subset_union_right _ _⟩⟩, _⟩,
    rintros ⟨_, _⟩ ⟨z, ⟨⟨a, b⟩, hab, ⟨⟩⟩ | ⟨⟨a, b⟩, hab, ⟨⟩⟩,
                       ⟨⟨_, c⟩, hbc, ⟨⟩⟩ | ⟨⟨_, c⟩, hbc, ⟨⟩⟩⟩,
    { have A : (a, c) ∈ tα ○ tα := ⟨b, hab, hbc⟩,
      exact Htα A },
    { have A : (a, c) ∈ tβ ○ tβ := ⟨b, hab, hbc⟩,
      exact Htβ A }
  end)

/-- The union of an entourage of the diagonal in each set of a disjoint union is again an entourage
of the diagonal. -/
lemma union_mem_uniformity_sum
  {a : set (α × α)} (ha : a ∈ 𝓤 α) {b : set (β × β)} (hb : b ∈ 𝓤 β) :
  ((λ p : (α × α), (inl p.1, inl p.2)) '' a ∪ (λ p : (β × β), (inr p.1, inr p.2)) '' b) ∈
    (@uniform_space.core.sum α β _ _).uniformity :=
⟨mem_map_sets_iff.2 ⟨_, ha, subset_union_left _ _⟩, mem_map_sets_iff.2 ⟨_, hb, subset_union_right _ _⟩⟩

/- To prove that the topology defined by the uniform structure on the disjoint union coincides with
the disjoint union topology, we need two lemmas saying that open sets can be characterized by
the uniform structure -/
lemma uniformity_sum_of_open_aux {s : set (α ⊕ β)} (hs : is_open s) {x : α ⊕ β} (xs : x ∈ s) :
  { p : ((α ⊕ β) × (α ⊕ β)) | p.1 = x → p.2 ∈ s } ∈ (@uniform_space.core.sum α β _ _).uniformity :=
begin
  cases x,
  { refine mem_sets_of_superset
      (union_mem_uniformity_sum (mem_nhds_uniformity_iff_right.1 (mem_nhds_sets hs.1 xs)) univ_mem_sets)
      (union_subset _ _);
    rintro _ ⟨⟨_, b⟩, h, ⟨⟩⟩ ⟨⟩,
    exact h rfl },
  { refine mem_sets_of_superset
      (union_mem_uniformity_sum univ_mem_sets (mem_nhds_uniformity_iff_right.1 (mem_nhds_sets hs.2 xs)))
      (union_subset _ _);
    rintro _ ⟨⟨a, _⟩, h, ⟨⟩⟩ ⟨⟩,
    exact h rfl },
end

lemma open_of_uniformity_sum_aux {s : set (α ⊕ β)}
  (hs : ∀x ∈ s, { p : ((α ⊕ β) × (α ⊕ β)) | p.1 = x → p.2 ∈ s } ∈ (@uniform_space.core.sum α β _ _).uniformity) :
  is_open s :=
begin
  split,
  { refine (@is_open_iff_mem_nhds α _ _).2 (λ a ha, mem_nhds_uniformity_iff_right.2 _),
    rcases mem_map_sets_iff.1 (hs _ ha).1 with ⟨t, ht, st⟩,
    refine mem_sets_of_superset ht _,
    rintro p pt rfl, exact st ⟨_, pt, rfl⟩ rfl },
  { refine (@is_open_iff_mem_nhds β _ _).2 (λ b hb, mem_nhds_uniformity_iff_right.2 _),
    rcases mem_map_sets_iff.1 (hs _ hb).2 with ⟨t, ht, st⟩,
    refine mem_sets_of_superset ht _,
    rintro p pt rfl, exact st ⟨_, pt, rfl⟩ rfl }
end

/- We can now define the uniform structure on the disjoint union -/
instance sum.uniform_space : uniform_space (α ⊕ β) :=
{ to_core := uniform_space.core.sum,
  is_open_uniformity := λ s, ⟨uniformity_sum_of_open_aux, open_of_uniformity_sum_aux⟩ }

lemma sum.uniformity : 𝓤 (α ⊕ β) =
    map (λ p : α × α, (inl p.1, inl p.2)) (𝓤 α) ⊔
    map (λ p : β × β, (inr p.1, inr p.2)) (𝓤 β) := rfl

end sum

end constructions

-- For a version of the Lebesgue number lemma assuming only a sequentially compact space,
-- see topology/sequences.lean

lemma lebesgue_number_lemma {α : Type u} [uniform_space α] {s : set α} {ι} {c : ι → set α}
  (hs : compact s) (hc₁ : ∀ i, is_open (c i)) (hc₂ : s ⊆ ⋃ i, c i) :
  ∃ n ∈ 𝓤 α, ∀ x ∈ s, ∃ i, {y | (x, y) ∈ n} ⊆ c i :=
begin
  let u := λ n, {x | ∃ i (m ∈ 𝓤 α), {y | (x, y) ∈ m ○ n} ⊆ c i},
  have hu₁ : ∀ n ∈ 𝓤 α, is_open (u n),
  { refine λ n hn, is_open_uniformity.2 _,
    rintro x ⟨i, m, hm, h⟩,
    rcases comp_mem_uniformity_sets hm with ⟨m', hm', mm'⟩,
    apply (𝓤 α).sets_of_superset hm',
    rintros ⟨x, y⟩ hp rfl,
    refine ⟨i, m', hm', λ z hz, h (monotone_comp_rel monotone_id monotone_const mm' _)⟩,
    dsimp at hz ⊢, rw comp_rel_assoc,
    exact ⟨y, hp, hz⟩ },
  have hu₂ : s ⊆ ⋃ n ∈ 𝓤 α, u n,
  { intros x hx,
    rcases mem_Union.1 (hc₂ hx) with ⟨i, h⟩,
    rcases comp_mem_uniformity_sets (is_open_uniformity.1 (hc₁ i) x h) with ⟨m', hm', mm'⟩,
    exact mem_bUnion hm' ⟨i, _, hm', λ y hy, mm' hy rfl⟩ },
  rcases hs.elim_finite_subcover_image hu₁ hu₂ with ⟨b, bu, b_fin, b_cover⟩,
  refine ⟨_, Inter_mem_sets b_fin bu, λ x hx, _⟩,
  rcases mem_bUnion_iff.1 (b_cover hx) with ⟨n, bn, i, m, hm, h⟩,
  refine ⟨i, λ y hy, h _⟩,
  exact prod_mk_mem_comp_rel (refl_mem_uniformity hm) (bInter_subset_of_mem bn hy)
end

lemma lebesgue_number_lemma_sUnion {α : Type u} [uniform_space α] {s : set α} {c : set (set α)}
  (hs : compact s) (hc₁ : ∀ t ∈ c, is_open t) (hc₂ : s ⊆ ⋃₀ c) :
  ∃ n ∈ 𝓤 α, ∀ x ∈ s, ∃ t ∈ c, ∀ y, (x, y) ∈ n → y ∈ t :=
by rw sUnion_eq_Union at hc₂;
   simpa using lebesgue_number_lemma hs (by simpa) hc₂

/-!
### Expressing continuity properties in uniform spaces

We reformulate the various continuity properties of functions taking values in a uniform space
in terms of the uniformity in the target. Since the same lemmas (essentially with the same names)
also exist for metric spaces and emetric spaces (reformulating things in terms of the distance or
the edistance in the target), we put them in a namespace `uniform` here.

In the metric and emetric space setting, there are also similar lemmas where one assumes that
both the source and the target are metric spaces, reformulating things in terms of the distance
on both sides. These lemmas are generally written without primes, and the versions where only
the target is a metric space is primed. We follow the same convention here, thus giving lemmas
with primes.
-/

namespace uniform

variables [uniform_space α]

theorem tendsto_nhds_right {f : filter β} {u : β → α} {a : α} :
  tendsto u f (𝓝 a) ↔ tendsto (λ x, (a, u x)) f (𝓤 α)  :=
⟨λ H, tendsto_left_nhds_uniformity.comp H,
λ H s hs, by simpa [mem_of_nhds hs] using H (mem_nhds_uniformity_iff_right.1 hs)⟩

theorem tendsto_nhds_left {f : filter β} {u : β → α} {a : α} :
  tendsto u f (𝓝 a) ↔ tendsto (λ x, (u x, a)) f (𝓤 α)  :=
⟨λ H, tendsto_right_nhds_uniformity.comp H,
λ H s hs, by simpa [mem_of_nhds hs] using H (mem_nhds_uniformity_iff_left.1 hs)⟩

theorem continuous_at_iff'_right [topological_space β] {f : β → α} {b : β} :
  continuous_at f b ↔ tendsto (λ x, (f b, f x)) (𝓝 b) (𝓤 α) :=
by rw [continuous_at, tendsto_nhds_right]

theorem continuous_at_iff'_left [topological_space β] {f : β → α} {b : β} :
  continuous_at f b ↔ tendsto (λ x, (f x, f b)) (𝓝 b) (𝓤 α) :=
by rw [continuous_at, tendsto_nhds_left]

theorem continuous_within_at_iff'_right [topological_space β] {f : β → α} {b : β} {s : set β} :
  continuous_within_at f s b ↔ tendsto (λ x, (f b, f x)) (nhds_within b s) (𝓤 α) :=
by rw [continuous_within_at, tendsto_nhds_right]

theorem continuous_within_at_iff'_left [topological_space β] {f : β → α} {b : β} {s : set β} :
  continuous_within_at f s b ↔ tendsto (λ x, (f x, f b)) (nhds_within b s) (𝓤 α) :=
by rw [continuous_within_at, tendsto_nhds_left]

theorem continuous_on_iff'_right [topological_space β] {f : β → α} {s : set β} :
  continuous_on f s ↔ ∀ b ∈ s, tendsto (λ x, (f b, f x)) (nhds_within b s) (𝓤 α) :=
by simp [continuous_on, continuous_within_at_iff'_right]

theorem continuous_on_iff'_left [topological_space β] {f : β → α} {s : set β} :
  continuous_on f s ↔ ∀ b ∈ s, tendsto (λ x, (f x, f b)) (nhds_within b s) (𝓤 α) :=
by simp [continuous_on, continuous_within_at_iff'_left]

theorem continuous_iff'_right [topological_space β] {f : β → α} :
  continuous f ↔ ∀ b, tendsto (λ x, (f b, f x)) (𝓝 b) (𝓤 α) :=
continuous_iff_continuous_at.trans $ forall_congr $ λ b, tendsto_nhds_right

theorem continuous_iff'_left [topological_space β] {f : β → α} :
  continuous f ↔ ∀ b, tendsto (λ x, (f x, f b)) (𝓝 b) (𝓤 α) :=
continuous_iff_continuous_at.trans $ forall_congr $ λ b, tendsto_nhds_left

end uniform

lemma filter.tendsto.congr_uniformity {α β} [uniform_space β] {f g : α → β} {l : filter α} {b : β}
  (hf : tendsto f l (𝓝 b)) (hg : tendsto (λ x, (f x, g x)) l (𝓤 β)) :
  tendsto g l (𝓝 b) :=
uniform.tendsto_nhds_right.2 $ (uniform.tendsto_nhds_right.1 hf).uniformity_trans hg

lemma uniform.tendsto_congr {α β} [uniform_space β] {f g : α → β} {l : filter α} {b : β}
  (hfg : tendsto (λ x, (f x, g x)) l (𝓤 β)) :
  tendsto f l (𝓝 b) ↔ tendsto g l (𝓝 b) :=
⟨λ h, h.congr_uniformity hfg, λ h, h.congr_uniformity hfg.uniformity_symm⟩
