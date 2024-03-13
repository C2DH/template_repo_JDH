# Journal of Digital History Author's Repository

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/C2DH/template_repo_JDH/main?filepath=author_guideline_template.ipynb)

This repository serves as a resource for authors submitting articles to the [Journal of Digital History](https://journalofdigitalhistory.org).
It contains a Jupyter notebook that provides an example and a simple structure that can be used to write articles for the journal.
The repository also includes a `preflight`github action that can be automatically triggered on commit, but by default, it is set to `workflow_dispatch`and actionable from the `actions` page on GitHub.
The preflight action generates a report within the repository that contains information about the adherence of the article to the submission guidelines.

## Contents

`article.ipynb` - This Jupyter notebook provides an example and a simple structure that authors can use to write articles for the Journal of Digital History. You can rename it according to your article name.

`.github/workflows/github-actions-preflight.yml` - This workflow file contains the preflight action that can be triggered automatically on commit or manually using the workflow_dispatch event to check that the article respects the Journal guidelines.

The preflight action generates or updates a report markdown file in the repository that provides information about the adherence of the article to the submission guidelines, usually named `report.md`

`requirements.txt` - stores information about all the libraries, modules, and packages in itself that are used while developing a particular project.

`runtime.txt` - specify the version of the runtime (e.g. the version of Python ). Have python-x.y in runtime.txt to run the repository with Python version x.y


## Getting Started

This repository it's a _template_, that is, it can be used as a starting point for new repositories.
On GitHub.com:

1. navigate to the main page of the repository.
2. Above the file list, click Use this template.
3. Select Create a new repository.
4. Type a name for your new repository, and an optional description.
5. Click Create repository from template.

Please follow the rest of the documentation on [GitHub](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template) to understand how to create a new repository from this template.

Use the example notebook as a template to write your article. You can modify the notebook to suit your needs and add your content.

## Preflight Action

To check if the article respects the Guidelines, we decided to create a `preflight` GitHub action that can be triggered automatically on commit - or manually using the `workflow_dispatch` event. The action is triggered by the `github-actions-preflight.yml` file in the `.github/workflows` folder.
By default, the preflight action is set to `workflow_dispatch`, which means you can manually trigger it by going to the "Actions" tab in the repository, selecting the "Preflight" workflow, and clicking the "Run workflow" button.
The preflight action will generate a report in the repository that provides information about the adherence of your article to the submission guidelines.

## MyBinder

The repository also contains a `requirements.txt` and a `runtime.txt` file that can be used to create a MyBinder environment. Check: https://mybinder.readthedocs.io/en/latest/using/config_files.html#preparing-a-repository-for-binder
The MyBinder environment can be used to run the example notebook to test that the code runs smoothly. 

## Contribution Guidelines

We welcome contributions to this repository that aim to improve the example notebook, the preflight action, or the overall workflow for authors submitting articles to the Journal of Digital History. Just contact us or open an issue.

## License

Copyright (C) 2023 university of Luxembourg.
This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but without any warranty; without even the implied warranty of merchantability or fitness for a particular purpose. See the GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

We hope this repository and the provided example notebook are helpful for authors submitting articles to the Journal of Digital History. If you have any questions, feedback, or suggestions, please feel free to open an issue or contact us. Thank you for your contribution!
