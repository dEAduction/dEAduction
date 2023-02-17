/-
Copyright (c) 2020 Floris van Doorn. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Floris van Doorn, Robert Y. Lewis, Gabriel Ebner
-/
import tactic.lint.basic

/-!
# Linters about type classes

This file defines several linters checking the correct usage of type classes
and the appropriate definition of instances:

 * `instance_priority` ensures that blanket instances have low priority
 * `has_inhabited_instances` checks that every type has an `inhabited` instance
 * `impossible_instance` checks that there are no instances which can never apply
 * `incorrect_type_class_argument` checks that only type classes are used in
   instance-implicit arguments
 * `dangerous_instance` checks for instances that generate subproblems with metavariables
 * `fails_quickly` checks that type class resolution finishes quickly
 * `has_coe_variable` checks that there is no instance of type `has_coe α t`
 * `inhabited_nonempty` checks whether `[inhabited α]` arguments could be generalized
   to `[nonempty α]`
 * `decidable_classical` checks propositions for `[decidable_... p]` hypotheses that are not used
   in the statement, and could thus be removed by using `classical` in the proof.
-/

open tactic

/-- Pretty prints a list of arguments of a declaration. Assumes `l` is a list of argument positions
and binders (or any other element that can be pretty printed).
`l` can be obtained e.g. by applying `list.indexes_values` to a list obtained by
`get_pi_binders`. -/
meta def print_arguments {α} [has_to_tactic_format α] (l : list (ℕ × α)) : tactic string := do
  fs ← l.mmap (λ ⟨n, b⟩, (λ s, to_fmt "argument " ++ to_fmt (n+1) ++ ": " ++ s) <$> pp b),
  return $ fs.to_string_aux tt

/-- checks whether an instance that always applies has priority ≥ 1000. -/
private meta def instance_priority (d : declaration) : tactic (option string) := do
  let nm := d.to_name,
  b ← is_instance nm,
  /- return `none` if `d` is not an instance -/
  if ¬ b then return none else do
  (is_persistent, prio) ← has_attribute `instance nm,
  /- return `none` if `d` is has low priority -/
  if prio < 1000 then return none else do
  let (fn, args) := d.type.pi_codomain.get_app_fn_args,
  cls ← get_decl fn.const_name,
  let (pi_args, _) := cls.type.pi_binders,
  guard (args.length = pi_args.length),
  /- List all the arguments of the class that block type-class inference from firing
    (if they are metavariables). These are all the arguments except instance-arguments and
    out-params. -/
  let relevant_args := (args.zip pi_args).filter_map $ λ⟨e, ⟨_, info, tp⟩⟩,
    if info = binder_info.inst_implicit ∨ tp.get_app_fn.is_constant_of `out_param
    then none else some e,
  let always_applies := relevant_args.all expr.is_var ∧ relevant_args.nodup,
  if always_applies then return $ some "set priority below 1000" else return none

/--
Certain instances always apply during type-class resolution. For example, the instance
`add_comm_group.to_add_group {α} [add_comm_group α] : add_group α` applies to all type-class
resolution problems of the form `add_group _`, and type-class inference will then do an
exhaustive search to find a commutative group. These instances take a long time to fail.
Other instances will only apply if the goal has a certain shape. For example
`int.add_group : add_group ℤ` or
`add_group.prod {α β} [add_group α] [add_group β] : add_group (α × β)`. Usually these instances
will fail quickly, and when they apply, they are almost the desired instance.
For this reason, we want the instances of the second type (that only apply in specific cases) to
always have higher priority than the instances of the first type (that always apply).
See also #1561.

Therefore, if we create an instance that always applies, we set the priority of these instances to
100 (or something similar, which is below the default value of 1000).
-/
library_note "lower instance priority"

/--
Instances that always apply should be applied after instances that only apply in specific cases,
see note [lower instance priority] above.

Classes that use the `extends` keyword automatically generate instances that always apply.
Therefore, we set the priority of these instances to 100 (or something similar, which is below the
default value of 1000) using `set_option default_priority 100`.
We have to put this option inside a section, so that the default priority is the default
1000 outside the section.
-/
library_note "default priority"

/-- A linter object for checking instance priorities of instances that always apply.
This is in the default linter set. -/
@[linter] meta def linter.instance_priority : linter :=
{ test := instance_priority,
  no_errors_found := "All instance priorities are good",
  errors_found := "DANGEROUS INSTANCE PRIORITIES.
The following instances always apply, and therefore should have a priority < 1000.
If you don't know what priority to choose, use priority 100.

If this is an automatically generated instance (using the keywords `class` and `extends`),
see note [lower instance priority] and see note [default priority] for instructions to change the priority",
  auto_decls := tt }

/-- Reports declarations of types that do not have an associated `inhabited` instance. -/
private meta def has_inhabited_instance (d : declaration) : tactic (option string) := do
tt ← pure d.is_trusted | pure none,
ff ← has_attribute' `reducible d.to_name | pure none,
ff ← has_attribute' `class d.to_name | pure none,
(_, ty) ← mk_local_pis d.type,
ty ← whnf ty,
if ty = `(Prop) then pure none else do
`(Sort _) ← whnf ty | pure none,
insts ← attribute.get_instances `instance,
insts_tys ← insts.mmap $ λ i, expr.pi_codomain <$> declaration.type <$> get_decl i,
let inhabited_insts := insts_tys.filter (λ i,
  i.app_fn.const_name = ``inhabited ∨ i.app_fn.const_name = `unique),
let inhabited_tys := inhabited_insts.map (λ i, i.app_arg.get_app_fn.const_name),
if d.to_name ∈ inhabited_tys then
  pure none
else
  pure "inhabited instance missing"

/-- A linter for missing `inhabited` instances. -/
@[linter]
meta def linter.has_inhabited_instance : linter :=
{ test := has_inhabited_instance,
  auto_decls := ff,
  no_errors_found := "No types have missing inhabited instances",
  errors_found := "TYPES ARE MISSING INHABITED INSTANCES",
  is_fast := ff }

attribute [nolint has_inhabited_instance] pempty

/-- Checks whether an instance can never be applied. -/
private meta def impossible_instance (d : declaration) : tactic (option string) := do
  tt ← is_instance d.to_name | return none,
  (binders, _) ← get_pi_binders_dep d.type,
  let bad_arguments := binders.filter $ λ nb, nb.2.info ≠ binder_info.inst_implicit,
  _ :: _ ← return bad_arguments | return none,
  (λ s, some $ "Impossible to infer " ++ s) <$> print_arguments bad_arguments

/-- A linter object for `impossible_instance`. -/
@[linter] meta def linter.impossible_instance : linter :=
{ test := impossible_instance,
  auto_decls := tt,
  no_errors_found := "All instances are applicable",
  errors_found := "IMPOSSIBLE INSTANCES FOUND.
These instances have an argument that cannot be found during type-class resolution, and therefore can never succeed. Either mark the arguments with square brackets (if it is a class), or don't make it an instance" }

/-- Checks whether an instance can never be applied. -/
private meta def incorrect_type_class_argument (d : declaration) : tactic (option string) := do
  (binders, _) ← get_pi_binders d.type,
  let instance_arguments := binders.indexes_values $
    λ b : binder, b.info = binder_info.inst_implicit,
  /- the head of the type should either unfold to a class, or be a local constant.
  A local constant is allowed, because that could be a class when applied to the
  proper arguments. -/
  bad_arguments ← instance_arguments.mfilter (λ ⟨_, b⟩, do
    (_, head) ← mk_local_pis b.type,
    if head.get_app_fn.is_local_constant then return ff else do
    bnot <$> is_class head),
  _ :: _ ← return bad_arguments | return none,
  (λ s, some $ "These are not classes. " ++ s) <$> print_arguments bad_arguments

/-- A linter object for `incorrect_type_class_argument`. -/
@[linter] meta def linter.incorrect_type_class_argument : linter :=
{ test := incorrect_type_class_argument,
  auto_decls := tt,
  no_errors_found := "All declarations have correct type-class arguments",
  errors_found := "INCORRECT TYPE-CLASS ARGUMENTS.
Some declarations have non-classes between [square brackets]" }

/-- Checks whether an instance is dangerous: it creates a new type-class problem with metavariable
arguments. -/
private meta def dangerous_instance (d : declaration) : tactic (option string) := do
  tt ← is_instance d.to_name | return none,
  (local_constants, target) ← mk_local_pis d.type,
  let instance_arguments := local_constants.indexes_values $
    λ e : expr, e.local_binding_info = binder_info.inst_implicit,
  let bad_arguments := local_constants.indexes_values $ λ x,
      !target.has_local_constant x &&
      (x.local_binding_info ≠ binder_info.inst_implicit) &&
      instance_arguments.any (λ nb, nb.2.local_type.has_local_constant x),
  let bad_arguments : list (ℕ × binder) := bad_arguments.map $ λ ⟨n, e⟩, ⟨n, e.to_binder⟩,
  _ :: _ ← return bad_arguments | return none,
  (λ s, some $ "The following arguments become metavariables. " ++ s) <$> print_arguments bad_arguments

/-- A linter object for `dangerous_instance`. -/
@[linter] meta def linter.dangerous_instance : linter :=
{ test := dangerous_instance,
  no_errors_found := "No dangerous instances",
  errors_found := "DANGEROUS INSTANCES FOUND.\nThese instances are recursive, and create a new type-class problem which will have metavariables.
  Possible solution: remove the instance attribute or make it a local instance instead.

  Currently this linter does not check whether the metavariables only occur in arguments marked with `out_param`, in which case this linter gives a false positive.",
  auto_decls := tt }

/-- Applies expression `e` to local constants, but lifts all the arguments that are `Sort`-valued to
  `Type`-valued sorts. -/
meta def apply_to_fresh_variables (e : expr) : tactic expr := do
t ← infer_type e,
(xs, b) ← mk_local_pis t,
xs.mmap' $ λ x, try $ do {
  u ← mk_meta_univ,
  tx ← infer_type x,
  ttx ← infer_type tx,
  unify ttx (expr.sort u.succ) },
return $ e.app_of_list xs

/-- Tests whether type-class inference search for a class will end quickly when applied to
  variables. This tactic succeeds if `mk_instance` succeeds quickly or fails quickly with the error
  message that it cannot find an instance. It fails if the tactic takes too long, or if any other
  error message is raised.
  We make sure that we apply the tactic to variables living in `Type u` instead of `Sort u`,
  because many instances only apply in that special case, and we do want to catch those loops. -/
meta def fails_quickly (max_steps : ℕ) (d : declaration) : tactic (option string) := do
  e ← mk_const d.to_name,
  tt ← is_class e | return none,
  e' ← apply_to_fresh_variables e,
  sum.inr msg ← retrieve_or_report_error $ tactic.try_for max_steps $
    succeeds_or_fails_with_msg (mk_instance e')
      $ λ s, "tactic.mk_instance failed to generate instance for".is_prefix_of s | return none,
  return $ some $
    if msg = "try_for tactic failed, timeout" then "type-class inference timed out" else msg

/-- A linter object for `fails_quickly`. If we want to increase the maximum number of steps
  type-class inference is allowed to take, we can increase the number `3000` in the definition.
  As of 5 Mar 2020 the longest trace (for `is_add_hom`) takes 2900-3000 "heartbeats". -/
@[linter] meta def linter.fails_quickly : linter :=
{ test := fails_quickly 3000,
  auto_decls := tt,
  no_errors_found := "No type-class searches timed out",
  errors_found := "TYPE CLASS SEARCHES TIMED OUT.
For the following classes, there is an instance that causes a loop, or an excessively long search.",
  is_fast := ff }

/--
Tests whether there is no instance of type `has_coe α t` where `α` is a variable,
or `has_coe t α` where `α` does not occur in `t`.
See note [use has_coe_t].
-/
private meta def has_coe_variable (d : declaration) : tactic (option string) := do
tt ← is_instance d.to_name | return none,
`(has_coe %%a %%b) ← return d.type.pi_codomain | return none,
if a.is_var then
  return $ some $ "illegal instance, first argument is variable"
else if b.is_var ∧ ¬ b.occurs a then
  return $ some $ "illegal instance, second argument is variable not occurring in first argument"
else
  return none

/-- A linter object for `has_coe_variable`. -/
@[linter] meta def linter.has_coe_variable : linter :=
{ test := has_coe_variable,
  auto_decls := tt,
  no_errors_found := "No invalid `has_coe` instances",
  errors_found := "INVALID `has_coe` INSTANCES.
Make the following declarations instances of the class `has_coe_t` instead of `has_coe`." }

/-- Checks whether a declaration is prop-valued and takes an `inhabited _` argument that is unused
elsewhere in the type. In this case, that argument can be replaced with `nonempty _`. -/
private meta def inhabited_nonempty (d : declaration) : tactic (option string) :=
do tt ← is_prop d.type | return none,
   (binders, _) ← get_pi_binders_dep d.type,
   let inhd_binders := binders.filter $ λ pr, pr.2.type.is_app_of `inhabited,
   if inhd_binders.length = 0 then return none
   else (λ s, some $ "The following `inhabited` instances should be `nonempty`. " ++ s) <$>
      print_arguments inhd_binders

/-- A linter object for `inhabited_nonempty`. -/
@[linter] meta def linter.inhabited_nonempty : linter :=
{ test := inhabited_nonempty,
  auto_decls := ff,
  no_errors_found := "No uses of `inhabited` arguments should be replaced with `nonempty`",
  errors_found := "USES OF `inhabited` SHOULD BE REPLACED WITH `nonempty`." }

/-- Checks whether a declaration is `Prop`-valued and takes a `decidable* _` hypothesis that is unused
elsewhere in the type. In this case, that hypothesis can be replaced with `classical` in the proof. -/
private meta def decidable_classical (d : declaration) : tactic (option string) :=
do tt ← is_prop d.type | return none,
   (binders, _) ← get_pi_binders_dep d.type,
   let deceq_binders := binders.filter $ λ pr, pr.2.type.is_app_of `decidable_eq
     ∨ pr.2.type.is_app_of `decidable_pred ∨ pr.2.type.is_app_of `decidable_rel
     ∨ pr.2.type.is_app_of `decidable,
   if deceq_binders.length = 0 then return none
   else (λ s, some $ "The following `decidable` hypotheses should be replaced with
                      `classical` in the proof. " ++ s) <$>
      print_arguments deceq_binders

/-- A linter object for `decidable_classical`. -/
@[linter] meta def linter.decidable_classical : linter :=
{ test := decidable_classical,
  auto_decls := ff,
  no_errors_found := "No uses of `decidable` arguments should be replaced with `classical`",
  errors_found := "USES OF `decidable` SHOULD BE REPLACED WITH `classical` IN THE PROOF." }

/- The file `logic/basic.lean` emphasizes the differences between what holds under classical
and non-classical logic. It makes little sense to make all these lemmas classical, so we add them
to the list of lemmas which are not checked by the linter `decidable_classical`. -/
attribute [nolint decidable_classical] dec_em by_contradiction not_not of_not_not of_not_imp
not.imp_symm not_imp_comm or_iff_not_imp_left or_iff_not_imp_right not_imp_not not_or_of_imp
imp_iff_not_or imp_or_distrib imp_or_distrib' not_imp peirce not_iff_not not_iff_comm not_iff
iff_not_comm iff_iff_and_or_not_and_not not_and_not_right not_and_distrib not_and_distrib'
or_iff_not_and_not and_iff_not_or_not not_forall not_forall_not forall_or_distrib_left
forall_or_distrib_right not_ball

private meta def has_coe_to_fun_linter (d : declaration) : tactic (option string) :=
retrieve $ do
reset_instance_cache,
mk_meta_var d.type >>= set_goals ∘ pure,
args ← intros,
expr.sort _ ← target | pure none,
let ty : expr := (expr.const d.to_name d.univ_levels).mk_app args,
some coe_fn_inst ←
  try_core $ to_expr ``(_root_.has_coe_to_fun %%ty) >>= mk_instance | pure none,
some trans_inst@(expr.app (expr.app _ trans_inst_1) trans_inst_2) ←
  try_core $ to_expr ``(@_root_.coe_fn_trans %%ty _ _ _) | pure none,
tt ← succeeds $ unify trans_inst coe_fn_inst transparency.reducible | pure none,
set_bool_option `pp.all true,
trans_inst_1 ← pp trans_inst_1,
trans_inst_2 ← pp trans_inst_2,
pure $ format.to_string $
  "`has_coe_to_fun` instance is definitionally equal to a transitive instance composed of: " ++
  trans_inst_1.group.indent 2 ++
  format.line ++ "and" ++
  trans_inst_2.group.indent 2

/-- Linter that checks whether `has_coe_to_fun` instances comply with Note [function coercion]. -/
@[linter] meta def linter.has_coe_to_fun : linter :=
{ test := has_coe_to_fun_linter,
  auto_decls := tt,
  no_errors_found := "has_coe_to_fun is used correctly",
  errors_found := "INVALID/MISSING `has_coe_to_fun` instances.
You should add a `has_coe_to_fun` instance for the following types.
See Note function coercions]." }
