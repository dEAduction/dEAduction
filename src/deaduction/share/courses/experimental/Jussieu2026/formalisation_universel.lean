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
title = "Formaliser des énoncés universels"
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

def s_croissante ( f : ℝ → ℝ )  := ∀ x : ℝ, ∀ y : ℝ, ( x < y) → (f x < f y )

lemma definition.s_croissante ( f : ℝ → ℝ ) :
s_croissante f ↔ ∀ x : ℝ, ∀ y : ℝ, ( x < y) → (f x < f y )
:=
/- dEAduction
pretty_name = "Fonction strictement croissante"
implicit_use = true
-/
begin
    todo
end

def s_decroissante ( f : ℝ → ℝ )  := ∀ x : ℝ, ∀ y : ℝ, ( x < y) → (f y < f x )

lemma definition.decroissante ( f : ℝ → ℝ ) :
s_decroissante f ↔ ∀ x : ℝ, ∀ y : ℝ, ( x < y) → (f y < f x )
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


def nulle (f : ℝ → ℝ )  := ∀ x : ℝ, (f x = 0)

lemma definition.nulle ( f : ℝ → ℝ ) :
nulle f ↔ ∀ x : ℝ, (f x = 0)
:=
/- dEAduction
pretty_name = "Fonction nulle"
-/
begin
    todo
end






namespace formalisation
/- dEAduction
pretty_name = "Formaliser un énoncé universel"
-/


constant JOKER_2: (ℝ→ℝ) → Prop
axiom AXIOMJOKER_2: JOKER_2 = λ f, (∀ x, f x = 0)

lemma exercise.definition_nulle (f: ℝ→ ℝ): (nulle f ↔ JOKER_2 f)  :=
/- dEAduction
pretty_name = "Définition d'une fonction nulle"
description = "Donner la définition d'une fonction nulle"
complete_statement = true
user_proves_statement =  false
available_definitions = "NONE"
-/
begin
  todo
end


constant JOKER_0: (ℝ→ℝ) → Prop
axiom AXIOMJOKER_0: JOKER_0 = λ f, (∀ x, f x = f (-x))
axiom AXIOM0JOKER_0: JOKER_0 = λ f, (∀ x, f (-x) = f x)

lemma exercise.definition_pair (f: ℝ→ ℝ): (paire f ↔ JOKER_0 f)  :=
/- dEAduction
pretty_name = "Définition d'une fonction paire"
description = "Donner la définition d'une fonction paire"
complete_statement = true
user_proves_statement =  false
available_definitions = "NONE"
-/
begin
  todo
end


constant JOKER_1: (ℝ→ℝ) → Prop
axiom AXIOMJOKER_1: JOKER_1 = λ f, (∀ x, f x = f (x+1))
axiom AXIOM0JOKER_1: JOKER_1 = λ f, (∀ x, f (x+1) = f x)

lemma exercise.definition_periodique (f: ℝ→ ℝ): (periodique f ↔ JOKER_1 f)  :=
/- dEAduction
pretty_name = "Définition d'une fonction périodique"
description = "Donner la définition d'une fonction périodique de période 1"
complete_statement = true
user_proves_statement =  false
available_definitions = "NONE"
-/
begin
  todo
end


constant JOKER_3: ℝ → ℝ → Prop
constant JOKER_4: (ℝ → ℝ) → ℝ → ℝ → Prop
axiom AXIOMJOKER_3: JOKER_3 = λ x y, x < y 
axiom AXIOMJOKER_4: JOKER_4 = λ f x y, (f x < f y)


lemma exercise.definition_croissante (f: ℝ→ ℝ): (s_croissante f ↔ 
(∀ x y , (JOKER_3 x y → JOKER_4 f x y)))  :=
/- dEAduction
pretty_name = "Définition d'une fonction strictement croissante"
description = "Donner la définition d'une fonction strictement croissante"
complete_statement = true
user_proves_statement =  false
available_definitions = "NONE"
-/
begin
  todo
end


constant JOKER_5: (ℝ→ℝ) → Prop
axiom AXIOMJOKER_5: JOKER_5 = λ f, (∀ x y, (x < y) → (f x  > f y))
axiom AXIOM0JOKER_5: JOKER_5 = λ f, (∀ x y, (y > x) → (f x  > f y))
axiom AXIOM1JOKER_5: JOKER_5 = λ f, (∀ x y, (x < y) → (f y  < f x))
axiom AXIOM2JOKER_5: JOKER_5 = λ f, (∀ x y, (y > x) → (f y  < f x))


lemma exercise.definition_decroissante (f: ℝ→ ℝ): (s_decroissante f ↔ JOKER_5 f)
:=
/- dEAduction
pretty_name = "Définition d'une fonction strictement décroissante"
description = "Donner la définition d'une fonction strictement décroissante"
complete_statement = true
user_proves_statement =  false
available_definitions = "NONE"
-/
begin
  todo
end




end formalisation


end course






