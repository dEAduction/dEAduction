/-
This files provides the tactics 
    hypo_analysis
    targets_analysis
which output a string reflecting the lean expr for objects in the
and in the target. The key function is analysis_expr_step that pattern
matches an object to determine a short string reflecting its node
(e.g., "INCLUSION"), and children (e.g. here, corresponding to the left 
and righ hand side of the inclusion property).
The two tactics also provides the types of all intermediate objects.

Authors: Frédéric Le Roux
-/

import data.set
import data.real.basic
import tactic
import parser_analysis_definitions

import user_notations

namespace tactic.interactive
open lean.parser tactic interactive
open interactive (loc.ns)
open interactive.types
open tactic expr
local postfix *:9001 := many -- necessary for ident*

set_option pp.width 1000 -- We do not want CR inside our strings

def separator_object := "¿¿¿"
def separator_comma := "¿, "
def separator_equal := "¿= "
def separator_slash := "¿/ "
def open_paren := "¿("
def closed_paren := "¿)"
def open_bra := "¿["
def closed_bra := "¿]"

-- set_option trace.eqn_compiler.elim_match true

/- When e is a pi or lambda expr, instanciate e returns
a local constant a that stands for the first bound variable,
and the body of a with the free variable replaced by a.
The name of 'a' is enriched with suffix 'BoundVar'. -/
meta def instanciate (e : expr) : tactic (expr × expr) :=
match e with
| (pi pp_name binder type body) := do
    let pp_name := mk_str_name pp_name "BoundVar",
--    pp_name ← get_unused_name pp_name,      -- does not do the job
    -- trace ("Instantiation name: " ++ to_string pp_name),
    a ← mk_local' pp_name binder type,
    let inst_body := instantiate_var body a,
    return (a , inst_body)
| (lam pp_name binder type body) := do
    let pp_name := mk_str_name pp_name "BoundVar", -- trial
--    pp_name ← get_unused_name pp_name,
    -- trace ("Instantiation name: " ++ to_string pp_name),
    a ← mk_local' pp_name binder type,
    let inst_body := instantiate_var body a,
    return (a , inst_body)
| _ := return (e, e)
end



open set

/- The key function. Decompose the root of an expression (just one step)
General types should be at the end.
-/


private meta def analysis_expr_step  (e : expr) : tactic (string × (list expr)) :=
do  S ←  (tactic.pp e), let e_joli := to_string S,
match e with
------------------------- LOGIC -------------------------
| `(%%p ∧ %%q) := return ("PROP_AND", [p,q])
| `(%%p ∨ %%q) := return ("PROP_OR", [p,q])
| `(%%p ↔ %%q) := return ("PROP_IFF", [p,q])
-- various negations
| `(%%a ≠ %%b) := return ("PROP_EQUAL_NOT", [a,b])
| `(¬ %%a = %%b) := return ("PROP_EQUAL_NOT", [a,b])
| `(%%a ∉ %%A) := return ("PROP_NOT_BELONGS", [a,A])
| `(¬ %%p) := return ("PROP_NOT", [p])
| `(%%p → false)  := return ("PROP_NOT", [p])
| `(false) := return ("PROP_FALSE",[])
------------------------- SET THEORY -------------------------
| `(%%A ∩ %%B) := return ("SET_INTER", [A,B])
| `(%%A ∪ %%B) := return ("SET_UNION", [A,B])
| `(set.compl %%A) := do e_type ← infer_type e, match e_type with
    | `(_root_.set %%X) := return ("SET_COMPLEMENT", [X, A])
    | _ := return ("", [])
    end
-- | `(set.symmetric_difference %%A %%B) := return ("SET_DIFF_SYM", [A,B])
| `(%%A \ %%B) := return ("SET_DIFF", [A,B])
| `(%%A ⊆ %%B) := return ("PROP_INCLUDED", [A,B])
| `(%%a ∈ %%A) := return ("PROP_BELONGS", [a,A])
| `(@set.univ %%X) := return ("SET_UNIVERSE", [X])
| `(-%%A) := return ("MINUS", [A])
| `(set.Union %%A) := return ("SET_UNION+", [A])
| `(set.Inter %%A) := return ("SET_INTER+", [A])
| `(%%f '' %%A) := return ("SET_IMAGE", [f,A])
| `(%%f  ⁻¹' %%A) := return ("SET_INVERSE", [f,A])
| `(∅) := return ("SET_EMPTY", [])
| `({%%x, %%x', %%x''}) := return ("SET_EXTENSION3", [x, x', x''])
| `({%%x, %%x'}) := return ("SET_EXTENSION2", [x, x'])
| `({%%x}) := return ("SET_EXTENSION1", [x])
-- | `(triplet %%x %%x' %%x'') := return ("SET_EXTENSION3", [x, x', x''])
| `(pair %%x %%x') := return ("SET_EXTENSION2", [x, x'])
| `(sing %%x) := return ("SET_EXTENSION1", [x])
| `(_root_.set %%X) := return ("SET", [X])
| `(set.prod %%A %%B) := return ("SET_PRODUCT", [A, B])
| `(prod.mk %%x %%y) := return ("COUPLE", [x, y])
-- set in extension, e.g. A = {x | P x} or A = {x:X | P x} :
| `(@set_of %%X %%P) := match P with
    | (lam name binder type body) :=
            do (var_, inst_body) ← instanciate P,
                return ("SET_INTENSION",[X, var_, inst_body])
    | _ := return ("SET_INTENSION", [X, P])
    end
| `(index_set) := return ("TYPE", [])
| `(set_family %%I %%X) := return ("SET_FAMILY", [I, X])
-- | `(seq %%X) := return ("SEQUENCE", [X])
| (pi name binder type body) := do
    let is_arr := is_arrow e,
    if is_arr
        then do
            is_pro ← tactic.is_prop e,
            if is_pro
                then return ("PROP_IMPLIES", [type,body])
            else match e with
                | `(%%X → %%Y) := match (X,Y) with
                    -- | (`(ℕ), `(ℕ)) := return ("SEQUENCE", [X, Y])
                    -- | (`(ℕ), `(ℤ)) := return ("SEQUENCE", [X, Y])
                    -- | (`(ℕ), `(ℚ)) := return ("SEQUENCE", [X, Y])
                    -- | (`(ℕ), `(ℝ)) := return ("SEQUENCE", [X, Y])
                    | (`(ℕ), _) := return ("SEQUENCE", [X, Y])
                    | _ := do X_type ← infer_type X,
                        match (X_type, Y) with
                    -- A set family is when source is an index_set
                    -- (just a type which is "tagged" for serving as index)
                    -- and target is "set something"
                        | (`(index_set), `(_root_.set %%Z)) := return ("SET_FAMILY", [X, Z])
                        | _ := return ("FUNCTION", [X, Y])
                        end
                    end
                | _ := return ("ERROR", [])
                end
        else do
            (var_, inst_body) ← instanciate e,
            return ("QUANT_∀", [type, var_, inst_body])
| `(Exists %%p) := do match p with
    | (lam name binder type body) :=
            do (var_, inst_body) ← instanciate p,
                is_pro ← is_prop type,
                if is_pro
                    then return ("PROP_∃", [type, inst_body]) -- we do not care about var_
                    else return ("QUANT_∃", [type, var_, inst_body])
    |  _ := do p_type ← infer_type p, match p_type with
        | `(%%type → Prop) :=  do Q  ← to_expr ``(λ x: %%type,  (%%p x)), -- Do not work properly
                                (var_, inst_body) ← instanciate Q,
                                is_pro ← is_prop type,
                if is_pro
                    then return ("PROP_∃", [type, inst_body]) -- we do not care about var_
                    else return ("QUANT_∃", [type, var_, inst_body])
        | _ := return ("ERROR", [])
        end
    end
| `(exists_unique %%P) := do match P with
    | (lam name binder type body)   :=
            do (var_, inst_body) ← instanciate P,
            return ("QUANT_∃!", [type, var_, inst_body])
    |  _                            := return ("ERROR", [])
    end
-- polymorphic
| `(%%a = %%b) := return ("PROP_EQUAL", [a,b]) -- does not provide the type
----------- TOPOLOGY --------------
-- | `(B(%%x, %%r))
------------ ORDER ----------------
| `(%%a < %%b) := return ("PROP_<", [a,b])
| `(%%a ≤ %%b) := return ("PROP_≤", [a,b])
| `(%%a > %%b) := return ("PROP_>", [a,b])
| `(%%a ≥ %%b) := return ("PROP_≥", [a,b])
------------ ARITHMETIC ------------
| `(↑%%a)      := return ("COE", [a])
| `(%%a + %%b) := return ("SUM", [a, b])
| `(%%a - %%b) := return ("DIFFERENCE", [a, b])
| `(has_mul.mul %%a %%b) := return ("MULT", [a, b]) -- TODO: distinguish types/numbers
| `(%%a × %%b) := return ("PRODUCT", [a, b]) -- TODO: distinguish types/numbers
| `(%%a / %%b) := return ("DIV", [a, b])
| `(%%a ^ %%b) := return ("POWER", [a, b])
| `(real.sqrt %%a) := return ("SQRT", [a])
------------------------------ Leaves with data ---------------------------
| (app function argument)   :=
    if is_numeral e
        then return ("NUMBER" ++ open_bra ++ "value: " ++ e_joli ++ closed_bra, [])
        else return("APPLICATION", [function,argument])
-- | `(%%I → _root_.set %%X) := return ("SET_FAMILY", [I,X])
-- | `(ℝ) := return ("TYPE_NUMBER" ++ open_bra
--    ++ "name: ℝ" ++ closed_bra,[])
--| `(ℕ) := return ("TYPE_NUMBER"++ open_bra
--     ++ "name: ℕ" ++ closed_bra,[])
| (const name list_level)   :=
            return ("CONSTANT" ++ open_bra ++ "name: " ++ e_joli ++ closed_bra, [])
| (sort level.zero) := return ("PROP", [])
| (sort level) := return ("TYPE", [])
| (local_const name pretty_name bi type) :=
            return ("LOCAL_CONSTANT" ++ open_bra ++ "name: " ++ to_string pretty_name
            ++ separator_slash ++ "identifier: " ++ to_string name ++ closed_bra, [])
---------------- Other structures -------------
| (var nat)       :=
            return ("VAR" ++ open_bra ++ to_string nat ++ closed_bra, [])
| (mvar name pretty_name type)        :=
            return ("METAVAR" ++ open_bra ++ "name: " ++ to_string pretty_name ++ closed_bra, [])
| (elet name_var type_var expr body) :=
            return ("LET"++ open_bra ++ to_string name_var ++ closed_bra, [type_var,expr,body])
| (macro list something)       := return ("MACRO", [])
| (lam name binder type body)          :=
            do (var_, inst_body) ← instanciate e,
                return ("LAMBDA",[type, var_, inst_body])
end


/- Recursively analyses an expression using analysis_expr_step,
and provides a string with parentheses reflecting the mathematical object-/
private meta def analysis_rec : expr →  tactic string
| e :=
do ⟨string, list_expr⟩ ←  analysis_expr_step(e),
    match list_expr with
    -- BEWARE, case of more than three arguments not implemented
    -- replace by a list.map
    |[e1] :=  do
       string1 ← analysis_rec e1,
       return(string ++ open_paren ++ string1 ++ closed_paren)
    |[e1,e2] :=  do
        string1 ← analysis_rec e1,
        string2 ← analysis_rec e2,
        return (string ++ open_paren ++ string1 ++ separator_comma ++ string2 ++ closed_paren)
    |[e1,e2,e3] :=  do
        string1 ← analysis_rec e1,
        string2 ← analysis_rec e2,
        string3 ← analysis_rec e3,
        return (string ++ open_paren ++ string1 ++ separator_comma ++ string2 ++ separator_comma ++ string3 ++ closed_paren)
    | _ :=    return(string)
    end


meta def analysis_expr : expr →  tactic string
| e := do
    expr_t ←  infer_type e,
    is_pro ← is_prop expr_t,
    if is_pro then do
            S ←  (tactic.pp expr_t), let et_joli := to_string S,
            S1b ← analysis_rec e,
            S2 ← analysis_rec expr_t,
            let S3 := "PROPERTY" ++ open_bra ++ "identifier: " ++ S1b ++ separator_slash
                        ++ "pp_type: " ++ et_joli ++ closed_bra ++ separator_equal ++ S2,
            return(S3)
        else  do
            S1b ← analysis_rec e,
            S2 ← analysis_rec expr_t,
            let S3 := "OBJECT" ++ open_bra ++ S1b ++ closed_bra
                        ++ separator_equal ++ S2,
            return(S3)

/- Recursively analyses an expression using analysis_expr_step,
and provides a string with parentheses reflecting the mathematical object,
with types-/
private meta def analysis_rec_with_types : expr →  tactic string
| e :=
do ⟨string, list_expr⟩ ←  analysis_expr_step(e),
    -- trace ("analysing e: " ++ to_string e),
    if is_local_constant e
        then return(string)
        else do
    e_type ← infer_type e,
    -- trace "analysing e_type",
    string_type ← analysis_rec e_type,
    let str_with_type := string ++ open_bra ++ "type: " ++ string_type ++ closed_bra,
    -- trace str_with_type,
    match list_expr with
    -- BEWARE, case of more than three arguments not implemented
    -- replace by a list.map
    |[e1] :=  do
       string1 ← analysis_rec_with_types e1,
       return(str_with_type ++ open_paren ++ string1 ++ closed_paren)
    |[e1,e2] :=  do
        string1 ← analysis_rec_with_types e1,
        string2 ← analysis_rec_with_types e2,
        return (str_with_type ++ open_paren ++ string1 ++ separator_comma ++ string2 ++ closed_paren)
    |[e1,e2,e3] :=  do
        string1 ← analysis_rec_with_types e1,
        string2 ← analysis_rec_with_types e2,
        string3 ← analysis_rec_with_types e3,
        return (str_with_type ++ open_paren ++ string1 ++ separator_comma ++ string2 ++ separator_comma ++ string3 ++ closed_paren)
    | _ :=    return(str_with_type)
    end

-- set_option pp.all true
meta def analysis_expr_with_types : expr →  tactic string
| e :=
    do
    expr_t ←  infer_type e,
    is_pro ← is_prop expr_t,
    if is_pro then do
            S ←  (tactic.pp expr_t),
            --  insert something like
            -- (options := (options.set_nat pp.width 1000))
            -- in  let et_joli := to_string S,
            -- let et_joli := format.to_string (options.set_nat pp.width 1000) S,
            let et_joli := to_string S,
            S1b ← analysis_rec e,
            S2 ← analysis_rec_with_types expr_t,
            let S3 := separator_object ++ "property"
                ++ open_bra ++ "pp_type: " ++ et_joli ++ closed_bra
                ++ ": " ++ S1b ++ separator_equal ++ S2,
            return(S3)
        else  do
            S1b ← analysis_rec e,
            S2 ← analysis_rec expr_t,
            let S3 := separator_object ++ "object: " ++ S1b ++ separator_equal ++ S2,
            return(S3)

/- print a list of strings reflecting objects in the context  -/
meta def hypo_analysis : tactic unit :=
do list_expr ← local_context,
    trace "context:",
    list_expr.mmap (λ h, analysis_expr_with_types h >>= trace),
    return ()

/- print the list of all targets -/
meta def targets_analysis : tactic unit :=
do list_expr ← get_goals,
    trace "targets:",
    list_expr.mmap (λ h, analysis_expr_with_types h >>= trace),
    return ()



/---------------------------------------------------
----------------------------------------------------
----------------------------------------------------
--------------------- DEBUG ------------------------
----------------------------------------------------
----------------------------------------------------
----------------------------------------------------/

private meta def analyse_expr_step_brut  (e : expr) : tactic (string × (list expr)) :=
match e with
-- autres
| (pi name binder type body ) := return ("pi (nom : " ++ to_string name ++ ")",[type,body])
| (app fonction argument)   := return ("application", [fonction,argument])
| (const name list_level)   := return ("constante :" ++ to_string name, []) -- name → list level → expr
| (var nat)       := return ("var_"++ to_string nat, []) --  nat → expr
| (sort level)      := return ("sort", [])  -- level → expr
| (mvar name pretty_name type)        := return ("metavar", []) -- name → name → expr → expr
| (local_const name pretty_name bi type) := return ("constante_locale :" ++ to_string pretty_name, []) -- name → name → binder_info → expr → expr
| (lam name binder type body)          := return ("lambda (nom : " ++ to_string name ++ ")", [type,body]) -- name → binder_info → expr → expr → expr
| (elet name_var type_var expr body)        := return ("let", []) --name → expr → expr → expr → expr
| (macro liste pas_compris)       := return ("macro", []) -- macro_def → list expr → expr
end

private meta def analyse_rec_brut : expr →  tactic string
| e :=
do ⟨string, liste_expr⟩ ←  analyse_expr_step_brut e,
    match liste_expr with
    -- ATTENTION, cas de plus de trois arguiments non traité
    -- à remplacer par un list.map
    |[e1] :=  do
       string1 ← analyse_rec_brut e1,
       return(string ++ "(" ++ string1 ++ ")")
    |[e1,e2] :=  do
        string1 ← analyse_rec_brut e1,
        string2 ← analyse_rec_brut e2,
         return (string ++ "(" ++ string1 ++ "," ++ string2 ++ ")")
    |[e1,e2,e3] :=  do  -- non utilisé
        string1 ← analyse_rec_brut e1,
        string2 ← analyse_rec_brut e2,
        string3 ← analyse_rec_brut e3,
        return (string ++ "(" ++ string1 ++ "," ++ string2 ++ "," ++ string3 ++ ")")
    | _ :=    return(string)
    end


private meta def analyse_expr_brut : expr →  tactic string
| e := do
    expr_t ←  infer_type e,
    expr_tt ← infer_type expr_t,
    if expr_tt = `(Prop) then do
            S ←  (tactic.pp expr_t),
            let S1 := to_string S,
            S2 ← analyse_rec_brut expr_t,
            let S3 := "PROPRIETE : " ++ S1 ++ " : " ++ S2,
            return(S3)
        else  do let S0 := "OBJET : ",
            let S1 :=  to_string e,
            S2 ← analyse_rec_brut expr_t,
            let S3 := S0 ++ S1 ++ " : "++ S2,
            return(S3)


/- Affiche la liste des objets du contexte, séparés par des retour chariots
format :  "OBJET" ou "PROPRIETE" : affichage Lean : structure -/
meta def analyse_contexte_brut : tactic unit :=
do liste_expr ← local_context,
    trace "Contexte :",
    liste_expr.mmap (λ h, analyse_expr_brut h >>= trace),
    return ()


/- Analyse brute de Lean (dans expr) -/
meta def analyse_raw (names : parse ident*) : tactic unit :=
match names with
    | [] := do goal ← tactic.target,
                trace $ to_raw_fmt goal
    | [nom] := do expr ← get_local nom,
                expr_t ←  infer_type expr,
                trace $ to_raw_fmt expr_t
    | _ := skip
    end




end tactic.interactive


-- example (X Y: Type) (f: set X → set X) (I: set.index_set) (E: I → set X)
-- (F: I → X) (G: I → set (X × Y)) (H: Y → set X):
-- true := 
-- begin
--     hypo_analysis,
-- end

example (X: Type) (P: X → Prop): ∀ x: X, P x :=
begin
    targets_analysis,
end