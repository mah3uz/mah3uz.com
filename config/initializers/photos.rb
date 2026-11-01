# Photos imported from Unsplash (site/schema/tasks/unsplash-photos.yml) take their title, and so their address, from
# the photo's alt text. Unsplash leaves that empty on some photos, so a photo without one gets an address from its
# Unsplash id instead of being skipped. The id is mixed-case and Nibble slugs are lower-case, hence the prefix and
# parameterize.
ActiveSupport.on_load(:nibble_entry) do
  before_validation if: -> { collection == "photos" && slug.blank? } do
    id = data.to_h["unsplash_id"].to_s.parameterize
    next if id.empty?

    self.slug = "photo-#{id}"
    self.uri = Nibble::Uris.for(self)
  end
end
