

namespace induction

open nat 
lemma simple_induction {P: nat → Prop} (HR0: P 0)
(HR1: ∀ n, (P n → P (n+1) )) :
∀n, P n
:=
begin
  intro n, induction n with n Hn, assumption,
  exact HR1 n Hn, 
end 

theorem two_step_induction {P : ℕ → Prop} (HR0 : P 0) (HR1 : P 1)
(HR2 : ∀ n, (P n ∧ P (n+1) → P (n+2))) :
∀n, P n :=
-- | 0               := HR0
-- | 1               := HR1
-- | (succ (succ n)) := HR2 n ⟨two_step_induction n, two_step_induction (n+1)⟩
begin
  sorry
end

theorem strong_induction {P : ℕ → Prop} (HR0 : P 0)
(HR2 : ∀ n, ( (∀ k < n, P k) → P n)) :
∀n, P n :=
begin
  sorry
end

end induction
