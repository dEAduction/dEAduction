-- import data.set
import tactic
import data.real.basic



-- dEAduction imports
import structures2
import compute

-- import definitions
-- import notations_definitions

-- General principles :
-- Type should be defined as parameters, in order to be implicit everywhere
-- other parameters are implicit in definitions, i.e. defined using '{}' (e.g. {A : set X} )
-- but explicit everywhere else, i.e. defined using '()' (e.g. (A : set X) )
-- each definition must be an iff statement (since it will be called with 'rw' or 'symp_rw')



local attribute [instance] classical.prop_decidable

---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course

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

open set

------------------
-- COURSE TITLE --
------------------
namespace maths_approfondies
/- dEAduction
PrettyName
    1M003 : mathématiques approfondies
-/


namespace nombres_reels
/- dEAduction
PrettyName
    Chapitre 1 : Nombres réels
-/

namespace majorants_minorants
/- dEAduction
PrettyName
    Majorants, minorants
-/

def majorant (E: set ℝ) (M: ℝ) := ∀ x ∈ E, x ≤ M
notation M ` est_un_majorant_de ` E := majorant E M
def minorant (E: set ℝ) (m: ℝ) := ∀ x ∈ E, m ≤ x
notation M ` est_un_minorant_de ` E := minorant E M
def est_majore (E: set ℝ) := ∃ M, majorant E M
def est_minore (E: set ℝ) := ∃ m, minorant E m
def est_borne (E: set ℝ) := (est_majore E) ∧ (est_minore E)
notation E ` est_borné` := est_borne E
notation E ` est_majoré` := est_majore E
notation E ` est_minoré` := est_minore E

------------------------
-- lemma DEFS A ECRIRE
------------------------
namespace definitions

lemma definition.majorant
(E: set ℝ) (M: ℝ) :
majorant E M ↔  ∀ x ∈ E, x ≤ M
:=
/- dEAduction
PrettyName
    Majorant
-/
begin
    sorry
end

lemma definition.minorant
(E: set ℝ) (m: ℝ) :
minorant E m ↔  ∀ x ∈ E, m ≤ x
:=
/- dEAduction
PrettyName
    Minorant
-/
begin
    sorry
end

lemma definition.est_majore
(E: set ℝ) :
est_majore E ↔ ∃ M, majorant E M
:=
/- dEAduction
PrettyName
    Partie majorée
-/
begin
    sorry
end

lemma definition.est_minore
(E: set ℝ) :
est_minore E ↔ ∃ m, minorant E m
:=
/- dEAduction
PrettyName
    Partie minorée
-/
begin
    sorry
end

lemma definition.est_borne
(E: set ℝ) :
est_borne E ↔  (est_majore E) ∧ (est_minore E)
:=
/- dEAduction
PrettyName
    Partie bornée
-/
begin
    sorry
end

notation `|`x`|`:= @abs ℝ _ x  -- valeur absolue sur ℝ

lemma theorem.est_borne
(E: set ℝ) :
est_borne E ↔ ( ∃ M, ∀ x:ℝ, x ∈ E → |x| ≤ M )
:=
/- dEAduction
PrettyName
    Caractérisation pratique d'une partie bornée
-/
begin
    sorry
end

end definitions

namespace exercices

-- def interval_ferme (a b:ℝ) := {x:ℝ // a ≤ x ∧ x ≤ b }
notation `[` a `,`b `]` := interval (a:ℝ) (b:ℝ)


lemma definition.intervalle_ferme {a b x : ℝ} :
x ∈ [a, b] ↔ (a ≤ x and x ≤ b)
:=
begin
    sorry
end

lemma exercise.exemple_ensemble_borne :
est_borne [(0:ℝ),1]
:=
/- dEAduction
PrettyName
    L'intervalle [0,1] est borné
-/
begin
    sorry
end


lemma essai1 (x ≤ (1:ℝ)) : x ≤ (2:ℝ)
:=
begin
    linarith,
end

lemma exercise.exemple_ensemble_borne_2 (a b : ℝ):
est_borne [a,b]
:=
/- dEAduction
PrettyName
    L'intervalle [a,b] est borné
-/
begin
    sorry
end

lemma essai2 (a: ℝ) (x ≤ (a:ℝ)) : x ≤ (a+1)
:=
begin
    linarith,
end

lemma theorem.R_non_borne :
¬ est_borne (set.univ)
:=
begin
    sorry
end

end exercices

end majorants_minorants


namespace borne_sup
/- dEAduction
PrettyName
    Borne supérieure
-/
open majorants_minorants

def borne_sup (E: set ℝ) (M: ℝ) := (majorant E M) ∧ (∀ m, majorant E m → M ≤ m)
def borne_inf (E: set ℝ) (M: ℝ) := (minorant E M) ∧ (∀ m, minorant E m → m ≤ M)
notation M ` =Sup ` E := borne_sup E M
notation M ` =Inf ` E := borne_inf E M


------------------------
-- lemma DEFS A ECRIRE
------------------------

lemma definition.borne_superieure
(E: set ℝ) (M: ℝ) :
borne_sup E M ↔  (majorant E M) ∧ (∀ m, majorant E m → M ≤ m)
:=
begin
    refl,
end

lemma definition.borne_inferieure
(E: set ℝ) (M: ℝ) :
borne_inf E M ↔  (minorant E M) ∧ (∀ m, minorant E m → m ≤ M)
:=
begin
    refl,
end


-- theorem admis : Axiome de la borne supérieure
lemma theorem.borne_superieure :
∀ E : set ℝ, est_majore E → ∃ M, borne_sup E M
:=
begin
    sorry
end

lemma definition.oppose_ensemble
(E F : set ℝ) :
F = -E ↔ (∀ x, x ∈ F ↔ -x ∈ E)
:=
/- dEAduction
PrettyName
    Opposé d'une partie de ℝ
-/
begin
    sorry
end

lemma exercise.oppose_minore
(E F : set ℝ) (H: F = -E): est_minore E ↔ est_majore (F)
:=
/- dEAduction
PrettyName
    L'opposé d'une partie minorée est majorée, et réciproquement
-/
begin
    hypo_analysis,
    sorry
end

lemma exercise.inf_de_oppose
(E : set ℝ) : est_minore E → ∃ M, borne_inf E M
:=
/- dEAduction
PrettyName
    "Axiome de la borne inférieure"
-/
begin
    sorry
end







namespace exercices

-- exo 8 a b c d
lemma exercise.plus_petit_que_tout_positif_I :
∀x:ℝ, ((∀ ε>0, x< ε) → x ≤ 0) :=
/- dEAduction
PrettyName
    1M003 exercice 1.8 (a)
-/

begin
    intro x,
    intro H1,
    by_contradiction,
    let   ε := x/2,
    have H2 : ε = x/2, refl,
    have H3: ε>0, by linarith,
    have H4 := H1 ε H3,
    linarith,
end

lemma exercise.plus_petit_que_tout_positif_II :
not (∀x:ℝ, ((∀ ε>0, x< ε) → x < 0)) :=
/- dEAduction
PrettyName
    1M003 exercice 1.8 (b)
-/
begin
    push_neg,
    use 0, split,
    intro ε, intro H,
    linarith,
    linarith,
end

lemma exercise.inf_positive :
not (∀ A : set ℝ, ∀ m:ℝ,
((borne_inf A m) ∧ (∀ x ∈ A, x > (0:ℝ))) → m >0)
:=
/- dEAduction
PrettyName
    1M003 exercice 1.8 (c)
-/
begin
    sorry
end

lemma exercise.inf_negative
(A: set ℝ) (m:ℝ) (H: borne_inf A m):
(∀ ε>(0:ℝ), ∃ a ∈ A, a  < ε) → m  ≤ 0
:=
/- dEAduction
PrettyName
    1M003 exercice 1.8 (d)
-/
begin
    intro H1,
    by_contradiction H2,
    push_neg at H2,
    rw definition.borne_inferieure at H,
    cases H with Ha Hb,
    specialize H1 m,
    specialize H1 H2,
    rcases H1 with ⟨ a, ⟨ H3, H4 ⟩ ⟩,
    rw majorants_minorants.definitions.definition.minorant at Ha,
    specialize Ha a,
    specialize Ha H3,
    linarith,
end


end exercices

end borne_sup

end nombres_reels



namespace analyse

namespace suites
-- NB : dans le cours, suites complexes, mais ici on se limite aux suites réelles

-- limite

-- ex : 1/n tend vers 0

-- unicite

-- (-1)^n diverge

-- suite bornée

-- convergente implique bornee

-- limite d'une somme, d'un produit, de l'inverse

-- Passage à la limite dans les inégalités larges

-- Théorème des gendarmes

-- corollaire : existence d'une suite convergeant vers la borne inf.

-- une suite croissante majorée converge (vers la borne sup de ses valeurs)

-- limites infinies. Une partie non majorée contient une suite qui tend vers +∞
-- Une suite croissante non majorée tend vers +∞

-- suites adjacentes, convergence

-- sous-suites

-- BW

-- une suite bornée CV ssi elle admet une unique valeur d'adhérence

namespace exercices

-- exo 3 : CV de l'inverse (avec un lemme)

-- toute suite convergente de nombres entiers est stationnaire

-- Une suite CV vers l ssi les deux suites extraites d'ordre pair et impair CV vers l

-- une suite bornee divergente a au moins deux valeurs d'adhérence

-- théorème de Cesaro

-- Suites de Cauchy : CV → Cauchy ; Cauchy → bornée ; Cauchy → sous-suite CV : Cauchy → CV.

end exercices

end suites

namespace continuite




end continuite

end analyse








end maths_approfondies

end course
