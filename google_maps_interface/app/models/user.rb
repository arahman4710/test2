class User < ActiveRecord::Base
 has_many :cityusers
 has_many :cities, :through => :cityusers
#has_and_belongs_to_many :Cities
accepts_nested_attributes_for :cityusers,
                                :allow_destroy => true,
                                :reject_if => proc { |attrs| attrs['city_id'].blank? }

  acts_as_authentic do |c|
    c.validates_length_of_password_field_options = {:on => :update, :minimum => 4, :if => :has_no_credentials?}
    c.validates_length_of_password_confirmation_field_options = {:on => :update, :minimum => 4, :if => :has_no_credentials?}
  end
 def has_no_credentials?
    self.crypted_password.blank?
  end
def deliver_password_reset_instructions!
reset_perishable_token!
Notifier.deliver_password_reset_instructions(self)
end
def active?
    active
  end
def activate!
    self.active = true
    save
  end
 def signup!(params)
    self.username = params[:user][:username]
    self.email = params[:user][:email]
    save_without_session_maintenance
  end
def activate!(params)
    self.active = true
    self.password = params[:user][:password]
    self.password_confirmation = params[:user][:password_confirmation]

    save
  end
def deliver_activation_instructions!
    reset_perishable_token!
    Notifier.deliver_activation_instructions(self)
  end
 
  def deliver_activation_confirmation!
    reset_perishable_token!
    Notifier.deliver_activation_confirmation(self)
  end
end
