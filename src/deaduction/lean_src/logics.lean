import data.set
import tactic

namespace tactic.interactive
open lean.parser tactic interactive 
open interactive.types
open tactic expr

local postfix *:9001 := many

---------------------------
/- LOGIQUE -/
---------------------------
/- ∀.intro  Pour démontrer "∀ x, P(x)", on introduit une variable x -/
meta def qqsintro (name : parse ident) : tactic unit :=
    do nom ← get_unused_name name,
    expr ← tactic.target, match expr with
        | (pi n bi d p) := if p.has_var then do 
                        intro nom
                        else tactic.fail "Le but est un pi-type mais pas un ∀"
        | _ := tactic.fail "Le but n'est pas un pi-type" 
        end

/-  ∀.elim  : applique une propriété universelle sur une variable -/
meta def qqselim (names : parse ident*) : tactic unit :=
match names with
    | [H,x] := do 
        e ← get_local x, 
        hypo ← get_local H,
        type_hypo ← infer_type hypo,
        if (is_pi type_hypo)∧ ¬(is_arrow type_hypo) then do 
            nom ← get_unused_name `H,
            «have» nom none ``(%%hypo %%e)
        else fail "La propriété n'est pas un quel que soit"
    | _ := fail "qqselim demande deux noms" 
    end

meta def qqs (names : parse ident*) : tactic unit :=
match names with
    | [nom] := do qqsintro nom
    | [H,x] := do qqselim [H,x] 
    | _ := fail "qqs requiert le nom de la variable à introduire, ou deux propriétés"
    end
 
/- verison brute -/
meta def existeelim_old (names : parse ident*) : tactic unit :=
match names with 
    | [nom_var, hypo] := do  
        nom_h ← get_local hypo,
        cases_core nom_h [nom_var, hypo]
    | _ := fail "existe  demande un nom de propriété et un nom de variable"
    end


/-  existeelim demande le nom de la variable à introduire + nom de la propriété 
AFER: test de type -/
meta def existeelim (names : parse ident*) : tactic unit :=
match names with 
    | [nom_var, hypo] := do  
        nom_h ← get_local hypo,
        cases_core nom_h [nom_var, hypo],
        nom_h ← get_local hypo,
        expr ← infer_type nom_h, 
        match expr with
            | `(Exists %%p) := do match p with          -- simplifier : cf use
            | (lam name binder type body) := do
                expr ← infer_type type,
                if expr = `(Prop) then do
                    {lem ← to_expr ```(exists_prop),
                    rewrite_hyp lem nom_h, skip}
                else skip
            | _ := skip
            end
        | _ := skip
        end
        -- `[rw [exists_prop nom_h]] 
    | _ := fail "existe  demande un nom de propriété et un nom de variable"
    end


-- obsolète
meta def existeelim' (hyp : parse ident) (nom : parse (tk "with" *> ident)) : tactic unit :=
 do
    nom_h ← get_local hyp,
    cases_core nom_h [nom, hyp],
    lem ← to_expr ```(exists_prop), -- !! fail si il n'y a pas de second ∃ caché
    nom_h ← get_local hyp,
    rewrite_hyp lem nom_h, 
    skip


meta def existeelim'' (hyp : parse ident) (nom : parse (tk "with" *> ident)) : tactic unit :=
 do
   nom_h ← get_local hyp,
   cases_core nom_h [nom, hyp],
   nom_h ← get_local hyp,
   expr ← infer_type nom_h, 
   match expr with
    | `(Exists %%p) := do match p with          -- simplifier : cf use
        | (lam name binder type body) := do
        expr ← infer_type type,
        if expr = `(Prop) then do
            {lem ← to_expr ```(exists_prop),
            rewrite_hyp lem nom_h, skip}
        else skip
        | _ := skip
        end
    | _ := skip
    end

/- existeintro utilise l'expression fournie dans la tactique use
AFER : test de type inutile puisque c'est fait par use
NB : use is more friendly than existsi (apply triv) -/
meta def existeintro (e : parse pexpr_list_or_texpr) : tactic unit :=
use e


/- Pour le moment ce qui suit ne marche pas (pas essentiel) -/
meta def existe (names : parse ident*) (expr : parse pexpr_list_or_texpr) : tactic unit :=
match names with 
    | [x,H] := do trace "j'élimine ∃", 
                loc ← get_local H,
                existeelim [H,x]
    | []    := do trace "j'introduis ∃",  use expr
    | _     := fail "Erreur"
    end
-- l : parse pexpr_list_or_texpr)



/- La tactique suivante traite les conjonctions
 elle décompose un but, ou bien une hypothèse fournie, si c'est une conjection,
 ou bien elle produit la conjonction de deux hypothèses fournies -/ 
meta def ET (names : parse ident*) : tactic unit :=
match names with
-- Sur le but
| [] := do  expr ← tactic.target, match expr with
    | `(%%P ∧ %%Q) := do split
    | _ := tactic.fail "Le but n'est pas une conjonction" 
    end
-- Sur une propriété : P ∧ Q -> P,Q
| [name] := do  
    expr ← get_local name,
    expr_t ←  infer_type expr,
    match expr_t with 
        | `(%%P ∧ %%Q) := do 
            n1 ← get_unused_name `HA, 
            n2 ← get_unused_name `HB,
            cases_core expr [n1, n2]
        | _ := tactic.fail "La propriété n'est pas une conjonction" 
        end
-- Sur deux propriétés : P,Q -> P ∧ Q
| [n, n'] := do  name ← get_unused_name `H,
    e ← get_local n, e' ← get_local n',
    «have» name none ``(and.intro %%e %%e')
| _ := tactic.fail "Pas plus de deux à la fois"
end

/- OU suivi de gauche ou droite choisit le nouveau but dans une disjonction
 OU suivi d'une hypothèse qui est une disjonction fait brancher la preuve  -/
meta def OU (name : parse ident)  :  tactic unit :=
match name with
-- Sur le but : droite ou gauche
| "gauche" := do  expr ← tactic.target, 
    match expr with
    | `(%%P ∨ %%Q) := do left
    | _ := tactic.fail "Le but n'est pas une disjonction" 
    end
| "droite" := do  expr ← tactic.target, 
    match expr with
    | `(%%P ∨ %%Q) := do right
    | _ := tactic.fail "Le but n'est pas une disjonction" 
    end
-- Sur une propriété : P ∨ Q -> sépare en deux buts
| _ := do  
    expr ← get_local name,
    expr_t ←  infer_type expr,
    match expr_t with 
    | `(%%P ∨ %%Q) := do 
            n1 ← get_unused_name `HA, 
            n2 ← get_unused_name `HB,
            cases_core expr [n1, n2]
    | _ := tactic.fail "La propriété n'est pas une disjonction" 
    end
-- | _ := tactic.fail "emploi illicite de OU"
end

/- A partir 'une propriété P vraie donnée par son nom, 
et d'une propriété Q quelconque donnée par une expression,
on déduit la propriété "P ou Q"
Il manque les variantes. Le choix de les incorporer dépend de la façon dont on gère
la commutativité de "ou". -/
meta def OUd (nom : parse ident) : parse texpr →  tactic unit
| expr2 := do
    expr1 ← get_local nom,
    name ← get_unused_name `H,
    «have» name none ``((or.intro_left %%expr2) %%expr1)
-- A FINIR : de P on déduit "P ou Q" pour n'importe quel Q
-- nom1, nom2 donné dans l'ordre, renvoie nom1 ∨ nom2
--| nom , expr := do { exp1 ← get_local  nom1, exp2 ← get_local  nom2, 
--                  name ← get_unused_name `H, 
--                «have» name none ``((or.intro_left %%exp2) %%exp1)
--                } <|> trace "raté"



-- meta def NON : tactic unit := sorry


/- implique.intro -/
meta def impliqueintro : tactic unit :=
    do nom ← get_unused_name `H,
    expr ← tactic.target, match expr with
        | (pi n bi d p) := if p.has_var then do 
                        tactic.fail "Le but est un ∀, pas un implique"
                        else intro nom
        | _ := tactic.fail "Le but n'est pas un pi-type" 
        end

meta def impliqueelim (names : parse ident*) : tactic unit :=
match names with
    | [H,x] := do 
        e ← get_local x, 
        hypo ← get_local H,
        type_hypo ← infer_type hypo,
        if (is_arrow type_hypo) then do 
            nom ← get_unused_name `H,
            «have» nom none ``(%%hypo %%e)
        else fail "La propriété n'est pas une implication"
    | _ := skip
    end

meta def implique  (names : parse ident*) : tactic unit :=
match names with
    | [H,x] := do impliqueelim [H,x]
    | [] := do impliqueintro
    | _ := tactic.fail "implique reçoit zero ou deux objets"
    end

end tactic.interactive
