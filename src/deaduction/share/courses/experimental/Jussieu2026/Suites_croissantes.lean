/- Feuille d'exercices sur le quantificateur universel,
utilisant des notions d'analyse élémentaires.
-/

import data.set
import data.real.basic
import init


import tactic

-- dEAduction tactics
import deaduction_all_tactics

-- dEAduction definitions
import set_definitions

/- dEAduction
title = "Feuille 1 : quantificateur universel"
author = "Frédéric Le Roux"
institution = "Sorbonne Université"
description = ""
[settings]
logic.usr_jokers_available = false
logic.use_color_for_applied_properties = false
functionality.allow_induction = true
functionality.calculator_available = true
others.Lean_request_method = "normal"
[display]
periodique = [-2, " est périodique de période ", -1]
croissante_f = [-1, " est croissante"]
decroissante_f = [-1, " est décroissante"]
-/

-- has_mod.mod = [-2, " modulo ", -1]


local attribute [instance] classical.prop_decidable

---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course

open set
open nat

def positive (u : ℕ → ℝ)  := ∀ n, u n ≥ 0

def croissante ( u : ℕ → ℝ )  := ∀ m n : ℕ, m ≤ n → ( u m ≤ u n)

def decroissante ( u : ℕ → ℝ )  := ∀ m n : ℕ, m ≤ n → ( u m ≥ u n)

def periodique (u : ℕ → ℝ) (p: ℕ)  := ∀ n, u (n+p) = u n

def even (a:ℕ) := ∃ b, a = 2*b 

def odd (a:ℕ) := ∃ b, a = 2*b + 1 

namespace definitions_suites
/- dEAduction
pretty_name = "Propriétés des suites : définitions"
-/

lemma definition.suite_positive {u}:
positive u ↔ ∀ n, u n ≥ 0
:=
/- dEAduction
pretty_name = "Suite positive"
implicit_use = true
-/
begin
    todo
end

lemma definition.suite_periodique {u} {p}:
periodique u p ↔ ∀ n, u (n+p) = u n
:=
/- dEAduction
pretty_name = "Suite périodique"
implicit_use = true
-/
begin
    todo
end

lemma definition.suite_croissante1 {u}:
croissante u ↔ ∀ n, u n ≤ u (n+1)
:=
/- dEAduction
pretty_name = "Suite croissante, définition 1"
implicit_use = true
-/
begin
    todo
end

lemma definition.suite_croissante2 {u}:
croissante u ↔ ∀ m n, m ≤ n → ( u m ≤ u n)
:=
/- dEAduction
pretty_name = "Suite croissante, définition 2"
implicit_use = false
-/
begin
    todo
end

lemma definition.suite_decroissante1 {u}:
decroissante u ↔ ∀ n, u n ≥ u (n+1)
:=
/- dEAduction
pretty_name = "Suite décroissante, définition 1"
implicit_use = true
-/
begin
    todo
end

lemma definition.suite_decroissante2  {u}:
decroissante u ↔ ∀ m n, m ≤ n → ( u m ≥ u n)
:=
/- dEAduction
pretty_name = "Suite décroissante, définition 2"
implicit_use = false
-/
begin
    todo
end

end definitions_suites

namespace lemme_de_calcul

lemma theorem.puissance_somme :
∀ a:ℝ, ∀b c: ℕ, a^(b+c) = a^b * a^c :=
/- dEAduction
pretty_name = "Puissance d'une somme"
-/
begin
  todo
end

lemma theorem.deux_est_pair :
even 2 :=
/- dEAduction
pretty_name = "Deux est pair"
-/
begin
  todo
end

lemma theorem.signe_parite_pair  :
∀ n:ℕ, ((even n) → ((-1:ℤ)^n = 1 ))
:= 
/- dEAduction
pretty_name = "(-1) puissance pair"
-/
begin
   todo
end

lemma theorem.signe_parite_impair  :
∀ n:ℕ, ((odd n) → ((-1:ℤ)^n = -1 ))
:= 
/- dEAduction
pretty_name = "(-1) puissance impair"
-/
begin
   todo
end

lemma theorem.pair_ou_impair :
∀ n, even n or odd n
:=
/- dEAduction
pretty_name = "Tout nombre est pair ou impair"
description = """Cet énoncé est utile pour faire une preuve pas cas.
Appliquez-le à votre entier préféré,
puis utilisez la propriété de disjonction obtenue.
"""
-/
begin
   todo
end

lemma theorem.prodpos (a:ℝ) (b:ℝ) :
 (( 0 ≤ a ) and (0 ≤ b )) → (0 ≤  a*b )
:=
/- dEAduction
pretty_name = "Produit nombres positifs"
implicit_use = true
-/
begin
    todo
end

lemma theorem.sompos (a:ℝ) (b:ℝ) :
 (( 0 ≤ a ) and (0 ≤ b )) → (0 ≤  a + b )
:=
/- dEAduction
pretty_name = "Somme nombres positifs"
implicit_use = true
-/
begin
    todo
end

lemma theorem.carrepos  :
 ∀ c:ℝ,   0 ≤ c^2
:=
/- dEAduction
pretty_name = "Carrés positifs"
implicit_use = true
-/
begin
    todo
end

lemma theorem.ineg (a:ℝ) (b:ℝ) :
 (( a ≤ b )) ↔  (0 ≤  b-a )
:=
/- dEAduction
pretty_name = "Inégalité"
implicit_use = true
-/
begin
    todo
end

lemma theorem.identite :
∀ a:ℝ, ∀ b:ℝ,  a^3 - b^3 = (a-b)*(a^2 +a*b +b^2)
:=
/- dEAduction
pretty_name = "Différence de deux cubes"
-/
begin
  todo
end

end lemme_de_calcul


namespace utiliser_pour_tout
/- dEAduction
pretty_name = "Utiliser une propriété universelle"
-/

lemma exercise.utiliser_positive (u) (H: positive u):
u 22 ≥ 0
:=
/- dEAduction
pretty_name = "Utiliser une hypothèse de positivité"
description = """Pour "dérouler" la définition, 
sélectionnez l'hypothèse du contexte,
puis cliquez sur la définition dans la zone des énoncés"""
-/
begin
  todo,
end

-- Nettement plus facile avec def 1 que def 2
lemma exercise.utiliser_croissante (u) (H: croissante u) :
u 123 ≤ u 234
:=
/- dEAduction
pretty_name = "Utiliser une hypothèse de croissance"
description = """Vous pouvez essayer successivement
avec les deux définitions de croissance"""
-/
begin
    todo
end

lemma exercise.utiliser_periodique (u) (H: periodique u 10):
u 27 = u 57
:=
/- dEAduction
pretty_name = "Utiliser une hypothèse de périodicité"
description = """Le bouton "=" permet d'utiliser une égalité
(ou même une égalité universelle) pour substituer dans le but
ou dans une propriété du contexte"""
-/
begin
    todo
end


end utiliser_pour_tout


namespace demontrer_pour_tout
/- dEAduction
pretty_name = "Démontrer une propriété universelle"
-/

-- Démontrer ∀
-- Manque un bouton de calcul * 
-- Plutôt nommer la suite ?
lemma exercise.positive_n (u: ℕ → ℝ) (H: ∀n, u n = n):
positive u
:=
/- dEAduction
pretty_name = "Démontrer qu'une suite est positive"
-/
begin
    todo
end

lemma exercise.croissante_2n (u: ℕ → ℝ) (H: ∀n, u n = 2*n):
croissante u
:=
/- dEAduction
pretty_name = "Démontrer qu'une suite est croissante"
-/
begin
    todo
end

lemma exercise.periodique (u: ℕ → ℝ) (H: ∀n, u n =  (-1) ^n):
periodique u 2
:=
/- dEAduction
pretty_name = "Démontrer qu'une suite est periodique"
-/
begin
--     rw definitions_suites.definition.suite_periodique, intro n,
-- rw H, trace "EFFECTIVE CODE n°1.0", trace "EFFECTIVE CODE n°0.0", no_meta_vars,
-- rw H, trace "EFFECTIVE CODE n°4.0", trace "EFFECTIVE CODE n°3.0", no_meta_vars,
-- rw lemme_de_calcul.theorem.puissance_somme, trace "EFFECTIVE CODE n°7.0", trace "EFFECTIVE CODE n°8.1", trace "EFFECTIVE CODE n°6.0",
-- have H_0 := @lemme_de_calcul.theorem.signe_parite_pair ((2: @nat)),
-- have H_1: (even (2: @nat)),
-- apply_with lemme_de_calcul.theorem.deux_est_pair {md:=reducible},
-- have H_2 := H_0 H_1, trace "EFFECTIVE CODE n°13.0",
-- `[ `[ rw H_2, trace "EFFECTIVE CODE n°15.0"] <|> `[ simp_rw H_2, trace "EFFECTIVE CODE n°15.1"], trace "EFFECTIVE CODE n°14.0"] <|> `[ `[ rw <- H_2, trace "EFFECTIVE CODE n°16.0"] <|> `[ simp_rw <- H_2, trace "EFFECTIVE CODE n°16.1"], trace "EFFECTIVE CODE n°14.1"],
  todo
end

-- Faut-il ajouter des lemmes de calcul pour celui-ci ?
lemma exercise.monotoneaffine  :
∀ a:ℝ, ∀ b:ℝ,
croissante (λ n , a*n+b) or decroissante (λ n, a*n + b)
:=
/- dEAduction
pretty_name = "Les fonctions affines sont croissantes ou décroissantes"
description = """Distinguez deux cas à l'aide du bouton Méthodes de Preuves.
Et utilisez le bouton ∨ ("ou") pour démontrer une disjonction."""
-/
begin
    todo 
end

lemma exercise.croissantecube   (u : ℕ → ℝ ) (H : ∀ n, u n = n^3 ) :
croissante u
:=
/- dEAduction
pretty_name = "(*) La fonction cube est croissante"
description = "Utiliser les énoncés fournis pour démontrer l'inégalité recherchée"
-/
begin
    todo
end

end demontrer_pour_tout



namespace utiliser_et_demontrer
/- dEAduction
pretty_name = "Utiliser et démontrer"
-/

lemma exercise.croissance_et_somme  (u v)
(H: croissante u) (H': croissante v) :
 (croissante (λ n, u n + v n) )
:=
/- dEAduction
pretty_name = "Croissance et somme"
-/
begin
    todo
end

lemma exercise.croissance_et_oppose  (u: ℕ→ ℝ )
(H: decroissante u):
croissante (λ n, - u n)
:=
/- dEAduction
pretty_name = "Croissance et opposé"
-/
begin
    todo
end


lemma exercise.croissance_et_difference  (u v: ℕ→ ℝ )
(H: croissante u) (H': decroissante v):
croissante (λ n, u n - v n)
:=
/- dEAduction
pretty_name = "Croissance et différence"
description = """Pour aller plus vite, utilisez les deux exercices précédents !
Ils apparaissent dans la liste des énoncés."""
-/
begin
    todo
end

lemma exercise.definitions_croissante (u: ℕ→ ℝ):
(∀ n, u n ≤ u (n+1)) ↔ 
( ∀ m:ℕ, (∀ n, ( u m ≤ u (m+n) )))
:=
/- dEAduction
pretty_name = "Deux définitions équivalente de suites croissance"
description = """Quelle méthode de preuve voulez-vous utiliser ?"""
-/
begin
-- split,
-- intro H_0,
-- intro m,
-- apply induction.simple_induction,
-- rotate,intros n H,
-- have Hn := H_0 (m+n),
-- have Hn1 := le_trans H Hn,assumption,
  -- todo,
--   split,
-- intro H_0, 
-- OK:
-- apply @induction.simple_induction (λ m, ∀ (n : ℕ), u m ≤ u (m + n)),
-- intro m, 
-- apply @induction.simple_induction (λ (n : ℕ), u m ≤ u (m + n)),
-- apply induction.simple_induction,
  todo
end

end utiliser_et_demontrer

namespace definitions_fonctions
/- dEAduction
pretty_name = "Propriétés des fonctions : définitions"
-/

lemma definition.composition {X Y Z: Sort} (g : Y → Z ) ( f : X → Y ) {x} :
(g ∘ f) x = g (f x)
:=
begin
    refl
end

def croissante_f ( f : ℝ → ℝ )  := ∀ x : ℝ, ∀ y : ℝ, ( x ≤ y) → (f x ≤ f y )

lemma definition.croissante ( f : ℝ → ℝ ) :
croissante_f f ↔ ∀ x : ℝ, ∀ y : ℝ, ( x ≤ y) → (f x ≤ f y )
:=
/- dEAduction
pretty_name = "Fonction croissante"
implicit_use = true
-/
begin
    todo
end

def decroissante_f ( f : ℝ → ℝ )  := ∀ x : ℝ, ∀ y : ℝ, ( x ≤ y) → (f y ≤ f x )

lemma definition.decroissante ( f : ℝ → ℝ ) :
decroissante_f f ↔ ∀ x : ℝ, ∀ y : ℝ, ( x ≤ y) → (f y ≤ f x )
:=
/- dEAduction
pretty_name = "Fonction décroissante"
implicit_use = true
-/
begin
    todo
end

end definitions_fonctions


namespace fonctions
/- dEAduction
pretty_name = "Fonctions croissantes et décroissantes"
-/
open definitions_fonctions

lemma exercise.croissante_croissante  ( f g: ℝ → ℝ )
(H: croissante_f f) (H': croissante_f g) :
croissante_f (f ∘ g)
:=
/- dEAduction
pretty_name = "Croissance et composition"
-/
begin
    todo
end

lemma exercise.decroissante_decroissante  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )
(H : croissante_f f) (H_1: decroissante_f g) :
decroissante_f (function.comp g f : ℝ → ℝ)
:=
/- dEAduction
pretty_name = "Croissance, décroissance et composition"
-/
begin
    todo
end

lemma exercise.decroissante_croissante  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )
(H : croissante_f f or decroissante_f f)
(H': croissante_f g or decroissante_f g) :
(croissante_f (function.comp g f : ℝ → ℝ)
or croissante_f (function.comp g f : ℝ → ℝ))
:=
/- dEAduction
pretty_name = "Composition de fonctions monotones"
description = """
Dans cet exercice, nous allons utiliser les boutons
"Démontrer ∨" et "Utiliser ∨" pour démontrer et utiliser des disjonctions.
Pensez à utiliser les exercices précédents !
"""
-/
begin
    todo
end

end suites_et_fonctions

end course






