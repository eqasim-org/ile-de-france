# Versioning

TODO: This is work in progress. It will only make proper sense if we have
a way to explicitly pass on the version number when a new population / MATSim
simulation is created!

Development of the pipeline happens in the `develop` branch. Changes are
introduced via PRs (pull requests). Every pull request (except it is a very
minor change) should update the `CHANGELOG.md`.

The `develop` branch always contains a `*-dev` version, which is currently
"under develpment". If there is `A-dev`, there was already a fixed release
version `A` in the `master` branch. This means, if there was a release `A`,
all "under development" work **after** happens in `A-dev`. Only when a new
release is made, we decide on the final new release number. This may depend
on what changes have been performed in the meantime, i.e. if they were major
or minor.

Whenever a new version should be released, the process is
as follows:

- Bump up the version number (see below for all the files where this needs to
  happen):
  - If there are changes that have a backwards compatibility break, update the
    minor version (e.g. `1.2.3-dev` -> `1.3.0-dev`).
  - If there are changes that do not introduce a change in API or backwards
    compatibility, update the patch version (e.g. `1.2.3-dev` -> `1.2.4-dev`).
  - If there are exceptional major changes in the pipeline, update the major
    version (e.g. `1.2.3-dev` -> `2.0.0-dev`).
- Make a new PR with the title "Version X.X.X" and merge it (after passing all
  necessary tests) back into `develop`.
- Now start a new branch from the `master` branch and merge in the `develop` branch.


- Update `config.py` by removing the `-dev` from the version number. This happens
  usually while resolving merge conflicts (as these version numbers are naturally
  out of synch between `master` and `develop`).
- Send a PR with the title "Release X.X.X" to the `master` branch.
- Tag the HEAD commit in the `master` branch as `vX.X.X`
- In the HEAD of the master branch, perform the `pip` build:
  - `python3 config.py sdist bdist_wheel` to create the packages
  - `python3 -m twine upload dist/*` to upload the packages
  - To do the last step, you need to have set up your account on PIP and you
    need to have received the rights to push to the `synpp` package.

When updating the version number, this should happen in the following files:
- `config.py`
- `README.md`
