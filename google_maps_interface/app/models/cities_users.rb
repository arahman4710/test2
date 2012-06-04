class CitiesUsers < ActiveRecord::Base
  belongs_to :City
  belongs_to :User
end
