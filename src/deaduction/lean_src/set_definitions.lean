namespace set

def injective {X Y : Type} (f₀ : X → Y) := ∀ x y : X, (f₀ x = f₀ y → x = y)
def surjective {X Y : Type} (f₀ : X → Y) := ∀ y : Y, ∃ x : X, y = f₀ x
def bijective {X Y : Type} (f₀ : X → Y) := ∀ y : Y, ∃! x : X, y = f₀ x
def composition {X Y Z : Type} (g₀ : Y → Z) (f₀ : X → Y) := λx:X, g₀ (f₀ x)
def Identite {X : Type} := λ x:X, x
def sing {X: Type} (x: X) := ({x}: set X)
def pair {X: Type} (x x': X) := ({x, x'}: set X)

-- def set_family (I X : Type) := I → set X  -- defined in parser_analysis_definitions
-- def index_set := Type


def symmetric_difference {X : Type} (A B : set X) := (A ∪ B) \ (A ∩ B)

notation A `Δ` B := symmetric_difference A B
notation `∁`A := set.compl A
notation `∃!` P := exists_unique P
notation [parsing_only] P ` and ` Q := P ∧ Q
notation [parsing_only]  P ` or ` Q := P ∨ Q
notation [parsing_only]  ` not ` P := ¬ P
-- The set difference is denoted \, as in 'A \ B'

end set