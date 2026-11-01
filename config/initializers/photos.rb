# The Photography page: photos from unsplash.com/@mah3uz, imported by two scheduled tasks.
#
# - site/schema/tasks/unsplash-photos.yml imports the photos and their statistics into the `photos` collection.
# - site/schema/tasks/unsplash-photo-details.yml runs the handler below, which fills the `photo_details` global with
#   each photo's camera, exposure, place and tags.

# A photo takes its title, and so its address, from Unsplash's alt text, which Unsplash writes itself for nearly every
# photo. One without it gets an address from its Unsplash id instead of being skipped. The id is mixed-case and Nibble
# slugs are lower-case, hence the prefix and parameterize.
ActiveSupport.on_load(:nibble_entry) do
  before_validation if: -> { collection == "photos" && slug.blank? } do
    id = data.to_h["unsplash_id"].to_s.parameterize
    next if id.empty?

    self.slug = "photo-#{id}"
    self.uri = Nibble::Uris.for(self)
  end
end

# Unsplash's list of a user's photos has no EXIF, place or tags; GET /photos/:id has them, one photo a call. So each
# run reads a batch: photos not read yet first, then any read more than a week ago. A run makes at most BATCH + 1
# calls, every two hours, well inside the 50 an hour an Unsplash app is allowed before it is approved for production.
module UnsplashPhotoDetails
  USER = "mah3uz".freeze
  BATCH = 15
  STALE = 7.days

  module_function

  def call(task)
    unsplash = task.connection(:unsplash)
    ids = fetch(unsplash, "/users/#{USER}/photos?per_page=30&order_by=views").map { |photo| photo["id"] }
    rows = stored.index_by { |row| row["unsplash_id"] }.slice(*ids)
    due = ids.select { |id| stale?(rows[id]) }.sort_by { |id| rows.dig(id, "fetched").to_s }.first(BATCH)
    due.each { |id| rows[id] = row(fetch(unsplash, "/photos/#{id}")) }

    task.update_global(:photo_details, { "photos" => ids.filter_map { |id| rows[id] } })
    { "photos" => ids.size, "read" => due.size, "waiting" => ids.count { |id| stale?(rows[id]) } }
  end

  def fetch(unsplash, path)
    response = unsplash.get(path)
    raise Nibble::Error, "Unsplash answered #{response.status} for #{path}" unless response.ok?

    response.json
  end

  def stored
    record = Nibble::Records::GlobalSet.find_by(handle: "photo_details", locale: Nibble.config.default_locale.code)
    Array(record&.values&.fetch("photos", nil))
  end

  def stale?(row)
    fetched = row && Time.zone.parse(row["fetched"].to_s)
    fetched.nil? || fetched < STALE.ago
  rescue ArgumentError
    true
  end

  def row(photo)
    exif = photo["exif"].to_h
    location = photo["location"].to_h
    latitude, longitude = location["position"].to_h.values_at("latitude", "longitude")
    placed = latitude.to_f.nonzero? || longitude.to_f.nonzero?

    {
      "unsplash_id" => photo["id"],
      "camera" => camera(exif["make"], exif["model"]),
      "aperture" => exif["aperture"].presence&.to_s,
      "exposure" => exif["exposure_time"].presence&.to_s,
      "focal_length" => exif["focal_length"].presence&.to_s,
      "iso" => exif["iso"].presence&.to_s,
      "location" => location["name"].presence || [ location["city"], location["country"] ].compact_blank.join(", ").presence,
      "latitude" => (latitude.to_s if placed),
      "longitude" => (longitude.to_s if placed),
      "tags" => Array(photo["tags"]).filter_map { |tag| tag["title"].presence }.uniq.first(8).join(", ").presence,
      "fetched" => Time.current.utc.iso8601
    }
  end

  # "NIKON CORPORATION" + "NIKON D750" reads "Nikon D750"; "Canon" + "Canon EOS R6" reads "Canon EOS R6".
  def camera(make, model)
    make = make.to_s.strip.sub(/[\s,]+(corporation|corp\.?|co\.?,? ?ltd\.?|inc\.?|imaging)\z/i, "")
    make = make.capitalize if make.match?(/\A[A-Z]{3,}\z/)
    model = model.to_s.strip
    return make.presence if model.empty?

    model = model.sub(/\A#{Regexp.escape(make)}\s*/i, "") if make.present?
    [ make, model ].compact_blank.join(" ")
  end
end

# Nibble is loaded after the initializers run, so the handler is registered once the application is ready.
Rails.application.config.to_prepare do
  Nibble::Tasks.register_handler("unsplash_photo_details", UnsplashPhotoDetails.method(:call))
end
