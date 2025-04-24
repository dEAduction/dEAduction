/-
Feuille d'exercices pour travailler les notions de parité et croissance pour les fonctions numériques - Particulièrement utile pour travailler l'utilisation d'un Pour tout.
-/

import data.set
import data.real.basic
import init


import tactic

-- dEAduction tactics
import deaduction_all_tactics
-- import compute
-- import structures2      -- hypo_analysis, targets_analysis
-- import utils            -- no_meta_vars
-- import user_notations   -- notations that can be used in deaduction UI for a new object
-- import push_neg_once


-- dEAduction definitions
import set_definitions

-- General principles :
-- Type should be defined as parameters, in order to be implicit everywhere
-- other parameters are implicit in definitions, i.e. defined using '{}' (e.g. {A : set X} )
-- but explicit everywhere else, i.e. defined using '()' (e.g. (A : set X) )
-- each definition must be an iff statement or an equality
-- (since it will be called with 'rw' or 'symp_rw')

-------------------------
-- dEAduction METADATA --
-------------------------
-- logic names ['and', 'or', 'negate', 'implicate', 'iff', 'forall', 'exists']
-- proofs names ['use_proof_methods', 'new_object', 'apply', 'assumption']
-- magic names ['compute']
-- proof methods names ['cbr', 'contrapose', 'absurdum', 'sorry']

/- dEAduction
title = "Fonctions : parité et croissance"
author = "Isabelle Dubois"
institution = "Université de Lorraine"
description = "Cette feuille propose de travailler les  notions de parité et monotonie pour des fonctions définies sur ℝ."
available_exercises = "NONE"
calculator_definitions = ["paire", "impaire"]
[display]
segment = [ "[",-2, " , ", -1, "]"]
function.add = [ -2, " + ", -1 ]
[settings]
functionality.calculator_available = true
others.Lean_request_method = "normal"
-/

/- RESTES
    sqrt --> ( "racine (",-1, ")")
Display
    segment --> ( "[",-2, " , ", -1, "]")
    
AvailableDefinitions
    ALL -sqrt
-/

local attribute [instance] classical.prop_decidable

---------------------------------------------
-- global parameters = implicit variables --
---------------------------------------------
section course

open set
open nat

-- noncomputable theory

def segment (a b : ℝ) := {x | a ≤ x ∧ x ≤ b}

notation `[`a `, ` b `]` := segment a b






---------------
-- EXERCICES --
---------------

lemma definition.composition ( g : ℝ → ℝ ) ( f : ℝ → ℝ ){x: ℝ} :
function.comp g f x = g (f x)
:=
begin
    todo
end



namespace exercices_parite
/- dEAduction
pretty_name = "Exercices sur la parité des fonctions"
-/

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

def impaire ( f : ℝ → ℝ )  := ∀ x : ℝ, (f (-x) = -f x)

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

namespace Exemples

lemma exercise.pairecsqce   ( f : ℝ → ℝ ) (H : paire f ) :
f (11) = f (-11)
:=
/- dEAduction
pretty_name = "Conséquence parité"
-/
begin
    todo
end



lemma exercise.pairecarree   ( f : ℝ → ℝ ) (H : ∀ x:ℝ, f x = x^2 ) :
paire f
:=
/- dEAduction
pretty_name = "La fonction carrée est paire"
-/
begin
    todo
end

lemma exercise.impairecube   ( f : ℝ → ℝ ) (H : ∀ x:ℝ, f x = x^3 ) :
impaire f
:=
/- dEAduction
pretty_name = "La fonction cube est impaire"
-/
begin
    todo
end

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


-- AJOUTER avec la nouvelle calcul :
-- lemma exercise.paire_et_impare:
-- ∃ f: ℝ → ℝ, (not paire f) and (not impaire f)
-- :=
-- /- dEAduction
-- PrettyName
--     Paire ou impaire ?
-- OpenQuestion
-- 	  True
-- AvailableExercices
--    non_paire non_impaire
-- -/
-- begin
--     todo
-- end

end Exemples

namespace Questions_ouvertes

lemma exercise.nonpaire2x  :
paire (λ (x: ℝ) , (2 : ℝ)*x)
:=
/- dEAduction
pretty_name = "La fonction f:ℝ → ℝ, f(x) = 2x, est-elle paire ?"
open_question = true
-/
begin
    todo
end

lemma exercise.paritecarreeplus1  :
(paire (λ (x: ℝ) , x^2+1) )
:=
/- dEAduction
pretty_name = "La fonction f:ℝ → ℝ, f(x) = x²+1, est-elle paire ?"
open_question = true
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

lemma exercise.imparitelineaire  :
(∀ a:ℝ, impaire (λ (x: ℝ) , a*x) )
:=
/- dEAduction
pretty_name = "La fonction fₐ:ℝ → ℝ, f(x) = ax, est-elle impaire ?"
open_question = true
-/
begin
    todo
end
  
lemma exercise.impariteaffine  :
(∀ a:ℝ, ∀ b:ℝ, impaire (λ (x: ℝ) , a*x+b) )
:=
/- dEAduction
pretty_name = "La fonction f_(a,b) :  ℝ → ℝ, f(x) = ax+b, est-elle impaire ?"
open_question = true
-/
begin
    todo
end

end Questions_ouvertes

namespace Paritecomposition
/- dEAduction
pretty_name = "Parité et composition : VRAI ou FAUX ?"
-/

-- lemma exercise.paireetcompex   ( f : ℝ → ℝ ) ( g : ℝ → ℝ )  :
-- (paire f)→ (function.comp g f (-2 : ℝ) = function.comp g f ( 2 : ℝ) )
-- :=
-- /- dEAduction
-- PrettyName
--     Parité et composition, exemple
-- -/
-- begin
--     todo
-- end

lemma exercise.paireetcomp1  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )  :
(paire g)→ (paire (function.comp g f : ℝ → ℝ) )
:=
/- dEAduction
pretty_name = "Parité et composition I : VRAI OU FAUX ?"
-/
begin
    todo
end

lemma exercise.paireetcomp2  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )  :
(paire f)→ (paire (function.comp g f : ℝ → ℝ) )
:=
/- dEAduction
pretty_name = "Parité et composition II : VRAI OU FAUX ?"
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
-/
begin
    todo
end

lemma exercise.impaireetcomp1  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )  :
(impaire g) → (impaire (function.comp g f : ℝ → ℝ) )
:=
/- dEAduction
pretty_name = "Imparité et composition I : VRAI OU FAUX ?"
-/
begin
    todo
end

lemma exercise.impaireetcomp2  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )  :
(impaire f) → (impaire (function.comp g f : ℝ → ℝ) )
:=
/- dEAduction
pretty_name = "Imparité et composition II : VRAI OU FAUX ?"
-/
begin
    todo
end

lemma exercise.impaireetcomp3  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )  :
((impaire f) and (impaire g)) → (impaire (function.comp g f : ℝ → ℝ) )
:=
/- dEAduction
pretty_name = "Imparité et composition III : VRAI OU FAUX ?"
-/
begin
    todo
end

end Paritecomposition

namespace PariteSomme
/- dEAduction
pretty_name = "Parité et somme"
-/

def function.add ( f : ℝ → ℝ ) ( g : ℝ → ℝ ) :  ℝ → ℝ 
:= λ (x: ℝ), f x + g x 


lemma definition.somme ( f : ℝ → ℝ ) ( g : ℝ → ℝ ) ( h : ℝ → ℝ ) :
f = function.add g h ↔ ∀ x:ℝ, f x = g x + h x
:=
/- dEAduction
pretty_name = "Fonction somme de deux fonctions"
-/
begin
    todo
end

lemma exercise.paireetsomme  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )  :
((paire f) and (paire g)) → (paire (λ x, f x  + g x) )
:=
/- dEAduction
pretty_name = "Parité et somme"
-/
begin
    todo
end

lemma exercise.paireetimpaire  ( f : ℝ → ℝ ) :
((paire f) and (impaire f)) → (∀ x:ℝ, f x = 0  )
:=
/- dEAduction
pretty_name = "Une fonction paire et impaire est nulle"
-/
begin
    todo
end

lemma exercise.decompositionpaireplusimpaire  ( f : ℝ → ℝ ):
∃ (g:ℝ → ℝ) (h:ℝ → ℝ), (f = function.add g h) and (paire g) and (impaire h)
:=
/- dEAduction
pretty_name = "Décomposition d'une fonction"
-/
begin
  todo
end

-- lemma exercise.decompositionpaireplusimpaire  ( f : ℝ → ℝ ) ( g  :ℝ → ℝ ) (h :ℝ → ℝ ) :
--  ( (f =  function.add g h ) and ((paire g) and (impaire h))) → 
--  ( exists a : ℝ, exists b : ℝ, exists c : ℝ, exists d : ℝ,  ∀ x:ℝ, (g x = a*f (x) + b*f(-x)) and (  h x = c*f(x) + d*f(-x) ))
-- :=
-- lemma exercise.decompositionpaireplusimpaire  ( f : ℝ → ℝ ) :
-- ∃ C: ((ℝ → ℝ) × (ℝ → ℝ)), ((paire C.1) and (impaire C.2)) :=
-- /- dEAduction
-- PrettyName
--     Décomposition d'une fonction en somme d'un fonction paire et d'une fonction impaire
-- -/
-- begin
--     todo
-- end

end PariteSomme
end exercices_parite




namespace exercices_monotonie
/- dEAduction
pretty_name = "Exercices sur la monotonie de fonctions"
-/

@[simp] axiom carrefois :  ∀ x:ℝ, x^2= x*x 
@[simp] axiom cubefois :  ∀ x:ℝ, x^3= x*x*x

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


lemma exercise.pasmonotonecarree   ( f : ℝ → ℝ ) (H : ∀ x:ℝ, f x = x^2 ) :
not(croissante f)
:=
/- dEAduction
pretty_name = "La fonction carrée n'est pas croissante"
-/
begin
    todo
end





lemma exercise.croissante2x  :
((croissante (λ (x: ℝ) , (2 : ℝ)*x) ))
:=
/- dEAduction
pretty_name = "La fonction f :  ℝ → ℝ, f(x) = 2x, est croissante"
-/
begin
    todo
end

lemma exercise.croissantelineaire  :
(∀ a:ℝ, croissante (λ (x: ℝ) , a*x) )
:=
/- dEAduction
pretty_name = "La fonction f_a :  ℝ → ℝ, f(x) = ax, est-elle croissante ?"
open_question = true
-/
begin
    todo
end

lemma exercise.monotoneaffine  :
∀ a:ℝ, ∀ b:ℝ,
(croissante (λ (x: ℝ) , a*x+b) ) or (decroissante (λ (x: ℝ) , a*x+b) )
:=
/- dEAduction
pretty_name = "La fonction f_(a,b) :  ℝ → ℝ, f(x) = ax+b, est-elle monotone ?"
open_question = true
-/
begin
    todo
end



lemma exercise.croissante_croissante  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )  :
((croissante f) and (croissante g)) → (croissante (function.comp g f : ℝ → ℝ) )
:=
/- dEAduction
pretty_name = "Croissance et composition"
-/
begin
    todo
end

lemma exercise.decroissante_decroissante  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )  :
((decroissante f) and (decroissante g)) → (croissante (function.comp g f : ℝ → ℝ) )
:=
/- dEAduction
pretty_name = "Décroissance et composition"
-/
begin
    todo
end

lemma exercise.decroissante_croissante  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )  :
((decroissante f) and (croissante g)) → (decroissante (function.comp g f : ℝ → ℝ) )
:=
/- dEAduction
pretty_name = "Décroissance, croissance et composition"
-/
begin
    todo
end

lemma exercise.croissanceetsomme  ( f : ℝ → ℝ ) ( g : ℝ → ℝ )  :
((croissante f) and (croissante g)) → (croissante (λ (x: ℝ), f x + g x ) )
:=
/- dEAduction
pretty_name = "Croissance et somme"
-/
begin
    todo
end

lemma exercise.croissanceethyp  ( f : ℝ → ℝ )  :
((croissante f) and ( ∀ x:ℝ, function.comp f f x = x)) → ∀ x:ℝ, f x = x
:=
/- dEAduction
pretty_name = "Croissance et idempotence"
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

lemma exercise.croissantecube   ( f : ℝ → ℝ ) (H : ∀ x:ℝ, f x = x^3 ) :
croissante f
:=
/- dEAduction
pretty_name = "La fonction cube est croissante"
-/
begin
    todo
end





end exercices_monotonie



end course

