import tactic
import structures2
import notations_definitions
import utils

/- dEAduction
Title
    Ensembles et applications
Institution
    Université du monde
AvailableProof
    use_proof_methods apply
AvailableMagic
    assumption
AvailableExercises
  UNTIL_NOW -image_directe_et_inclusion_II -image_reciproque_et_inclusion_II -image_directe_et_intersection_II
-/

local attribute [instance] classical.prop_decidable
---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course
parameters {X Y Z: Type}

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
notation f `⟮` A `⟯` := f '' A
notation f `⁻¹⟮` A `⟯` := f  ⁻¹' A
notation [parsing_only] f `inverse` A := f  ⁻¹' A
notation g `∘` f := set.composition g f
notation `∃!` P := exists_unique P

open set

------------------
-- COURSE TITLE --
------------------
namespace ensembles_et_applications
/- dEAduction
PrettyName
    Ensembles et applications
-/

namespace definitions
/- dEAduction
PrettyName
    Définitions
-/

namespace generalites
/- dEAduction
PrettyName
    Généralités
-/

lemma definition.inclusion {A B : set X} : A ⊆ B ↔ ∀ {x:X}, x ∈ A → x ∈ B :=
/- dEAduction
AutoSteps
  ∀, →
-/
begin
    exact iff.rfl
end

lemma definition.egalite_deux_ensembles {A A' : set X} :
(A = A') ↔ ( ∀ x, x ∈ A ↔ x ∈ A' ) :=
/- dEAduction
PrettyName
    Egalité de deux ensembles
-/
begin
     exact set.ext_iff
end

lemma theorem.double_inclusion (A A' : set X) :
(A ⊆ A' ∧ A' ⊆ A) → A = A' :=
/- dEAduction
PrettyName
    Egalité de deux ensembles : double inclusion
-/
begin
    exact set.subset.antisymm_iff.mpr
end

lemma definition.ensemble_vide
{A: set X} :
(A = ∅) ↔ ∀ x : X, x ∉ A
:=
begin
    exact eq_empty_iff_forall_not_mem,
end

lemma theorem.ensemble_non_vide
(A: set X) :
(A ≠ ∅) ↔ ∃ x : X, x ∈ A
:=
begin
    sorry
end

end generalites

---------------
-- SECTION 1 --
---------------
namespace unions_et_intersections
-- variables unions_et_intersections --
variables {A B C : set X}

lemma definition.intersection_deux_ensembles {A B : set X} {x : X} :
x ∈ A ∩ B ↔ ( x ∈ A ∧ x ∈ B) :=
/- dEAduction
PrettyName
    Intersection de deux ensembles
-/
begin
    exact iff.rfl
end

lemma definition.union_deux_ensembles  {A : set X} {B : set X} {x : X} :
x ∈ A ∪ B ↔ ( x ∈ A ∨ x ∈ B) :=
/- dEAduction
PrettyName
    Union de deux ensembles
-/
begin
    exact iff.rfl
end

end unions_et_intersections


namespace applications

-- variables applications --

variables  {A A': set X}
variables {f: X → Y} {B B': set Y}

lemma definition.injectivite :
injective f ↔ ∀ x x' : X, (f x = f x' → x = x')
:=
/- dEAduction
PrettyName
    Application injective
-/
begin
    refl,
end

lemma definition.surjectivite :
surjective f ↔ ∀ y : Y, ∃ x : X, y = f x
:=
/- dEAduction
PrettyName
    Application surjective
-/
begin
    refl,
end

lemma definition.image_directe (y : Y) :
y ∈ f '' A ↔ ∃ x : X, x ∈ A ∧  f x = y
:=
begin
    sorry
end

lemma theorem.image_directe :
∀ f: X→Y, ∀{A: set X}, ∀{x: X},
 (x ∈ A → f x ∈ f '' A)
:=
begin
    sorry
end

lemma definition.image_reciproque (x:X) :
x ∈ f  ⁻¹' B ↔ f(x) ∈ B
:=
begin
    sorry
end

end applications

end definitions

-----------------
--- EXERCICES ---
-----------------
namespace exercices
variables  {A A': set X}
variables {f: X → Y} {B B': set Y}

/-
1. ∀A,B⊆E A⊆B⇒f(A)⊆f(B)
2. ∀A,B⊆E f(A)⊆f(B)⇒A⊆B
3. Sif estinjective,alors∀A,B⊆E f(A)⊆f(B)⇒A⊆B
4. f estinjectivesietseulementsi∀A,B⊆E f(A)⊆f(B)⇒A⊆B

5. ∀A,B⊆F A⊆B⇒f−1(A)⊆f−1(B)
6. ∀A,B⊆F f−1(A)⊆f−1(B)⇒A⊆B
7. Si f est surjective, alors ∀A,B ⊆ F f−1(A) ⊆ f−1(B) ⇒ A ⊆ B
8. festsurjectivesietseulementsi∀A,B⊆F f−1(A)⊆f−1(B)⇒A⊆B

9. ∀A ⊆ F f(f−1(A)) ⊆ A
10. ∀A ⊆ F A ⊆ f(f−1(A))
11. Si f est surjective, alors ∀A ⊆ F A ⊆ f(f−1(A))
12. f est surjective si et seulement si ∀A ⊆ F A = f(f−1(A))

13. ∀A ⊆ E A ⊆ f−1(f(A))
14. ∀A ⊆ E f−1(f(A)) ⊆ A
15. Si f est injective alors ∀A ⊆ E f−1(f(A)) ⊆ A
16. f est injective si et seulement si ∀A ⊆ E f−1(f(A)) = A

17. ∀A,B⊆E f(A∩B)⊆f(A)∩f(B)
18. ∀A,B⊆E f(A)∩f(B)⊆f(A∩B)
19. Sif estinjective,alors∀A,B⊆E f(A)∩f(B)⊆f(A∩B)
20. f estinjectivesietseulementsi∀A,B⊆E f(A)∩f(B)=f(A∩B)

21. ∀A,B⊆E 22.∀A,B⊆F 23.∀A,B⊆F
22. f(A∪B)=f(A)∪f(B)
23. f−1(A ∩ B) = f−1(A) ∩ f−1(B) f−1(A ∪ B) = f−1(A) ∪ f−1(B)
-/


---------------------------------
namespace image_directe
/- dEAduction
PrettyName
  Image directe et inclusion
-/


lemma exercise.image_directe_et_inclusion_I :
∀ A B: set X, A ⊆ B → f '' (A) ⊆ f '' (B)
:=
/- dEAduction
PrettyName
  Image directe et inclusion (i)
-/
begin
  sorry
end

lemma exercise.image_directe_et_inclusion_II :
∀ A B: set X,  f '' (A) ⊆ f '' (B) → A ⊆ B
:=
/- dEAduction
PrettyName
  Image directe et inclusion (ii)
-/
begin
  sorry
end

lemma exercise.image_directe_et_inclusion_III :
(injective f) →  (∀ A B: set X,  f '' (A) ⊆ f '' (B) → A ⊆ B)
:=
/- dEAduction
PrettyName
  Image directe et inclusion (iii)
-/
begin
  sorry
end

end image_directe



---------------------------------
namespace image_reciproque
/- dEAduction
PrettyName
  Image réciproque et inclusion
-/


lemma exercise.image_reciproque_et_inclusion_I :
∀ A' B': set Y, A'⊆B' → f ⁻¹' (A') ⊆ f ⁻¹' (B')
:=
/- dEAduction
PrettyName
  Image réciproque et inclusion (i)
-/
begin
  sorry
end

lemma exercise.image_reciproque_et_inclusion_II :
∀ A' B': set Y,  f ⁻¹' (A') ⊆ f ⁻¹' (B') → A' ⊆ B'
:=
/- dEAduction
PrettyName
  Image réciproque et inclusion (ii)
-/
begin
  sorry
end

lemma exercise.image_reciproque_et_inclusion_III :
(surjective f) → (∀ A' B': set Y,  f ⁻¹' (A') ⊆ f ⁻¹' (B') → A' ⊆ B')
:=
/- dEAduction
PrettyName
  Image réciproque et inclusion (iii)
-/
begin
  sorry
end

end image_reciproque


---------------------------------
namespace image_et_image_reciproque
/- dEAduction
PrettyName
  Image et image réciproque
-/

namespace inclusions

lemma exercise.image_de_image_reciproque :
∀ A' : set Y, f '' (f ⁻¹' (A')) ⊆ A'
:=
/- dEAduction
PrettyName
  Image de l'image réciproque
-/
begin
  sorry
end


lemma exercise.image_reciproque_de_image :
∀ A : set X, A ⊆ f ⁻¹' (f '' (A))
:=
/- dEAduction
PrettyName
  Image réciproque de l'image
-/
begin
  sorry
end

end inclusions



namespace inclusions_reciproques
/- dEAduction
PrettyName
  Inclusions réciproques
-/

lemma exercise.image_de_image_reciproque_bis :
(surjective f) → (∀ A' : set Y, A' ⊆ f '' (f ⁻¹' (A')))
:=
/- dEAduction
PrettyName
  Image de l'image réciproque : inclusion réciproque
-/
begin
  sorry
end

lemma exercise.image_reciproque_de_image_bis :
(injective f) → (∀ A : set X, f ⁻¹' (f '' (A)) ⊆ A)
:=
/- dEAduction
PrettyName
  Image réciproque de l'image : inclusion réciproque
-/
begin
  sorry
end

end inclusions_reciproques
end image_et_image_reciproque


namespace image_intersection
/- dEAduction
PrettyName
  Image de l'intersection
-/


lemma exercise.image_directe_et_intersection_I :
∀ A B: set X, f '' (A ∩ B) ⊆ f '' (A) ∩ f '' (B)
:=
/- dEAduction
PrettyName
  Image directe et intersection (i)
-/
begin
  sorry
end

lemma exercise.image_directe_et_intersection_II :
∀ A B: set X,  f '' (A) ∩ f '' (B) ⊆ f '' (A ∩ B)
:=
/- dEAduction
PrettyName
  Image directe et intersection (ii)
-/
begin
  sorry
end

lemma exercise.image_directe_et_intersection_III
(H : injective f) :
∀ A B: set X,  f '' (A) ∩ f '' (B) ⊆ f '' (A ∩ B)
:=
/- dEAduction
PrettyName
  Image directe et intersection (iii)
-/
begin
  sorry
end

end image_intersection



namespace egalites
/- dEAduction
PrettyName
  Autres formules
-/

lemma exercise.egalite_I :
∀ A B : set X, f '' ( A ∪ B) = f '' (A) ∪ f '' (B)
:=
/- dEAduction
PrettyName
  Image directe et union
-/
begin
  sorry
end

lemma exercise.egalite_II :
∀ A' B' : set Y, f ⁻¹' ( A' ∩ B') = f ⁻¹' (A') ∩ f ⁻¹' (B')
:=
/- dEAduction
PrettyName
  Image réciproque et intersection
-/
begin
  sorry
end

lemma exercise.egalite_III :
∀ A' B' : set Y, f ⁻¹' ( A' ∪ B') = f ⁻¹' (A') ∪ f ⁻¹' (B')
:=
/- dEAduction
PrettyName
  Image réciproque et union
-/
begin
  sorry
end


end egalites

end exercices

end ensembles_et_applications

end course


