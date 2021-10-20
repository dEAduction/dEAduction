namespace set

def symmetric_difference {X : Type} (A B : set X) := (A ∪ B) \ (A ∩ B)
notation A `Δ` B := symmetric_difference A B

def injective {X Y : Type} (f₀ : X → Y) := ∀ x y : X, (f₀ x = f₀ y → x = y)
def surjective {X Y : Type} (f₀ : X → Y) := ∀ y : Y, ∃ x : X, y = f₀ x
def bijective {X Y : Type} (f₀ : X → Y) := ∀ y : Y, ∃! x : X, y = f₀ x
def composition {X Y Z : Type} (g₀ : Y → Z) (f₀ : X → Y) := λx:X, g₀ (f₀ x)
def Identite {X : Type} := λ x:X, x

def set_family (I X : Type) := I → set X
def index_set := Type

notation g `∘` f := composition g f
notation `∁`A := set.compl A

end set

notation [parsing_only] P ` and ` Q := P ∧ Q
notation [parsing_only]  P ` or ` Q := P ∨ Q
notation [parsing_only]  ` not ` P := ¬ P
notation [parsing_only]  P ` implies ` Q := P → Q
notation [parsing_only]  P ` iff ` Q := P ↔ Q

notation [parsing_only]  x ` in ` A := x ∈ A
notation [parsing_only]  A ` cap ` B := A ∩ B
notation [parsing_only]  A ` cup ` B := A ∪ B
notation [parsing_only]  A ` subset ` B := A ⊆ B
notation [parsing_only]  `emptyset` := ∅

notation [parsing_only] P ` et ` Q := P ∧ Q
notation [parsing_only]  P ` ou ` Q := P ∨ Q
notation [parsing_only]  ` non ` P := ¬ P
notation [parsing_only]  P ` implique ` Q := P → Q
notation [parsing_only]  P ` ssi ` Q := P ↔ Q

notation [parsing_only]  x ` dans ` A := x ∈ A
notation [parsing_only]  x ` appartient ` A := x ∈ A
notation [parsing_only]  A ` inter ` B := A ∩ B
notation [parsing_only]  A ` intersection ` B := A ∩ B
notation [parsing_only]  A ` union ` B := A ∪ B
notation [parsing_only]  A ` inclus ` B := A ⊆ B
notation [parsing_only]  `vide` := ∅

notation f `⟮` A `⟯` := set.image f  A
notation f `⁻¹⟮` A `⟯` := set.preimage f  A
notation [parsing_only] f `inverse` A := set.preimage f  A
notation g `∘` f := set.composition g f
notation `∃!` P := exists_unique P
