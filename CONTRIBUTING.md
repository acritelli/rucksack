# Contributing

As this project is in very early stages, the best way to contribute right now is to file a GitHub issue if you find a bug or want to request a feature.

In general, this project will aim to follow the [OneFlow](https://www.endoflineblog.com/oneflow-a-git-branching-model-and-workflow) branching strategy. Essentially:

* All work will be done in short-lived feature branches
* Feature branches will be merged into the `develop` branch
* A release will be cut by creating a release branch off develop, tagging it, and merging it into `develop`
* The `main` branch is a "pointer" branch to the latest release tag

Rucksack follows [Semantic Versioning](https://semver.org/).
