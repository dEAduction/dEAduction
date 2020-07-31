import data.set
import tactic

-- dEAduction imports
import logics
import definitions
import definitions_theorie_des_ensembles
import structures


local attribute [instance] classical.prop_decidable



lemma definition.iff {P Q : Prop} : ( P ↔ Q ) ↔ (P → Q) ∧ (Q → P) := 
iff_def

namespace theorie_des_ensembles

variable {X : Type}

lemma definition.inclusion (A B : set X) : A ⊆ B ↔ ∀ {{x:X}}, x ∈ A → x ∈ B :=
iff.rfl

lemma definition.egalite_deux_ensembles {A A' : set X} : (A = A') ↔ ( ∀ x, x ∈ A ↔ x ∈ A' ) :=
/- dEAduction
PrettyName
    egalité de deux ensembles
-/
by exact set.ext_iff

lemma theorem.double_inclusion {A A' : set X} : (A ⊆ A' ∧ A' ⊆ A) → A = A' :=
/- dEAduction
PrettyName
    Double inclusion
-/
begin
    exact set.subset.antisymm_iff.mpr
end


-----------------------------------------
--------------- section 1 ---------------
namespace unions_et_intersections
-----------------------------------------
-----------------------------------------

variables {A B C : set X}


lemma definition.intersection_deux_ensembles (A B : set X) (x : X) :  x ∈ A ∩ B ↔ ( x ∈ A ∧ x ∈ B) :=
iff.rfl
/- dEAduction
PrettyName
    Intersection de deux ensembles
-/

lemma definition.intersection_quelconque_ensembles (I : Type) (O : I → set X)  (x : X) : (x ∈ set.Inter O) ↔ (∀ i:I, x ∈ O i) :=
set.mem_Inter
/- dEAduction
PrettyName
    Intersection d'une famille d'ensembles quelconque
-/

lemma definition.union_deux_ensembles  (A : set X) (B : set X) (x : X) :  x ∈ A ∪ B ↔ ( x ∈ A ∨ x ∈ B) :=
iff.rfl
/- dEAduction
PrettyName
    Union de deux ensembles
-/

lemma definition.union_quelconque_ensembles (I : Type) (O : I → set X)  (x : X) : (x ∈ set.Union O) ↔ (∃ i:I, x ∈ O i) :=
set.mem_Union
/- dEAduction
PrettyName
    Union d'une famille d'ensembles quelconque
-/



lemma exercise.union_distributive_inter : A ∩ (B ∪ C)  = (A ∩ B) ∪ (A ∩ C) := 
/- dEAduction
PrettyName
    Intersection d'une union
Description
    L'intersection est distributive par rapport à l'union
Tools->Logic
    $ALL -negate
Tools->ProofTechniques
    $ALL -contradiction
Tools->Definitions
    $UNTIL_NOW
Tools->Theorems
    double_inclusion
ExpectedVarsNumber
    X=3, A=1, B=1
-/

begin
    sorry
end

set_option pp.all
lemma exercise.inter_distributive_union : A ∪ (B ∩ C)  = (A ∪ B) ∩ (A ∪ C) := 
/- dEAduction
PrettyName
    
Description
    
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
Tools->Definitions
    $UNTIL_NOW
Tools->Theorems
    $ALL   
-/

begin
    sorry
end

end unions_et_intersections

-----------------------------------------
-----------------------------------------
section complementaire -- sous-section 2
-----------------------------------------
-----------------------------------------
variables  {A B : set X}
variables {I : Type} {E F : I → set X}
notation A`ᶜ` := set.compl A 

lemma definition.complement {A : set X} {x : X} : x ∈ set.compl A ↔ x ∉ A := 
/- dEAduction
PrettyName
    Complémentaire
-/
by finish

lemma definition.difference_symetrique {A B : set X} {x : X} : x ∈ B \ A ↔ (x ∈ B ∧ x ∉ A) :=
/- dEAduction
PrettyName
    Différence symétrique
-/
iff.rfl


lemma complement_complement : (set.compl (set.compl A)) =A :=
/- dEAduction
PrettyName
    Complémentaire du complémentaire    
Description
    Tout ensemble est égal au complémentaire de son complémentaire    
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
Tools->Definitions
    $UNTIL_NOW
Tools->Theorems
    $ALL   
-/
begin
    hypo_analysis,
    targets_analysis,
    sorry
end

lemma complement_union_deux : set.compl (A ∪ B) = (set.compl A) ∩ (set.compl B) :=
/- dEAduction
PrettyName
    Complémentaire d'union I
Description
    Le complémentaire de l'union de deux ensembles égale l'intersection des complémentaires 
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
Tools->Definitions
    $UNTIL_NOW
Tools->Theorems
    $ALL   
-/
begin    
    sorry
end



open set
-- set_option pp.all true
lemma exercise.complement_union_quelconque  (H : ∀ i, F i = set.compl (E i)) : set.compl (Union E) = Inter F :=
/- dEAduction
PrettyName
    Complémentaire d'union II    
Description
    Le complémentaire d'une réunion quelconque égale l'intersection des complémentaires     
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
Tools->Definitions
    $UNTIL_NOW
Tools->Theorems
    $ALL   
-/
begin
    sorry
end

lemma complement_intersection_quelconque  (H : ∀ i, F i = set.compl (E i)) : set.compl (Inter E) = Union F :=
/- dEAduction
PrettyName
    
Description
    Le complémentaire d'une intersection quelconque égale l'union des complémentaires    
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
Tools->Definitions
    $UNTIL_NOW
Tools->Theorems
    $ALL   
-/
begin   
    sorry
end


/- Le complémentaire du vide est X ??? -/ 



lemma inclus_ssi_complement_contient : A ⊆ B ↔ set.compl B ⊆ set.compl A :=
/- dEAduction
PrettyName
    
Description
    A est inclus dans B ssi le complémentaire de A contient le complémentaire de B    
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
Tools->Definitions
    $UNTIL_NOW
Tools->Theorems
    $ALL   
-/

begin
    defi double_implication,
        ET, 
        implique,
        defi inclusion, qqs a, implique, 
        defi complement,
        by_contradiction,
        -- alternative : defi inclusion at H, qqselim H a, impliqueelim H_2 a_1,
        applique H a_1,
        -- alternative : tautology, -- le contexte contient P et non P
        applique H_1 H_2, assumption,
    implique,
    defi inclusion, qqs a, implique,
    by_contradiction,
    applique H a_1,
    applique H_2 H_1, assumption,
    -- alternative :  defi inclusion at H, qqselim H a, impliqueelim H_3 H_2,
    -- tautology -- a remplacer : trop puissant !
end


/- -/
example : A ⊆ B ↔ B \ A = ∅ :=
begin
    split,
    intro H,

end

-- Comment manipuler l'ensemble vide dans un type ?

/- Autres : différence symétrique-/




end complementaire



-- Ajouter : 3. produit cartésien, 4. relations ?
-- comment définit-on un produit cartésien d'ensembles ?



-----------------------------------------
-----------------------------------------
section applications  -- sous-section 5
-----------------------------------------
-----------------------------------------
notation f `⟮` A `⟯` := f '' A
notation f `⁻¹⟮` A `⟯` := f  ⁻¹' A

variables  (A A': set X) 
variables {Y: Type} {f: X → Y} (B B': set Y)
variables {I : Type} {E : I → set X} {F : I → set Y}

lemma exercise.image_de_reciproque : f '' (f ⁻¹' B)  ⊆ B :=
/- dEAduction
PrettyName
    
Description
    
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
Tools->Definitions
    $UNTIL_NOW
Tools->Theorems
    $ALL   
-/
begin
    hypo_analysis,
    goals_analysis,
    sorry
end

lemma exercise.reciproque_de_image : A ⊆ f ⁻¹' (f '' A) :=
/- dEAduction
PrettyName
    
Description
    
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
Tools->Definitions
    $UNTIL_NOW
Tools->Theorems
    $ALL   
-/
begin
    intros x H,
end

lemma exercise.image_reciproque_inter :  f ⁻¹'  (B∩B') = f ⁻¹'  (B) ∩ f ⁻¹'  (B') :=
/- dEAduction
PrettyName
    
Description
    
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
Tools->Definitions
    $UNTIL_NOW
Tools->Theorems
    $ALL   
-/
begin
    sorry
end


lemma  image_reciproque_union  : f ⁻¹' (B ∪ B') = f ⁻¹' B ∪ f ⁻¹' B'  :=
/- dEAduction
PrettyName
    
Description
    
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
Tools->Definitions
    $UNTIL_NOW
Tools->Theorems
    $ALL   
-/
begin
    defi double_inclusion,
    ET,
        defi inclusion,
        hypo_analysis,
        goals_analysis,
        qqs x,
        assumption,
        implique,
        hypo_analysis,
        goals_analysis,
        defi image_reciproque at H,
        hypo_analysis,
        defi union,
        defi union at H,
        OU H,
        defi image_reciproque at HA,
        OUd HA (f x ∈ B),
            OU gauche, assumption,
        OU droite, assumption, 
-- ici assumption en fait un peu trop, 
-- on voudrait obliger à avoir appliqué la def de l'image réciproque avant
    defi inclusion, 
    qqs x,
    implique,
    defi image_reciproque,
    defi union,
    defi union at H,
    OU H,
        OU gauche, assumption,
    OU droite, assumption,
end


/- Idem union, intersection quelconques -/

lemma image_reciproque_inter_quelconque  (H : ∀ i:I,  (E i = f ⁻¹' (F i))) :  (f ⁻¹'  (set.Inter F)) = set.Inter E :=
/- dEAduction
PrettyName
    
Description
    
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
Tools->Definitions
    $UNTIL_NOW
Tools->Theorems
    $ALL   
-/
begin
    hypo_analysis,
    targets_analysis,
    defi double_inclusion, ET,
    {defi inclusion, qqs x,
    implique,
    defi image_reciproque at H_1,
    defi intersection_quelconque at H_1,
    defi intersection_quelconque,
    qqs i,
    applique H_1 i,
    defi image_reciproque at H_2,
    applique H i,
    rw ← H_3 at H_2,
    assumption},
    {




    }
end



lemma image_inter_inclus_inter_images   :  
        f '' (A∩A') ⊆ f '' (A) ∩ f '' (A') :=
/- dEAduction
PrettyName
    
Description
    
Tools->Logic
    $ALL
Tools->ProofTechniques
    $ALL
Tools->Definitions
    $UNTIL_NOW
Tools->Theorems
    $ALL   
-/
begin
    -- Soit b un élément de  f(A'∩A)
    defi inclusion,
    qqsintro b,
    impliqueintro,
    -- ligne non indispensable :
    defi image at H,
    hypo_analysis,
    goals_analysis,
    existeelim a H, ET H,
    defi intersection_deux at HA, ET HA,
    defi intersection_deux, ET,
    defi image,
    existeintro a, ET,
    assumption, assumption,
    existeintro a, ET,
    assumption, assumption,
end


/- L'image réciproque du complémentaire 
égale le complémentaire de l'image réciprqque-/


end applications





end theorie_des_ensembles

