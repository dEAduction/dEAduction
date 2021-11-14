-----------
-- Logic --
-----------

notation [parsing_only] P ` and ` Q := P ∧ Q
notation [parsing_only]  P ` or ` Q := P ∨ Q
notation [parsing_only]  ` not ` P := ¬ P
notation [parsing_only]  P ` implies ` Q := P → Q
notation [parsing_only]  P ` iff ` Q := P ↔ Q

-- French
notation [parsing_only] P ` et ` Q := P ∧ Q
notation [parsing_only]  P ` ou ` Q := P ∨ Q
notation [parsing_only]  ` non ` P := ¬ P
notation [parsing_only]  P ` implique ` Q := P → Q
notation [parsing_only]  P ` ssi ` Q := P ↔ Q


----------------
-- Set theory --
----------------

-- notation [parsing_only]  x ` in ` A := x ∈ A Does not work: 'in' is a key word
notation [parsing_only]  A ` cap ` B := A ∩ B
notation [parsing_only]  A ` cup ` B := A ∪ B
notation [parsing_only]  A ` subset ` B := A ⊆ B
notation [parsing_only]  `emptyset` := ∅
notation [parsing_only]  `vide` := ∅

notation [parsing_only]  x ` dans ` A := x ∈ A
notation [parsing_only]  x ` belongs ` A := x ∈ A
notation [parsing_only]  x ` appartient ` A := x ∈ A

notation [parsing_only]  A ` inter ` B := A ∩ B
notation [parsing_only]  A ` intersection ` B := A ∩ B
notation [parsing_only]  A ` union ` B := A ∪ B
notation [parsing_only]  A ` inclus ` B := A ⊆ B

-- notation f `⟮` A `⟯` := set.image f  A  Does not work?
-- notation f `⁻¹⟮` A `⟯` := set.preimage f  A
notation [parsing_only] f `inverse_image` A := set.preimage f  A
notation [parsing_only] f `direct_image` A := set.image f  A
notation [parsing_only] f `image_reciproque` A := set.preimage f  A
notation [parsing_only] f `image_directe` A := set.image f  A
-- notation g `∘` f := set.composition g f

definition sing {X: Type} (x: X) := ({x}: set X)
definition paire {X: Type} (x x': X) := ({x, x'}: set X)