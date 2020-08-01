import data.real.basic
import data.set
import tactic

namespace tactic.interactive
open lean.parser tactic interactive
open interactive (loc.ns)
open interactive.types
open tactic expr
local postfix *:9001 := many -- necessary for ident*


def separator_comma := "¿, "
def separator_equal := " ¿= "
def open_paren := "¿("
def closed_paren := "¿)"
def open_bra := "¿["
def closed_bra := "¿]"


-- set_option trace.eqn_compiler.elim_match true

/- When e is a pi or lambda expr, instanciate e returns
a local constant a that stands for the first bound variable,
and the body of a with the free variable replaced by a -/
meta def instanciate (e : expr) : tactic (expr × expr) :=
match e with
| (pi pp_name binder type body) := do
    a ← mk_local' pp_name binder type,
    let inst_body := instantiate_var body a,
    return (a , inst_body)
| (lam pp_name binder type body) := do
    a ← mk_local' pp_name binder type,
    let inst_body := instantiate_var body a,
    return (a , inst_body)
| _ := return (e, e)
end



/- Decompose the root of an expression (just one step)
BEWARE, propositions should either start by "PROP" or "QUANT"
    since this is how dEAduction distinguish between objects and props -/
private meta def analysis_expr_step  (e : expr) : tactic (string × (list expr)) :=
do  S ←  (tactic.pp e), let e_joli := to_string S,
match e with
------------------------- LOGIC -------------------------
| `(%%p ∧ %%q) := return ("PROP_AND", [p,q])
| `(%%p ∨ %%q) := return ("PROP_OR", [p,q])
| `(%%p ↔ %%q) := return ("PROP_IFF", [p,q])
| `(¬ %%p) := return ("PROP_NOT", [p])
| `(%%p → false)  := return ("PROP_NOT", [p])
| `(false) := return ("PROP_FALSE",[])
| `(ℕ → %%X) := return ("SEQUENCE", [X])
| `(%%I → _root_.set %%X) := return ("SET_FAMILY", [I,X])
| (pi name binder type body) := do let is_arr := is_arrow e,
    if is_arr then do is_pro ← tactic.is_prop e,
        if is_pro
            then return ("PROP_IMPLIES", [type,body])
            else return ("FUNCTION", [type,body])
     else do (var_, inst_body) ← instanciate e,
               return ("QUANT_∀", [type, var_, inst_body])
| `(Exists %%p) := do match p with
    | (lam name binder type body) :=
            do (var_, inst_body) ← instanciate p,
                is_pro ← is_prop type,
                if is_pro
                    then return ("PROP_∃", [type, inst_body]) -- we do not care about var_
                    else return ("QUANT_∃", [type, var_, inst_body])
    |  _ := return ("ERROR", [])
    end
------------------------- SET THEORY -------------------------
| `(%%A ∩ %%B) := return ("SET_INTER", [A,B])
| `(%%A ∪ %%B) := return ("SET_UNION", [A,B])
| `(set.compl %%A) := return ("SET_COMPLEMENT", [A])
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
| `(_root_.set %%X) := return ("SET", [X])
-- polymorphic
| `(%%a = %%b) := return ("PROP_EQUAL", [a,b]) -- does not provide the type
| `(%%a ≠ %%b) := return ("PROP_EQUAL_NOT", [a,b])
----------- TOPOLOGY --------------
-- | `(B(%%x, %%r))
| `(%%a < %%b) := return ("PROP_<", [a,b])
| `(%%a ≤ %%b) := return ("PROP_≤", [a,b])
| `(%%a > %%b) := return ("PROP_>", [a,b])
| `(%%a ≥ %%b) := return ("PROP_≥", [a,b])
------------------------------ Leaves with data ---------------------------
| (app fonction argument)   :=
    if is_numeral e
        then return ("NUMBER" ++ open_bra ++ e_joli ++ closed_bra, [])
        else return("APPLICATION", [fonction,argument])
| `(ℝ) := return ("TYPE_NUMBER" ++ open_bra
    ++ "name:ℝ" ++ closed_bra,[])
| `(ℕ) := return ("TYPE_NUMBER"++ open_bra
    ++ "name:ℕ" ++ closed_bra,[])
| (const name list_level)   := return ("CONSTANT" ++ open_bra ++ "name:"
    ++ e_joli ++ "/" ++ to_string name ++ closed_bra, [])
| (sort level.zero) := return ("PROP", [])
| (sort level) := return ("TYPE", [])
| (local_const name pretty_name bi type) := return ("LOCAL_CONSTANT" ++ open_bra
    ++ "name:" ++ to_string pretty_name ++ "/identifier:" ++ to_string name ++ closed_bra, [type])
---------------- Useless for dEAduction ? -------------
| (var nat)       := return ("VAR" ++ open_bra ++ to_string nat ++ closed_bra, [])
| (mvar name pretty_name type)        := return ("METAVAR[" ++ to_string pretty_name ++ "]", [])
| (elet name_var type_var expr body)        := return ("LET["++ to_string name_var ++"]", [type_var,expr,body])
| (macro list something)       := return ("MACRO", [])
| (lam name binder type body)          := return ("lambda[" ++ to_string name ++ "]", [type,body])
end


/- Recursively analysiss an expression using analysis_expr_step,
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
            let S3 := "PROPERTY[" ++ S1b ++ "/pp_type: " ++ et_joli ++ "]"
                ++ separator_equal ++ S2,
            return(S3)
        else  do
            S1b ← analysis_rec e,
            S2 ← analysis_rec expr_t,
            let S3 := "OBJECT[" ++ S1b ++ "]" ++ separator_equal ++ S2,
            return(S3)


/- print a list of strings reflecting objects in the context  -/
meta def hypo_analysis : tactic unit :=
do list_expr ← local_context,
    trace "context:",
    list_expr.mmap (λ h, analysis_expr h >>= trace),
    return ()


/- print the list of all targets -/
meta def targets_analysis : tactic unit :=
do list_expr ← get_goals,
    trace "targets:",
    list_expr.mmap (λ h, analysis_expr h >>= trace),
    return ()


end tactic.interactive