class Region < ActiveRecord::Base
  has_many :points
  belongs_to :city
end
