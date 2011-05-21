class City < ActiveRecord::Base
has_many :hotels
 has_many :cityusers
 has_many :users, :through => :cityusers
 has_many :regions
 #has_and_belongs_to_many :Users
end
