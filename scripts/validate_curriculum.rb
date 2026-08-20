#!/usr/bin/env ruby
# frozen_string_literal: true

require "pathname"
require "open3"

ROOT = Pathname.new(__dir__).join("..").expand_path
errors = []

# 検査対象は教材そのものだけ。node_modules や仮想環境の中には、
# 教材が責任を持たない大量の Markdown があり、そこの壊れたリンクを
# 報告しても直しようがない。学習者が npm install した直後に
# 検査が落ちる、という無意味な失敗を避ける。
IGNORED_DIRECTORIES = %w[.git node_modules .venv venv dist build __pycache__].freeze

markdown_files = ROOT.glob("**/*.md").reject do |path|
  path.relative_path_from(ROOT).each_filename.any? { |part| IGNORED_DIRECTORIES.include?(part) }
end

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

# README trees and tables often show file names as plain text rather than links.
# Check README references separately so renames cannot leave a curriculum index
# pointing learners at files that no longer exist. Paths are resolved from the
# phase root; bare names may exist anywhere below the phase that mentions them.
curriculum_reference = %r{
  (?<![A-Za-z0-9_.-])
  (?:[A-Za-z0-9_.-]+/)*
  (?:\d{2}-[A-Za-z0-9_.-]+\.md|ex\d{2}[-_][A-Za-z0-9_.-]*)
}x

phase_dirs.each do |phase|
  phase.glob("**/README.md").each do |file|
    content = file.read(encoding: "UTF-8")
    content.scan(curriculum_reference).each do |reference|
      basename = Pathname.new(reference).basename.to_s
      exists = if reference.include?("/")
                 phase.join(reference).cleanpath.exist?
               else
                 !phase.glob("**/#{basename}").empty?
               end
      next if exists

      errors << "missing curriculum file: #{file.relative_path_from(ROOT)} -> #{reference}"
    end
  end
end

phase_dirs.sort.each do |phase|
  readme = phase.join("README.md")
  errors << "missing phase README: #{phase.basename}" unless readme.file?

  lessons = phase.join("lessons")
  errors << "missing lessons directory: #{phase.basename}" unless lessons.directory?
  if lessons.directory? && lessons.glob("*.md").empty?
    errors << "phase has no lessons: #{phase.basename}"
  end
end

phase_dirs.each do |phase|
  assessment = phase.join("assessment", "README.md")
  errors << "missing practical assessment: #{phase.basename}" unless assessment.file?

  retrieval_check = phase.join("assessment", "retrieval-check.md")
  errors << "missing retrieval check: #{phase.basename}" unless retrieval_check.file?
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

errors.uniq!
warn "Curriculum validation failed with #{errors.length} error(s):"
errors.each { |error| warn "- #{error}" }
exit 1
