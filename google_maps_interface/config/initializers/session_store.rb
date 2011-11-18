# Be sure to restart your server when you modify this file.

# Your secret key for verifying cookie session data integrity.
# If you change this key, all old sessions will become invalid!
# Make sure the secret is at least 30 characters and all random, 
# no regular words or you'll be exposed to dictionary attacks.
ActionController::Base.session = {
  :key         => '_myproject_session',
  :secret      => '283f83241bcf5b180fefd199ec43050395d015e4d807c8ebfd78b5ee75f0448bbeea8ea17cfbcf190937d80f4734cde1e5138b581178bb8a107b8f7e3a9f4c85'
}

# Use the database for sessions instead of the cookie-based default,
# which shouldn't be used to store highly confidential information
# (create the session table with "rake db:sessions:create")
# ActionController::Base.session_store = :active_record_store
