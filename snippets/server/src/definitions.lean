import tactic
import data.real.basic
import data.set
import data.set.lattice
import logics


namespace tactic.interactive
open lean.parser tactic interactive 
open tactic expr


local postfix *:9001 := many



/- Tente de réécrire le but ou une hypothèse avec un lemme du type "definitions.***"
dans le sens direct, puis dans le sens réciproque -/
-- Ammélioration : utilisation parse location, cf mathlib doc
-- Amélioration vitale : cibler une occurence de la définition
-- Amélioration : pouvoir passer deux hypothèses (ou plus) qui seront combinées en P ∧ Q ; problème = 
-- comment les combiner dans le bon ordre ? 
-- Amélioration : essayer successivement toutes les versions d'un lemme, 
-- terminant par un numéro, e g intersection_2, intersection_ensemble
meta def defi (name : parse ident) (at_hypo : parse (optional (tk "at" *> ident)))
                            : tactic unit :=
do
    let name := "definitions" <.> to_string name, 
    trace ("J'appelle le lemme " ++ to_string name ++ ","),
    expr ← mk_const name,
    -- expr ← get_local name,
    -- expr ← (to_expr ``(%%name)),
    match at_hypo with
    | none :=  do {rewrite_target expr, trace "sur le but, sens direct"}
            <|>  do {rewrite_target expr {symm := tt},
                    trace "sur le but, sens réciproque"}
 --   | `(tk "at" %%hypo) := skip,
    | some hypo := do e ← get_local hypo, 
                    do {rewrite_hyp expr e,
                 trace ("sur l'hypothèse " ++ (to_string hypo) ++", sens direct")}
                <|>  do {rewrite_hyp expr e {symm := tt},
                 trace ("sur l'hypothèse " ++ (to_string hypo) ++", sens réciproque")}
    end


-- à AMELIORER : essayer simp only si ça rate
meta def applique (names : parse ident*) : tactic unit :=
match names with 
    | [H1,H2] := do 
         nom_hyp ← get_unused_name `H,
        n1 ← get_local H1, 
        n2 ← get_local H2,
        «have» nom_hyp none ``(%%n1 %%n2)
    | _ := fail "Il faut deux paramètres exactement"
    end

-- à AMELIORER
meta def appliquetheo (names : parse ident*) : tactic unit :=
match names with 
    | [name,H2] := do 
         nom_hyp ← get_unused_name `H,
        let name := "theoremes" <.> to_string name, 
        n1 ← mk_const name,
        n2 ← get_local H2,
    «have» nom_hyp none ``(%%n1 %%n2)
    | _ := fail "Il faut deux paramètres exactement"
    end

private meta def is_theorem : declaration → bool
| (declaration.defn _ _ _ _ _ _) :=  ff
| (declaration.thm _ _ _ _) := tt
| (declaration.cnst _ _ _ _) := ff
| (declaration.ax _ _ _) := tt

private meta def get_all_theorems : tactic (list name) := 
do
    env ← tactic.get_env,
    pure (environment.fold env [] (λ decl nams,
         if is_theorem decl then 
            declaration.to_name decl :: nams
         else 
            nams))

private meta def name.get_ante_suffix : name → name
| (name.mk_string s1 (name.mk_string s2 p))  := s2
| (name.mk_numeral s1 (name.mk_string s2 p)) := s2
| p := name.anonymous

private meta def is_definition_as (n : name) : tactic bool :=
if (name.get_ante_suffix n = "definition") then return tt else return ff

private meta def is_exercise_as (n : name) : tactic bool :=
if (name.get_ante_suffix n = "exercise") then return tt else return ff

private meta def is_theorem_as (n : name) : tactic bool :=
if (name.get_ante_suffix n = "theorem") then return tt else return ff

meta def print_all_definitions : tactic unit :=
do
    nams ← get_all_theorems,
    def_nams ← list.mfilter is_definition_as nams,
    def_nams.mmap (λ h, tactic.trace h),
    return ()

meta def print_all_exercises : tactic unit :=
do
    nams ← get_all_theorems,
    def_nams ← list.mfilter is_exercise_as nams,
    def_nams.mmap (λ h, tactic.trace h),
    return ()

meta def print_all_theorems : tactic unit :=
do
    nams ← get_all_theorems,
    def_nams ← list.mfilter is_theorem_as nams,
    def_nams.mmap (λ h, tactic.trace h),
    return ()





end tactic.interactive

