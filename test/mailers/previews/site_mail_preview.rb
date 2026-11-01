# The site's emails in its own layout (app/views/layouts/nibble/mailer.*), at /rails/mailers in development.
class SiteMailPreview < ActionMailer::Preview
  SAMPLE = { "name" => "Alex Example", "email" => "alex@example.com", "topic" => "project",
             "message" => "We're moving a Rails app off Heroku onto our own servers and would like help planning it." }.freeze

  # What someone who writes through the contact form receives.
  def contact_confirmation
    form = Nibble::Forms.find("contact")
    plan = Nibble::Forms::Notify.new(form, SAMPLE, nil).plan(0)
    Nibble::FormsMailer.submission("contact", 0, SAMPLE, plan)
  end

  # These two need a user to address; create one with bin/rails nibble:setup first.
  def invitation = Nibble::PasswordsMailer.invite(user)
  def password_reset = Nibble::PasswordsMailer.reset(user)

  private

  def user = Nibble::User.first || raise("No user yet: create one, then reload this preview.")
end
