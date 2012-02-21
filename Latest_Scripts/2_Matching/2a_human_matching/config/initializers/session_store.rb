# Be sure to restart your server when you modify this file.

# Your secret key for verifying cookie session data integrity.
# If you change this key, all old sessions will become invalid!
# Make sure the secret is at least 30 characters and all random, 
# no regular words or you'll be exposed to dictionary attacks.
ActionController::Base.session = {
  :key         => '_forum_hotel_match_human_input_session',
  :secret      => 'cca4c078951eaf208c17b46b4ed0bcf7d30f1f61f2862bfae4813d380a17640b663ff8321ecf35aa353700a6f1d60db80b6cc3c0b243fcb3edd90f420983341b'
}

# Use the database for sessions instead of the cookie-based default,
# which shouldn't be used to store highly confidential information
# (create the session table with "rake db:sessions:create")
# ActionController::Base.session_store = :active_record_store
