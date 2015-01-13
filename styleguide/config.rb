###################
# Page options, layouts, aliases and proxies
###################

# With alternative layout
page '/**', :layout => 'glyptotheque'
# With no layout
page "*.component", :layout => false
page "/glyptotheque/*", :layout => false, directory_index: false
page '*.css', :layout => false
page '*.js', :layout => false
page '*.json', :layout => false

# Meta redirects
# redirect 'index.html', to: 'prototypes/sample'

# A path which all have the same layout
# with_layout :admin do
#   page "/admin/*"
# end

ready do
  # Create mappings for isolated component pages (iframe embeddable)
  resources_for('/', exclude_indexes: true, allow_hidden: true).each do |r|
    proxy "#{r.path.sub(r.ext, '')}-isolated.html", r.path, layout: 'isolated'
  end
  resources_for('/', allow_hidden: true).each do |r|
    proxy "#{r.path.sub(r.ext, '')}/isolated", r.path, layout: 'isolated'
  end
end

###################
# Helpers
###################

# helpers do
# end

set :css_dir, 'assets/styles'
set :js_dir, 'assets/js'
set :images_dir, 'assets/img'

set :relative_links, true

bowerrc_dir = JSON.parse(IO.read("#{root}/.bowerrc"))['directory']

# Compass configuration
compass_config do |config|
  import_paths = %w(normalize.css)

  import_paths.each do |path|
    full_path = File.join(root, bowerrc_dir, path)
    config.add_import_path(full_path)
    config.add_import_path(Sass::CssImporter::Importer.new(full_path))
  end

  # Add project specific style dependencies
  cla_styles = File.expand_path('../', root)
  govuk_styles = File.expand_path('../node_modules/govuk_frontend_toolkit', root)
  config.add_import_path(cla_styles, govuk_styles)

  config.sass_options = {
    quiet: true
  }
  # For Style Guide CSS sources
  # config.output_style = :expanded
end

# Sprockets
ready do
  sprockets.append_path(File.join(root, bowerrc_dir))
end

activate :model
activate :data_loaders
activate :resource_helpers
activate :outliner
activate :syntax, css_class: 'codehilite'

Slim::Engine.disable_option_validator!
Slim::Engine.set_default_options :pretty => true
Slim::Engine.set_default_options :attr_list_delims => { '(' => ')', '[' => ']' }

# Development-secific configuration
configure :development do
  activate :livereload, animate: true
end

# Build-specific configuration
configure :build do
  compass_config do |config|
    config.sass_options = { :line_comments => false }
  end

  # For example, change the Compass output style for deployment
  # activate :minify_css

  # Minify Javascript on build
  # activate :minify_javascript

  # Enable cache buster
  # activate :asset_hash

  # Use relative URLs
  activate :relative_assets

  # Or use a different image path
  # set :http_prefix, "/Content/images/"
end

###################
# Additional tasks
###################

# Simple launcher for local evaluation build
# Double click `build/launch.command` (Mac)
after_build do |builder|
  file = "#{build_dir}/launch.command"
  open(file, 'w') do |f|
    f << "#!/bin/bash\n"
    f << 'cd `dirname $0` && open "http://localhost:8000" && python -m SimpleHTTPServer'
  end
  File.chmod(0555, file)
end

# Middleman Deploy
activate :deploy do |deploy|
  deploy.method = :git
  # Optional Settings
  # deploy.remote   = 'custom-remote' # remote name or git url, default: origin
  # deploy.branch   = 'custom-branch' # default: gh-pages
  # deploy.strategy = :submodule      # commit strategy: can be :force_push or :submodule, default: :force_push
  # deploy.commit_message = 'custom-message'      # commit message (can be empty), default: Automated commit at `timestamp` by middleman-deploy `version`
end
