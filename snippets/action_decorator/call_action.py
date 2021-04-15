# async def _server_call_action(self, action_btn: ActionButton):
#         action = action_btn.action
#         user_input = []
#         while True:
#             try:
#                 if user_input == []:
#                     code = action_btn.action.run(self.current_goal, self.current_context_selection_as_pspos)
#                 else:
#                     code = action_btn.action.run(self.current_goal, self.current_context_selection, user_input)
#             except MissingParametersError as miss:
#                 if miss.input_type == InputType.Text:
#                     text, ok = QInputDialog.getText(action_btn, 'Input element','Input element:')
#                 elif miss.input_type == InputType.Choice:
#                     #text, ok = PopUp(action_btn, miss.list_of_choices).showDialog()
#                 if ok:
#                     user_input.append(text)
#                 else:
#                     break
#             except WrongUserInput:
#                 self.clear_user_selection()
#                 break
#             else:
#                 print(code)
#                 await self.servint.code_insert(action.caption, code)
#                 self.clear_user_selection()
#                 break
