namespace set

def symmetric_difference {X : Type} (A B : set X) := (A ∪ B) \ (A ∩ B)
notation A `Δ` B := symmetric_difference A B

def injective {X Y : Type} (f₀ : X → Y) := ∀ x y : X, (f₀ x = f₀ y → x = y)
def surjective {X Y : Type} (f₀ : X → Y) := ∀ y : Y, ∃ x : X, y = f₀ x
def bijective {X Y : Type} (f₀ : X → Y) := ∀ y : Y, ∃! x : X, y = f₀ x
def composition {X Y Z : Type} (g₀ : Y → Z) (f₀ : X → Y) := λx:X, g₀ (f₀ x)
def Identite {X : Type} := λ x:X, x

notation g `∘` f := composition g f
notation `∁`A := set.compl A

end set