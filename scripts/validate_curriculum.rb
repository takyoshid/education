#!/usr/bin/env ruby
# frozen_string_literal: true

require "pathname"
require "open3"

ROOT = Pathname.new(__dir__).join("..").expand_path
errors = []

markdown_files = ROOT.glob("**/*.md").reject { |path| path.to_s.include?("/.git/") }

markdown_files.each do |file|
  content = file.read(encoding: "UTF-8")

  if content.strip.empty?
    errors << "empty Markdown file: #{file.relative_path_from(ROOT)}"
  end

  # Links in fenced code blocks are examples learners are expected to replace.
  prose = content.gsub(/^```.*?^```\s*$/m, "")
  prose.scan(/\[[^\]]*\]\(([^)]+)\)/).flatten.each do |raw_target|
    target = raw_target.strip.delete_prefix("<").delete_suffix(">")
    next if target.empty?
    next if target.match?(%r{\A(?:https?://|mailto:|#)})

    path_part = target.split("#", 2).first
    next if path_part.include?("{") || path_part.include?("<")

    # Prose placeholders such as [title](link) are examples, not repository links.
    looks_like_path = path_part.start_with?(".") || path_part.include?("/") ||
                      path_part.match?(/\.(?:md|py|js|ts|tsx|html|css|png|jpg|jpeg|gif|svg|sql|sh|ya?ml|json)\z/i)
    next unless looks_like_path

    resolved = file.dirname.join(path_part).cleanpath
    unless resolved.exist?
      errors << "broken link: #{file.relative_path_from(ROOT)} -> #{target}"
    end
  end
end

phase_dirs = ROOT.children.select { |path| path.directory? && path.basename.to_s.match?(/\Aphase\d+-/) }
phase_dirs.sort.each do |phase|
  readme = phase.join("README.md")
  errors << "missing phase README: #{phase.basename}" unless readme.file?

  lessons = phase.join("lessons")
  errors << "missing lessons directory: #{phase.basename}" unless lessons.directory?
  if lessons.directory? && lessons.glob("*.md").empty?
    errors << "phase has no lessons: #{phase.basename}"
  end
end

assessed_phases = %w[
  phase2-programming
  phase3-algorithms
  phase5-web-frontend
  phase6-backend-db
  phase7-software-design
  phase8-infra-cloud
  phase11-ai-era
  phase12-concurrency-reliability
  phase13-distributed-systems
]
assessed_phases.each do |name|
  assessment = ROOT.join(name, "assessment", "README.md")
  errors << "missing practical assessment: #{name}" unless assessment.file?
end

longitudinal_starter = ROOT.join("longitudinal-project", "starter", "phase2")
errors << "missing longitudinal project starter" unless longitudinal_starter.directory?

tracked_files, git_error, git_status = Open3.capture3("git", "-C", ROOT.to_s, "ls-files")
errors << "git ls-files failed: #{git_error.strip}" unless git_status.success?
tracked_junk = tracked_files.lines.map(&:strip).grep(/(?:^|\/)\.DS_Store\z/)
tracked_junk.each { |path| errors << "tracked OS metadata: #{path}" }

if errors.empty?
  puts "Curriculum validation passed (#{markdown_files.length} Markdown files, #{phase_dirs.length} phases)."
  exit 0
end

warn "Curriculum validation failed with #{errors.length} error(s):"
errors.each { |error| warn "- #{error}" }
exit 1
