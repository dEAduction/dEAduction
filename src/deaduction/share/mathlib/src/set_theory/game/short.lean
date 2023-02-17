/-
Copyright (c) 2019 Scott Morrison. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Scott Morrison
-/
import set_theory.game
import data.fintype.basic

/-!
# Short games

A combinatorial game is `short` [Conway, ch.9][conway2001] if it has only finitely many positions.
In particular, this means there is a finite set of moves at every point.

We prove that the order relations `≤` and `<`, and the equivalence relation `≈`, are decidable on
short games, although unfortunately in practice `dec_trivial` doesn't seem to be able to
prove anything using these instances.
-/
universes u

namespace pgame

/-- A short game is a game with a finite set of moves at every turn. -/
inductive short : pgame.{u} → Type (u+1)
| mk : Π {α β : Type u} {L : α → pgame.{u}} {R : β → pgame.{u}}
         (sL : ∀ i : α, short (L i)) (sR : ∀ j : β, short (R j))
         [fintype α] [fintype β],
       short ⟨α, β, L, R⟩

instance subsingleton_short : Π (x : pgame), subsingleton (short x)
| (mk xl xr xL xR) :=
⟨λ a b, begin
  cases a, cases b,
  congr,
  { funext,
    apply @subsingleton.elim _ (subsingleton_short (xL x)) },
  { funext,
    apply @subsingleton.elim _ (subsingleton_short (xR x)) },
end⟩
using_well_founded { dec_tac := pgame_wf_tac }

/-- A synonym for `short.mk` that specifies the pgame in an implicit argument. -/
def short.mk' {x : pgame} [fintype x.left_moves] [fintype x.right_moves]
  (sL : ∀ i : x.left_moves, short (x.move_left i))
  (sR : ∀ j : x.right_moves, short (x.move_right j)) :
  short x :=
by unfreezingI { cases x, dsimp at * }; exact short.mk sL sR

attribute [class] short

/--
Extracting the `fintype` instance for the indexing type for Left's moves in a short game.
This is an unindexed typeclass, so it can't be made a global instance.
-/
def fintype_left {α β : Type u} {L : α → pgame.{u}} {R : β → pgame.{u}} [S : short ⟨α, β, L, R⟩] :
  fintype α :=
by { casesI S with _ _ _ _ _ _ F _, exact F }
local attribute [instance] fintype_left
instance fintype_left_moves (x : pgame) [S : short x] : fintype (x.left_moves) :=
by { casesI x, dsimp, apply_instance }
/--
Extracting the `fintype` instance for the indexing type for Right's moves in a short game.
This is an unindexed typeclass, so it can't be made a global instance.
-/
def fintype_right {α β : Type u} {L : α → pgame.{u}} {R : β → pgame.{u}} [S : short ⟨α, β, L, R⟩] :
  fintype β :=
by { casesI S with _ _ _ _ _ _ _ F, exact F }
local attribute [instance] fintype_right
instance fintype_right_moves (x : pgame) [S : short x] : fintype (x.right_moves) :=
by { casesI x, dsimp, apply_instance }

instance move_left_short (x : pgame) [S : short x] (i : x.left_moves) : short (x.move_left i) :=
by { casesI S with _ _ _ _ L _ _ _, apply L }
/--
Extracting the `short` instance for a move by Left.
This would be a dangerous instance potentially introducing new metavariables
in typeclass search, so we only make it an instance locally.
-/
def move_left_short' {xl xr} (xL xR) [S : short (mk xl xr xL xR)] (i : xl) : short (xL i) :=
by { casesI S with _ _ _ _ L _ _ _, apply L }
local attribute [instance] move_left_short'
instance move_right_short (x : pgame) [S : short x] (j : x.right_moves) : short (x.move_right j) :=
by { casesI S with _ _ _ _ _ R _ _, apply R }
/--
Extracting the `short` instance for a move by Right.
This would be a dangerous instance potentially introducing new metavariables
in typeclass search, so we only make it an instance locally.
-/
def move_right_short' {xl xr} (xL xR) [S : short (mk xl xr xL xR)] (j : xr) : short (xR j) :=
by { casesI S with _ _ _ _ _ R _ _, apply R }
local attribute [instance] move_right_short'

instance short.of_pempty {xL} {xR} : short (mk pempty pempty xL xR) :=
short.mk (λ i, pempty.elim i) (λ j, pempty.elim j)

instance short_0 : short 0 :=
short.mk (λ i, by cases i) (λ j, by cases j)

instance short_1 : short 1 :=
short.mk (λ i, begin cases i, apply_instance, end) (λ j, by cases j)

/-- Evidence that every `pgame` in a list is `short`. -/
inductive list_short : list pgame.{u} → Type (u+1)
| nil : list_short []
| cons : Π (hd : pgame.{u}) [short hd] (tl : list pgame.{u}) [list_short tl], list_short (hd :: tl)

attribute [class] list_short
attribute [instance] list_short.nil list_short.cons

instance list_short_nth_le : Π (L : list pgame.{u}) [list_short L] (i : fin (list.length L)),
  short (list.nth_le L (i.val) i.is_lt)
| [] _ n := begin exfalso, rcases n with ⟨_, ⟨⟩⟩, end
| (hd :: tl) (@list_short.cons _ S _ _) ⟨0, _⟩ := S
| (hd :: tl) (@list_short.cons _ _ _ S) ⟨n+1, h⟩ :=
  @list_short_nth_le tl S ⟨n, (add_lt_add_iff_right 1).mp h⟩

instance short_of_lists : Π (L R : list pgame) [list_short L] [list_short R],
  short (pgame.of_lists L R)
| L R _ _ := by { resetI, apply short.mk; { intros, apply_instance } }

/-- If `x` is a short game, and `y` is a relabelling of `x`, then `y` is also short. -/
def short_of_relabelling : Π {x y : pgame.{u}} (R : relabelling x y) (S : short x), short y
| x y ⟨L, R, rL, rR⟩ S :=
begin
  resetI,
  haveI := (fintype.of_equiv _ L),
  haveI := (fintype.of_equiv _ R),
  exact short.mk'
    (λ i, by { rw ←(L.right_inv i), apply short_of_relabelling (rL (L.symm i)) infer_instance, })
    (λ j, short_of_relabelling (rR j) infer_instance)
end

/-- If `x` has no left move or right moves, it is (very!) short. -/
def short_of_equiv_empty {x : pgame.{u}}
  (el : x.left_moves ≃ pempty) (er : x.right_moves ≃ pempty) : short x :=
short_of_relabelling (relabel_relabelling el er).symm short.of_pempty

instance short_neg : Π (x : pgame.{u}) [short x], short (-x)
| (mk xl xr xL xR) _ :=
begin
  resetI,
  apply short.mk,
  { rintro i,
    apply short_neg _,
    apply_instance, },
  { rintro j,
    apply short_neg _,
    apply_instance, }
end
using_well_founded { dec_tac := pgame_wf_tac }

instance short_add : Π (x y : pgame.{u}) [short x] [short y], short (x + y)
| (mk xl xr xL xR) (mk yl yr yL yR) _ _ :=
begin
  resetI,
  apply short.mk,
  { rintro ⟨i⟩,
    { apply short_add, },
    { change short (mk xl xr xL xR + yL i), apply short_add, } },
  { rintro ⟨j⟩,
    { apply short_add, },
    { change short (mk xl xr xL xR + yR j), apply short_add, } },
end
using_well_founded { dec_tac := pgame_wf_tac }

instance short_nat : Π n : ℕ, short n
| 0 := pgame.short_0
| (n+1) := @pgame.short_add _ _ (short_nat n) pgame.short_1

instance short_bit0 (x : pgame.{u}) [short x] : short (bit0 x) :=
by { dsimp [bit0], apply_instance }
instance short_bit1 (x : pgame.{u}) [short x] : short (bit1 x) :=
by { dsimp [bit1], apply_instance }

/--
Auxiliary construction of decidability instances.
We build `decidable (x ≤ y)` and `decidable (x < y)` in a simultaneous induction.
Instances for the two projections separately are provided below.
-/
def le_lt_decidable : Π (x y : pgame.{u}) [short x] [short y], decidable (x ≤ y) × decidable (x < y)
| (mk xl xr xL xR) (mk yl yr yL yR) shortx shorty :=
begin
  resetI,
  split,
  { apply @and.decidable _ _ _ _,
    { apply @fintype.decidable_forall_fintype xl _ _ (by apply_instance),
      intro i,
      apply (@le_lt_decidable _ _ _ _).2; apply_instance, },
    { apply @fintype.decidable_forall_fintype yr _ _ (by apply_instance),
      intro i,
      apply (@le_lt_decidable _ _ _ _).2; apply_instance, }, },
  { apply @or.decidable _ _ _ _,
    { apply @fintype.decidable_exists_fintype yl _ _ (by apply_instance),
      intro i,
      apply (@le_lt_decidable _ _ _ _).1; apply_instance, },
    { apply @fintype.decidable_exists_fintype xr _ _ (by apply_instance),
      intro i,
      apply (@le_lt_decidable _ _ _ _).1; apply_instance, }, },
end
using_well_founded { dec_tac := pgame_wf_tac }

instance le_decidable (x y : pgame.{u}) [short x] [short y] : decidable (x ≤ y) :=
(le_lt_decidable x y).1

instance lt_decidable (x y : pgame.{u}) [short x] [short y] : decidable (x < y) :=
(le_lt_decidable x y).2

instance equiv_decidable (x y : pgame.{u}) [short x] [short y] : decidable (x ≈ y) :=
and.decidable

example : short 0 := by apply_instance
example : short 1 := by apply_instance
example : short 2 := by apply_instance
example : short (-2) := by apply_instance

example : short (of_lists [0] [1]) := by apply_instance
example : short (of_lists [-2, -1] [1]) := by apply_instance

example : short (0 + 0) := by apply_instance

example : decidable ((1 : pgame) ≤ 1) := by apply_instance

example : (0 : pgame) ≤ 0 := dec_trivial
example : (1 : pgame) ≤ 1 := dec_trivial

end pgame
