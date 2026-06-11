# Group A Manifest Notes

Preferred current manifest files:

- `manifest-current.csv`
- `manifest-current.json`

These files list the current local collection state for Alabama, Alaska, Arizona, Arkansas, California, Colorado, Connecticut, Delaware, Florida, and Georgia. They include source URL, source role, HTTP/status result where available, error reason where blocked or uncollected, local raw file path, extracted text file path, and extracted text byte size.

The earlier completed-run manifest files, `manifest.csv` and `manifest.json`, are retained as run provenance. Use `manifest-current.*` for review because it also reflects local files produced before the later interrupted retry was stopped.

Summary and analysis are in `summary.md`.
