# Changelog

All notable changes to this project will be documented in this file.

<!--attr-start-->

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--attr-end-->

<!--
Using the following categories, list your changes in this order:
    - "Added" for new features.
    - "Changed" for changes in existing functionality.
    - "Deprecated" for soon-to-be removed features.
    - "Removed" for now removed features.
    - "Fixed" for any bug fixes.
    - "Security" in case of vulnerabilities.
 -->

<!--changelog-start-->

## [Unreleased]

### Added

-   `auth_required` decorator to prevent your components from rendered to unauthenticated users.
-   `use_query` hook for fetching database values.
-   `use_mutation` hook for modifying database values.

## [1.1.0] - 2022-07-01

### Added

-   `django_css` and `django_js` components to defer loading CSS & JS files until needed.

### Changed

-   Bumped the minimum IDOM version to 0.39.0

## [1.0.0] - 2022-05-22

### Added

-   Django-specific hooks! `use_websocket`, `use_scope`, and `use_location` are now available within the `django_idom.hooks` module.
-   Documentation has been placed into a formal docs webpage.
-   Logging for when a component fails to import, or if no components were found within Django.

### Changed

-   `idom_component` template tag has been renamed to `component`
-   Bumped the minimum IDOM version to 0.38.0

### Removed

-   `websocket` parameter for components has been removed. Functionally, it is replaced with `django_idom.hooks.use_websocket`.

## [0.0.5] - 2022-04-04

### Changed

-   Bumped the minimum IDOM version to 0.37.2

### Fixed

-   ModuleNotFoundError: No module named `idom.core.proto` caused by IDOM 0.37.2

## [0.0.4] - 2022-03-05

### Changed

-   Bumped the minimum IDOM version to 0.37.1

## [0.0.3] - 2022-02-19

### Changed

-   Bumped the minimum IDOM version to 0.36.3

## [0.0.2] - 2022-01-30

### Added

-   Ability to declare the HTML class of the top-level component `div`
-   `name = ...` parameter to IDOM HTTP paths for use with `django.urls.reverse()`
-   Cache versioning to automatically invalidate old web module files from the cache backend
-   Automatic pre-population of the IDOM component registry
-   Type hinting for `IdomWebsocket`

### Changed

-   Fetching web modules from disk and/or cache is now fully async
-   Static files are now contained within a `django_idom/` parent folder
-   Upgraded IDOM to version `0.36.0`
-   Minimum Django version required is now `4.0`
-   Minimum Python version required is now `3.8`

### Removed

-   `IDOM_WEB_MODULES_PATH` has been replaced with Django `include(...)`
-   `IDOM_WS_MAX_RECONNECT_DELAY` has been renamed to `IDOM_WS_MAX_RECONNECT_TIMEOUT`
-   `idom_web_modules` cache backend has been renamed to `idom`

### Fixed

-   Increase test timeout values to prevent false positives
-   Windows compatibility for building Django-IDOM

### Security

-   Fixed potential directory travesal attack on the IDOM web modules URL

## [0.0.1] - 2021-08-18

### Added

-   Support for IDOM within the Django

[unreleased]: https://github.com/idom-team/django-idom/compare/1.0.0...HEAD
[1.1.0]: https://github.com/idom-team/django-idom/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/idom-team/django-idom/compare/0.0.5...1.0.0
[0.0.5]: https://github.com/idom-team/django-idom/compare/0.0.4...0.0.5
[0.0.4]: https://github.com/idom-team/django-idom/compare/0.0.3...0.0.4
[0.0.3]: https://github.com/idom-team/django-idom/compare/0.0.2...0.0.3
[0.0.2]: https://github.com/idom-team/django-idom/compare/0.0.1...0.0.2
[0.0.1]: https://github.com/idom-team/django-idom/releases/tag/0.0.1
