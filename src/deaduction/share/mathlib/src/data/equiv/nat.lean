/-
Copyright (c) 2018 Mario Carneiro. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Author: Mario Carneiro

Additional facts about equiv and encodable using the
pairing function on nat.
-/
import data.nat.pairing
import data.pnat.basic

open nat

namespace equiv

@[simp] def nat_prod_nat_equiv_nat : ℕ × ℕ ≃ ℕ :=
⟨λ p, nat.mkpair p.1 p.2,
 nat.unpair,
 λ p, begin cases p, apply nat.unpair_mkpair end,
 nat.mkpair_unpair⟩

@[simp] def bool_prod_nat_equiv_nat : bool × ℕ ≃ ℕ :=
⟨λ ⟨b, n⟩, bit b n, bodd_div2,
 λ ⟨b, n⟩, by simp [bool_prod_nat_equiv_nat._match_1, bodd_bit, div2_bit],
 λ n, by simp [bool_prod_nat_equiv_nat._match_1, bit_decomp]⟩

@[simp] def nat_sum_nat_equiv_nat : ℕ ⊕ ℕ ≃ ℕ :=
(bool_prod_equiv_sum ℕ).symm.trans bool_prod_nat_equiv_nat

def int_equiv_nat : ℤ ≃ ℕ :=
int_equiv_nat_sum_nat.trans nat_sum_nat_equiv_nat

def prod_equiv_of_equiv_nat {α : Sort*} (e : α ≃ ℕ) : α × α ≃ α :=
calc α × α ≃ ℕ × ℕ : prod_congr e e
      ...  ≃ ℕ     : nat_prod_nat_equiv_nat
      ...  ≃ α     : e.symm

def pnat_equiv_nat : ℕ+ ≃ ℕ :=
⟨λ n, pred n.1, succ_pnat,
  λ ⟨n, h⟩, by { cases n, cases h, simp [succ_pnat, h] }, λ n, by simp [succ_pnat] ⟩


end equiv
