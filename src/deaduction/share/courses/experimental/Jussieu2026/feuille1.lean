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
periodique = [-1, " est périodique de période 1"]
-/

-- available_exercises = "NONE"
-- [display]
-- segment = [ "[",-2, " , ", -1, "]"]
-- function.add = [ -2, " + ", -1 ]
-- calculator_definitions = ["paire", "impaire"]

local attribute [instance] classical.prop_decidable

---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course

open set
open nat

lemma definition.composition ( g : ℝ → ℝ ) ( f : ℝ → ℝ ){x: ℝ} :
(g ∘ f) x = g (f x)
:=
begin
    refl
end

def croissante ( f : ℝ → ℝ )  := ∀ x : ℝ, ∀ y : ℝ, ( x ≤ y) → (f x ≤ f y )

lemma definition.croissante ( f : ℝ → ℝ ) :
croissante f ↔ ∀ x : ℝ, ∀ y : ℝ, ( x ≤ y) → (f x ≤ f y )
:=
/- dEAduction
pretty_name = "Fonction croissante"
implicit_use = true
-/
begin
    todo
end

def decroissante ( f : ℝ → ℝ )  := ∀ x : ℝ, ∀ y : ℝ, ( x ≤ y) → (f y ≤ f x )

lemma definition.decroissante ( f : ℝ → ℝ ) :
decroissante f ↔ ∀ x : ℝ, ∀ y : ℝ, ( x ≤ y) → (f y ≤ f x )
:=
/- dEAduction
pretty_name = "Fonction décroissante"
implicit_use = true
-/
begin
    todo
end

def periodique ( f : ℝ → ℝ )  := ∀ x : ℝ, f(x+1) = f x

lemma definition.periodique ( f : ℝ → ℝ ) :
periodique f ↔ ∀ x : ℝ, f(x+1) = f x
:=
/- dEAduction
pretty_name = "Fonction périodique de période 1"
-/
begin
    todo
end

def paire ( f : ℝ → ℝ )  := ∀ x : ℝ, (f (-x) = f x)

lemma definition.paire ( f : ℝ → ℝ ) :
paire f ↔ ∀ x : ℝ, (f (-x) = f x)
:=
/- dEAduction
pretty_name = "Fonction paire"
implicit_use = true
-/
begin
    todo
end

def impaire (f : ℝ → ℝ )  := ∀ x : ℝ, (f (-x) = -f x)

lemma definition.impaire ( f : ℝ → ℝ ) :
impaire f ↔ ∀ x : ℝ, (f (-x) = -f x)
:=
/- dEAduction
pretty_name = "Fonction impaire"
implicit_use = true
-/
begin
    todo
end


namespace utiliser_pour_tout
/- dEAduction
pretty_name = "Utiliser une propriété universelle"
-/

-- Utiliser ∀
lemma exercise.utiliser_periodique (f: ℝ → ℝ) (H_0: periodique f) :
f 8 = f 9
:=
/- dEAduction
pretty_name = "Utiliser une hypothèse de périodicité"
-/
begin
    todo
end

lemma exercise.utiliser_paire   (f : ℝ → ℝ ) (H_0 : paire f) :
f (11) = f (-11)
:=
/- dEAduction
pretty_name = "Utiliser une hypothèse de parité"
-/
begin
    todo
end

-- Pb = on doit aussi utiliser une implication
-- Sol = Deaduction devrait démontrer automatiquement la prémisse 0 < 1
lemma exercise.utiliser_croissante (f: ℝ → ℝ) (H_0: croissante f) :
f 0 ≤ f 1
:=
/- dEAduction
pretty_name = "Utiliser une hypothèse de croissance"
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
lemma exercise.croissante2x :
((croissante (λ (x: ℝ) , (2 : ℝ)*x) ))
:=
/- dEAduction
pretty_name = "Démontrer qu'une fonction est croissante"
-/
begin
    todo
end

lemma exercise.pairecarree   ( f : ℝ → ℝ ) (H : ∀ x:ℝ, f x = x^2 ) :
paire f
:=
/- dEAduction
pretty_name = "Démontrer qu'une fonction est paire"
-/
begin
    todo
end

lemma exercise.impairecube   ( f : ℝ → ℝ ) (H : ∀ x:ℝ, f x = x^3 ) :
impaire f
:=
/- dEAduction
pretty_name = "Démontrer qu'une fonction est impaire"
-/
begin
    todo
end

end demontrer_pour_tout



namespace utiliser_et_demontrer
/- dEAduction
pretty_name = "Utiliser et démontrer"
-/

lemma exercise.croissanceetsomme  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )
(H_0: croissante f) (H_1: croissante g) :
 (croissante (λ (x: ℝ), f x + g x ) )
:=
/- dEAduction
pretty_name = "Croissance et somme"
-/
begin
    todo
end

lemma exercise.croissante_croissante  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )
(H_0: croissante f) (H_1: croissante g) :
croissante (function.comp g f : ℝ → ℝ)
:=
/- dEAduction
pretty_name = "Croissance et composition"
-/
begin
    todo
end

-- A JOKERISER
lemma exercise.decroissante_decroissante  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )
(H_0 : decroissante f) (H_1: decroissante g) :
croissante (function.comp g f : ℝ → ℝ)
:=
/- dEAduction
pretty_name = "Décroissance et composition"
-/
begin
    todo
end

lemma exercise.decroissante_croissante  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )
(H_0 : decroissante f) (H_1: croissante g) :
decroissante (function.comp g f : ℝ → ℝ)
:=
/- dEAduction
pretty_name = "Décroissance, croissance et composition"
-/
begin
    todo
end





-- Plus dur : le cube est croissant, il faut calculer avec les énoncés fournis


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

lemma exercise.croissantecube   ( f : ℝ → ℝ ) (H : ∀ x:ℝ, f x = x^3 ) :
croissante f
:=
/- dEAduction
pretty_name = "La fonction cube est croissante"
description = "Utiliser les énoncés fournis pour démontrer l'inégalité recherchée"
-/
begin
    todo
end



-- Plus dur : disjonction de cas
-- retirer linarith, ajouter les théorèmes de calcul ad hoc, ou les boutons

lemma exercise.monotoneaffine  :
∀ a:ℝ, ∀ b:ℝ,
(croissante (λ (x: ℝ) , a*x+b) ) or (decroissante (λ (x: ℝ) , a*x+b) )
:=
/- dEAduction
pretty_name = "Les fonctions affines sont croissantes ou décroissantes"
description = "Ici, le bouton Méthodes de Preuves est indispensable !"
-/
begin
    todo 
end

end utiliser_et_demontrer


namespace contreexemples
/- dEAduction
pretty_name = "Contre-exemples"
-/

-- Il faut la négation du "pour tout"

lemma exercise.nonpaire :
not (paire (λ (x:ℝ), x+1))
:=
/- dEAduction
pretty_name = "La fonction f:ℝ → ℝ, f(x) = x+1, n'est pas paire."
open_question = false
-/
begin
    todo
end

lemma exercise.nonimpaire :
not (impaire (λ (x:ℝ), x+1))
:=
/- dEAduction
pretty_name = "La fonction f:ℝ → ℝ, f(x) = x+1, n'est pas impaire."
open_question = false
-/
begin
    todo
end

lemma exercise.pariteseconddegre  :
(paire (λ (x: ℝ) , x^2+x+1) )
:=
/- dEAduction
pretty_name = "La fonction f :  ℝ → ℝ, f(x) = x²+x+1, est-elle paire ?"
open_question = true
-/
begin
    todo
end


-- GROS PB : avec la négation de f est impaire, qui conduit à un truc chelou
lemma exercise.impariteaffine  :
(∀ a:ℝ, ∀ b:ℝ, impaire (λ (x:ℝ), a*x+b) )
:=
/- dEAduction
pretty_name = "La fonction f_(a,b) :  ℝ → ℝ, f(x) = ax+b, est-elle impaire ?"
open_question = true
-/
begin
    todo
end


namespace Paritecomposition
/- dEAduction
pretty_name = "Parité et composition : questions ouvertes"
-/


-- BOFBOF : négation, et c'est long de rentrer des fonctions
lemma exercise.paireetcomp1  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )  :
(paire g)→ (paire (function.comp g f : ℝ → ℝ) )
:=
/- dEAduction
pretty_name = "Parité et composition I : VRAI OU FAUX ?"
open_question = true
-/
begin
    todo
end

lemma exercise.paireetcomp2  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )  :
(paire f)→ (paire (function.comp g f : ℝ → ℝ) )
:=
/- dEAduction
pretty_name = "Parité et composition II : VRAI OU FAUX ?"
open_question = true
-/
begin
    todo
end

lemma exercise.paireetcomp3  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )  :
(paire  g and paire f)→ (paire (function.comp g f : ℝ → ℝ) )
:=
/- dEAduction
pretty_name = "Parité et composition III : VRAI OU FAUX ?"
available_exercises = "paireetcomp2"
open_question = true
-/
begin
    todo
end

lemma exercise.impaireetcomp1  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )  :
(impaire g) → (impaire (function.comp g f : ℝ → ℝ) )
:=
/- dEAduction
pretty_name = "Imparité et composition I : VRAI OU FAUX ?"
open_question = true
-/
begin
    todo
end

lemma exercise.impaireetcomp2  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )  :
(impaire f) → (impaire (function.comp g f : ℝ → ℝ) )
:=
/- dEAduction
pretty_name = "Imparité et composition II : VRAI OU FAUX ?"
open_question = true
-/
begin
    todo
end

lemma exercise.impaireetcomp3  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )  :
((impaire f) and (impaire g)) → (impaire (function.comp g f : ℝ → ℝ) )
:=
/- dEAduction
pretty_name = "Imparité et composition III : VRAI OU FAUX ?"
open_question = true
-/
begin
    todo
end

end Paritecomposition


end contreexemples


end course






