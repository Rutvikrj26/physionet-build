# PhysioNet Build

The new PhysioNet platform built using Django. The new site is currently hosted at [https://physionet.org/](https://physionet.org/)

Dev branch: [![Run Status](https://api.shippable.com/projects/59e7d1baaf0a170700d5b5b0/badge?branch=dev)](https://app.shippable.com/github/MIT-LCP/physionet-build) [![Coverage Badge](https://api.shippable.com/projects/59e7d1baaf0a170700d5b5b0/coverageBadge?branch=dev)](https://app.shippable.com/github/MIT-LCP/physionet-build)

## Running Local Instance Using Django Server

- Install sqlite3: `sudo apt-get install sqlite3`.
- Create python environment with python 3.6.
- Activate virtual python environment.
- Install python packages in `requirements.txt`.
- Copy `.env.example` file to `.env`.
- Within the `physionet-django` directory:
  - Run: `python manage.py resetdb` to reset the database.
  - Run: `python manage.py loaddemo` to load the demo fixtures set up example files.
  - Run: `python manage.py runserver` to run the server.

## Contribution Guidelines

- Familiarise yourself with the [PEP8 style guidelines](https://www.python.org/dev/peps/pep-0008/).
- Create a branch originating from the `dev` branch, titled after the new feature/change to be implemented.
- Write tests for your code where possible (see "Testing" section below). Confirm that all tests pass before making a pull request.
- If you create or alter any models or fields, you'll need to generate one or more accompanying migration scripts. Commit these scripts alongside your other changes.
- Make a pull request to the `dev` branch with a clear title and description of the changes. Tips for a good pull request: http://blog.ploeh.dk/2015/01/15/10-tips-for-better-pull-requests/

## Testing

- Unit tests for each app are kept in their `test*.py` files.
- To run the unit tests, change to the `physionet-django` directory and run `python manage.py test`.
- To check test coverage, change to the `physionet-django` directory and run `coverage run --source='.' manage.py test`. Next run `coverage html` to generate an html output of the coverage results. You may need to `pip install coverage` beforehand.
- To run the browser tests in the `test_browser.py` files, selenium and the [firefox driver](https://github.com/mozilla/geckodriver/releases) are required. If you want to see the test run in your browser, remove the `options.set_headless(True)` lines in the `setUpClass` of the browser testing modules.

## Database Content During Development

During development, the following workflow is applied for convenience:
- The database engine is sqlite3. The db.sqlite3 file will not be tracked by git, and hence will not be uploaded and shared between developers
- Demo model instances will be specified in json files in the `fixtures` subdirectory of each app. Example file: `<BASE_DIR>/<appname>/fixtures/demo-<appname>.json`

To conveniently obtain a clean database with the latest applied migrations, run:`python manage.py resetdb`. This does not populate the database with any data.

### Creating a branch with migrations

If you need to add, remove, or modify any models or fields, your branch will also need to include the necessary migration script(s).  In most cases, Django can generate these scripts for you automatically, but you should still review them to be sure that they are doing what you intend.

After making a change (such as adding a field or changing options), run `./manage.py makemigrations` to generate a corresponding migration script.  Then run `./manage.py migrate` to run that script on your local sqlite database.

If you make changes and later decide to undo them without committing, the easiest way is to simply run `rm */migrations/*.py && git checkout */migrations` to revert to your current HEAD.  Then run `./manage.py makemigrations` again if necessary, followed by `./manage.py resetdb && ./manage.py loaddemo`.

If other migrations are committed to dev in the meantime, you will need to resolve the resulting conflicts before your feature branch can be merged back into dev.  There are two ways to do this:

#### Merging migrations

If the two sets of changes are independent, they can be combined by merging `dev` into the feature branch and adding a "merge migration":
 * `git checkout my-new-feature && git pull && rm */migrations/*.py && git checkout */migrations`
 * `git merge --no-ff --no-commit origin/dev`
 * `./manage.py makemigrations --merge`
The latter command will ask you to confirm that the changes do not conflict (it will *not* detect conflicts automatically.)  Read the list of changes carefully before answering.  If successful, you can then run:
 * `./manage.py migrate && ./manage.py test`
 * `git add */migrations/ && git commit`
As with any pull request, have someone else review your changes before merging the result back into `dev`.

#### Rebasing migrations

If the migration behavior interacts with other changes that have been applied to dev in the meantime, the migration scripts will need to be rewritten.
 * Either rebase the feature branch onto origin/dev, or merge origin/dev into the feature branch.
 * Roll back migrations by running `rm */migrations/*.py; git checkout origin/dev */migrations`
 * Generate new migrations by running `./manage.py makemigrations`
 * `./manage.py migrate && ./manage.py test`
 * `git add */migrations/ && git commit`
