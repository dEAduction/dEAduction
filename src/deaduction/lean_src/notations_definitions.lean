


/-
notation [parsing_only] P ` \and ` Q := P ∧ Q
notation [parsing_only]  P ` \or ` Q := P ∨ Q
notation [parsing_only]  ` \not ` P := ¬ P
notation [parsing_only]  P ` \implies ` Q := P → Q
notation [parsing_only]  P ` \iff ` Q := P ↔ Q

notation [parsing_only]  x ` \in ` A := x ∈ A
notation [parsing_only]  A ` \cap ` B := A ∩ B
notation [parsing_only]  A ` \cup ` B := A ∪ B
notation [parsing_only]  A ` \subset ` B := A ⊆ B
notation [parsing_only]  `\emptyset` := ∅
-/

namespace set
def symmetric_difference {X : Type} (A B : set X) := (A ∪ B) \ (A ∩ B)
notation A `Δ` B := symmetric_difference A B

def injective {X Y : Type} (f₀ : X → Y) := ∀ x y : X, (f₀ x = f₀ y → x = y)
def surjective {X Y : Type} (f₀ : X → Y) := ∀ y : Y, ∃ x : X, f₀ x = y
def composition {X Y Z : Type} (g₀ : Y → Z) (f₀ : X → Y) := λx:X, g₀ (f₀ x)
def Identite {X : Type} := λ x:X, x
notation g `∘` f := composition g f

notation `∁`A := set.compl A

/-
notation f `⟮` A `⟯` := f '' A
notation f `⁻¹⟮` A `⟯` := f  ⁻¹' A
-/
end set