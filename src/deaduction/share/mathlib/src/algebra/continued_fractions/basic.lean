/-
Copyright (c) 2019 Kevin Kappelmann. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Kevin Kappelmann
-/
import data.seq.seq
import algebra.field
/-!
# Basic Definitions/Theorems for Continued Fractions

## Summary

We define generalised, simple, and regular continued fractions and functions to evaluate their
convergents. We follow the naming conventions from Wikipedia and [wall2018analytic], Chapter 1.

## Main definitions

1. Generalised continued fractions (gcfs)
2. Simple continued fractions (scfs)
3. (Regular) continued fractions ((r)cfs)
4. Computation of convergents using the recurrence relation in `convergents`.
5. Computation of convergents by directly evaluating the fraction described by the gcf in
`convergents'`.

## Implementation notes

1. The most commonly used kind of continued fractions in the literature are regular continued
fractions. We hence just call them `continued_fractions` in the library.
2. We use sequences from `data.seq` to encode potentially infinite sequences.

## References

- <https://en.wikipedia.org/wiki/Generalized_continued_fraction>
- [Wall, H.S., *Analytic Theory of Continued Fractions*][wall2018analytic]

## Tags

numerics, number theory, approximations, fractions
-/

-- Fix a carrier `α`.
variable (α : Type*)

/-- We collect a partial numerator `aᵢ` and partial denominator `bᵢ` in a pair `⟨aᵢ,bᵢ⟩`. -/
@[derive inhabited]
protected structure generalized_continued_fraction.pair := (a : α) (b : α)

/- Interlude: define some expected coercions and instances. -/
namespace generalized_continued_fraction.pair
open generalized_continued_fraction as gcf

/-- Make a gcf.pair printable. -/
instance [has_repr α] : has_repr (gcf.pair α) :=
⟨λ p, "(a : " ++ (repr p.a) ++ ", b : " ++ (repr p.b) ++ ")"⟩

section coe
/-! Interlude: define some expected coercions. -/
/- Fix another type `β` and assume `α` can be converted to `β`. -/
variables {α} {β : Type*} [has_coe α β]

/-- Coerce a pair by elementwise coercion. -/
instance has_coe_to_generalized_continued_fraction_pair : has_coe (gcf.pair α) (gcf.pair β) :=
⟨λ ⟨a, b⟩, ⟨(a : β), (b : β)⟩⟩

@[simp, norm_cast]
lemma coe_to_generalized_continued_fraction_pair {a b : α} :
  (↑(gcf.pair.mk a b) : gcf.pair β) = gcf.pair.mk (a : β) (b : β) :=
rfl

end coe
end generalized_continued_fraction.pair

/--
A *generalised continued fraction* (gcf) is a potentially infinite expression of the form

                                a₀
                h + ---------------------------
                                  a₁
                      b₀ + --------------------
                                    a₂
                            b₁ + --------------
                                        a₃
                                  b₂ + --------
                                      b₃ + ...

where `h` is called the *head term* or *integer part*, the `aᵢ` are called the
*partial numerators* and the `bᵢ` the *partial denominators* of the gcf.
We store the sequence of partial numerators and denominators in a sequence of
generalized_continued_fraction.pairs `s`.
For convenience, one often writes `[h; (a₀, b₀), (a₁, b₁), (a₂, b₂),...]`.
-/
structure generalized_continued_fraction :=
(h : α) (s : seq $ generalized_continued_fraction.pair α)

variable {α}

namespace generalized_continued_fraction
open generalized_continued_fraction as gcf

/-- Constructs a generalized continued fraction without fractional part. -/
def of_integer (a : α) : gcf α :=
⟨a, seq.nil⟩

instance [inhabited α] : inhabited (gcf α) := ⟨of_integer (default _)⟩

/-- Returns the sequence of partial numerators `aᵢ` of `g`. -/
def partial_numerators (g : gcf α) : seq α := g.s.map gcf.pair.a
/-- Returns the sequence of partial denominators `bᵢ` of `g`. -/
def partial_denominators (g : gcf α) : seq α := g.s.map gcf.pair.b

/-- A gcf terminated at position `n` if its sequence terminates at position `n`. -/
def terminated_at (g : gcf α) (n : ℕ) : Prop := g.s.terminated_at n

/-- It is decidable whether a gcf terminated at a given position. -/
instance terminated_at_decidable (g : gcf α) (n : ℕ) : decidable (g.terminated_at n) :=
by { unfold terminated_at, apply_instance }

/-- A gcf terminates if its sequence terminates. -/
def terminates (g : gcf α) : Prop := g.s.terminates

section coe
/-! Interlude: define some expected coercions. -/
-- Fix another type `β` and assume `α` can be converted to `β`.
variables {β : Type*} [has_coe α β]

/-- Coerce a sequence by elementwise coercion. -/
def seq.coe_to_seq : has_coe (seq α) (seq β) := ⟨seq.map (λ a, (a : β))⟩

local attribute [instance] seq.coe_to_seq

/-- Coerce a gcf by elementwise coercion. -/
instance has_coe_to_generalized_continued_fraction : has_coe (gcf α) (gcf β) :=
⟨λ ⟨h, s⟩, ⟨(h : β), (s : seq $ gcf.pair β)⟩⟩

@[simp, norm_cast]
lemma coe_to_generalized_continued_fraction {g : gcf α} :
  (↑(g : gcf α) : gcf β) = ⟨(g.h : β), (g.s : seq $ gcf.pair β)⟩ :=
by { cases g, refl }

end coe
end generalized_continued_fraction

/--
A generalized continued fraction is a *simple continued fraction* if all partial numerators are
equal to one.

                                1
                h + ---------------------------
                                  1
                      b₀ + --------------------
                                    1
                            b₁ + --------------
                                        1
                                  b₂ + --------
                                      b₃ + ...

-/
def generalized_continued_fraction.is_simple_continued_fraction
  (g : generalized_continued_fraction α) [has_one α] : Prop :=
∀ (n : ℕ) (aₙ : α), g.partial_numerators.nth n = some aₙ → aₙ = 1

variable (α)
/--
A *simple continued fraction* (scf) is a generalized continued fraction (gcf) whose partial
numerators are equal to one.

                                1
                h + ---------------------------
                                  1
                      b₀ + --------------------
                                    1
                            b₁ + --------------
                                        1
                                  b₂ + --------
                                      b₃ + ...

For convenience, one often writes `[h; b₀, b₁, b₂,...]`.
It is encoded as the subtype of gcfs that satisfy
`generalized_continued_fraction.is_simple_continued_fraction`.
 -/
def simple_continued_fraction [has_one α] :=
{g : generalized_continued_fraction α // g.is_simple_continued_fraction}

variable {α}
/- Interlude: define some expected coercions. -/
namespace simple_continued_fraction
open generalized_continued_fraction as gcf
open simple_continued_fraction as scf
variable [has_one α]

/-- Constructs a simple continued fraction without fractional part. -/
def of_integer (a : α) : scf α :=
⟨gcf.of_integer a, λ n aₙ h, by cases h⟩

instance : inhabited (scf α) := ⟨of_integer 1⟩

/-- Lift a scf to a gcf using the inclusion map. -/
instance has_coe_to_generalized_continued_fraction : has_coe (scf α) (gcf α) :=
by {unfold scf, apply_instance}

@[simp, norm_cast]
lemma coe_to_generalized_continued_fraction {s : scf α} : (↑s : gcf α) = s.val := rfl

end simple_continued_fraction

/--
A simple continued fraction is a *(regular) continued fraction* ((r)cf) if all partial denominators
`bᵢ` are positive, i.e. `0 < bᵢ`.
-/
def simple_continued_fraction.is_regular_continued_fraction [has_one α] [has_zero α] [has_lt α]
  (s : simple_continued_fraction α) : Prop :=
∀ (n : ℕ) (bₙ : α),
  (↑s : generalized_continued_fraction α).partial_denominators.nth n = some bₙ → 0 < bₙ

variable (α)

/--
A *(regular) continued fraction* ((r)cf) is a simple continued fraction (scf) whose partial
denominators are all positive. It is the subtype of scfs that satisfy
`simple_continued_fraction.is_regular_continued_fraction`.
 -/
def continued_fraction [has_one α] [has_zero α] [has_lt α] :=
{s : simple_continued_fraction α // s.is_regular_continued_fraction}

variable {α}

/- Interlude: define some expected coercions. -/
namespace continued_fraction
open generalized_continued_fraction as gcf
open simple_continued_fraction as scf
open continued_fraction as cf
variables [has_one α] [has_zero α] [has_lt α]

/-- Constructs a continued fraction without fractional part. -/
def of_integer (a : α) : cf α :=
⟨scf.of_integer a, λ n bₙ h, by cases h⟩

instance : inhabited (cf α) := ⟨of_integer 0⟩

/-- Lift a cf to a scf using the inclusion map. -/
instance has_coe_to_simple_continued_fraction : has_coe (cf α) (scf α) :=
by {unfold cf, apply_instance}

@[simp, norm_cast]
lemma coe_to_simple_continued_fraction {c : cf α} : (↑c : scf α) = c.val := rfl

/-- Lift a cf to a scf using the inclusion map. -/
instance has_coe_to_generalized_continued_fraction : has_coe (cf α) (gcf α) := ⟨λ c, ↑(↑c : scf α)⟩

@[simp, norm_cast squash]
lemma coe_to_generalized_continued_fraction {c : cf α} : (↑c : gcf α) = c.val := rfl

end continued_fraction

/-
We now define how to compute the convergents of a gcf. There are two standard ways to do this:
directly evaluating the (infinite) fraction described by the gcf or using a recurrence relation.
For (r)cfs, these computations are equivalent as shown in
`algebra.continued_fractions.convergents_equiv`.
-/
namespace generalized_continued_fraction
open generalized_continued_fraction as gcf

-- Fix a division ring for the computations.
variables {K : Type*} [division_ring K]

/-
We start with the definition of the recurrence relation. Given a gcf `g`, for all `n ≥ 1`, we define
- `A₋₁ = 1,  A₀ = h,  Aₙ = bₙ₋₁ * Aₙ₋₁ + aₙ₋₁ * Aₙ₋₂`, and
- `B₋₁ = 0,  B₀ = 1,  Bₙ = bₙ₋₁ * Bₙ₋₁ + aₙ₋₁ * Bₙ₋₂`.

`Aₙ, `Bₙ` are called the *nth continuants*, Aₙ the *nth numerator*, and `Bₙ` the
*nth denominator* of `g`. The *nth convergent* of `g` is given by `Aₙ / Bₙ`.
-/

/--
Returns the next numerator `Aₙ = bₙ₋₁ * Aₙ₋₁ + aₙ₋₁ * Aₙ₋₂`, where `predA` is `Aₙ₋₁`,
`ppredA` is `Aₙ₋₂`, `a` is `aₙ₋₁`, and `b` is `bₙ₋₁`.
-/
def next_numerator (a b ppredA predA : K) : K := b * predA + a * ppredA

/--
Returns the next denominator `Bₙ = bₙ₋₁ * Bₙ₋₁ + aₙ₋₁ * Bₙ₋₂``, where `predB` is `Bₙ₋₁` and
`ppredB` is `Bₙ₋₂`, `a` is `aₙ₋₁`, and `b` is `bₙ₋₁`.
-/
def next_denominator (aₙ bₙ ppredB predB : K) : K := bₙ * predB + aₙ * ppredB

/--
Returns the next continuants `⟨Aₙ, Bₙ⟩` using `next_numerator` and `next_denominator`, where `pred`
is `⟨Aₙ₋₁, Bₙ₋₁⟩`, `ppred` is `⟨Aₙ₋₂, Bₙ₋₂⟩`, `a` is `aₙ₋₁`, and `b` is `bₙ₋₁`.
-/
def next_continuants (a b : K) (ppred pred : gcf.pair K) : gcf.pair K :=
⟨next_numerator a b ppred.a pred.a, next_denominator a b ppred.b pred.b⟩

/-- Returns the continuants `⟨Aₙ₋₁, Bₙ₋₁⟩` of `g`. -/
def continuants_aux (g : gcf K) : stream (gcf.pair K)
| 0 := ⟨1, 0⟩
| 1 := ⟨g.h, 1⟩
| (n + 2) :=
  match g.s.nth n with
  | none := continuants_aux (n + 1)
  | some gp := next_continuants gp.a gp.b (continuants_aux n) (continuants_aux $ n + 1)
  end

/-- Returns the continuants `⟨Aₙ, Bₙ⟩` of `g`. -/
def continuants (g : gcf K) : stream (gcf.pair K) := g.continuants_aux.tail

/-- Returns the numerators `Aₙ` of `g`. -/
def numerators (g : gcf K) : stream K := g.continuants.map gcf.pair.a

/-- Returns the denominators `Bₙ` of `g`. -/
def denominators (g : gcf K) : stream K := g.continuants.map gcf.pair.b

/-- Returns the convergents `Aₙ / Bₙ` of `g`, where `Aₙ, Bₙ` are the nth continuants of `g`. -/
def convergents (g : gcf K) : stream K := λ (n : ℕ), (g.numerators n) / (g.denominators n)

/--
Returns the approximation of the fraction described by the given sequence up to a given position n.
For example, `convergents'_aux [(1, 2), (3, 4), (5, 6)] 2 = 1 / (2 + 3 / 4)` and
`convergents'_aux [(1, 2), (3, 4), (5, 6)] 0 = 0`.
-/
def convergents'_aux : seq (gcf.pair K) → ℕ → K
| s 0 := 0
| s (n + 1) := match s.head with
  | none := 0
  | some gp := gp.a / (gp.b + convergents'_aux s.tail n)
  end

/--
Returns the convergents of `g` by evaluating the fraction described by `g` up to a given
position `n`. For example, `convergents' [9; (1, 2), (3, 4), (5, 6)] 2 = 9 + 1 / (2 + 3 / 4)` and
`convergents' [9; (1, 2), (3, 4), (5, 6)] 0 = 9`
-/
def convergents' (g : gcf K) (n : ℕ) : K := g.h + convergents'_aux g.s n

end generalized_continued_fraction

-- Now, some basic, general theorems
namespace generalized_continued_fraction
open generalized_continued_fraction as gcf

/-- Two gcfs `g` and `g'` are equal if and only if their components are equal. -/
protected lemma ext_iff {g g' : gcf α} : g = g' ↔ g.h = g'.h ∧ g.s = g'.s :=
by { cases g, cases g', simp }

@[ext]
protected lemma ext {g g' : gcf α} (hyp : g.h = g'.h ∧ g.s = g'.s) : g = g' :=
generalized_continued_fraction.ext_iff.elim_right hyp

end generalized_continued_fraction
