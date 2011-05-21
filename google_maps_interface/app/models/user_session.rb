class UserSession < Authlogic::Session::Base
def deliver_password_reset_instructions!
reset_perishable_token!
Notifier.deliver_password_reset_instructions(self.username)
end
end