class Cityuser < ActiveRecord::Base
  belongs_to :city
  belongs_to :User
end
