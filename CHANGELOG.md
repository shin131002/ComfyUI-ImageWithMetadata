# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-25

### Added
- Initial release
- **LoadImageWithMetadata** node
  - Batch image loading from folder
  - Metadata extraction from PNG/text files
  - Two modes: single_image and incremental_image
  - Support for A1111 format metadata
  - Automatic loop when reaching end of folder
- **SaveImageWithMetadata** node
  - Save images with comprehensive metadata
  - PNG metadata and/or text file output
  - JSON and plain text format support
  - Date-based filename support
- **CheckpointLoaderWithNames** node
  - Returns model and VAE names as strings
  - Baked VAE support
- Based on WAS Node Suite's BatchImageLoader pattern
- English and Japanese README
- Comprehensive documentation (USAGE.md)

### Technical Details
- Uses WAS Node Suite's proven image loading method for stability
- PIL to tensor conversion optimized for speed
- No VRAM issues or memory leaks
- File-based counter persistence for batch processing

[1.0.0]: https://github.com/YOUR_USERNAME/ComfyUI-ImageWithMetadata/releases/tag/v1.0.0
