namespace :site do
  namespace :assets do
    # The content import only uploads a file the library lacks, so a redrawn image never reaches a site that already
    # has it. These compare each package file with the library's copy; refresh replaces the ones that differ the way
    # Replace does in the Control Plane, so the asset keeps its path and id and every reference to it stays.
    stale = lambda do |package|
      root = Rails.root.join(package || "site/packages/default", "assets")
      abort "#{root} does not exist" unless root.directory?
      references = Nibble::Packages::References.new([])

      Dir.glob(root.join("**/*")).sort.filter_map do |file|
        next unless File.file?(file)

        path = Pathname(file).relative_path_from(root).to_s
        asset = references.existing("asset", nil, path)
        next puts("  #{path}: not in the library; the content import uploads it") unless asset

        local = File.binread(file)
        # Uploaded SVGs are stored sanitized, so compare like with like or every SVG would look changed.
        local = Nibble::Assets::SvgSanitizer.call(local) if Nibble::Assets.kind_for(path) == "svg"
        [ path, file, asset ] unless asset.blob.download == local
      end
    end

    desc "List library assets whose file differs from the content package's"
    task :changed, [ :package ] => :environment do |_, args|
      changed = stale.(args[:package])
      changed.each { |path, _, _| puts "~ #{path}" }
      puts "#{changed.size} would be replaced by site:assets:refresh"
    end

    desc "Replace library assets whose file differs from the content package's"
    task :refresh, [ :package ] => :environment do |_, args|
      failed = 0
      changed = stale.(args[:package])
      changed.each do |path, file, asset|
        puts "~ #{path}"
        blob = ActiveStorage::Blob.create_and_upload!(io: File.open(file, "rb"), filename: File.basename(path), content_type: Marcel::MimeType.for(Pathname(file)))
        result = Nibble::Assets::Upload.replace(asset, blob, actor: Nibble::Principal.system)
        next if result.ok?

        failed += 1
        puts "  failed: #{result.errors.values.flatten.to_sentence}"
      end
      puts "replaced #{changed.size - failed}, #{failed} failed"
      exit 1 if failed.positive?
    end
  end
end
