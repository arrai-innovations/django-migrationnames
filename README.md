# Project Testcase

## Overview

This project exists to provide a way to demonstrate an issue that can occur when squashing migrations in a project, and has in this project.

The issue occurs in django 4.2.24 (the original version) and django 5.2.7 (the version this is updated to use).

This project has its migrations set up in a way that if you call `showmigrations`, you could either have the command succeed, or you could get a CircularDependencyError.  Which occurs, depends on the way python iterates over the data of a set, which varies with each run.

Project code, app names, model names, and migrations have been changed to obscure what the project is and minimize things needed to test the issue.  These changes didn't affect the circular dependency issues that occur.

There are 8 distinct situations that can occur.  2 of them succeed and 6 cause a CircularDependencyError.


The first step to help prevent circular dependency errors, was to comment out the dependencies to other apps in the older migrations.  This helps, but doesn't fix the issue.  The issue is related to this set containing migration names.  If this set is turned into a list, then the success rate jumps to 100%.

    https://github.com/django/django/blob/2d2e1a6a9dbfe0cba58a4d2486c51fccdb501d55/django/db/migrations/loader.py#L111-L115


## Recent Changes / Discoveries

* 2 old migrations had dependencies that I had missed commenting out, which appears to be how this issue occurs.

* Commented out 1 of the old migration dependencies.  This modified the distinct situations that can occur.  There are now 2 that succeed and 2 that cause a CircularDependencyError.

* All apps have been modified to have a max of 6 migrations.

* Modified the dependency in the old migration to point to the last migration for that app.

* Removed apps 3, 5, 7, 8, and 10.  Also contrib, which wasn't used.


## Usage

The management command is called `show_issue`.  It imports and modifies the MigrationLoader to provide a way to capture and analyze the results of each attempt.

By default, when you run the command, 100 attempts will be made.  The output will show which attempts succeed and which fail.

```shell
python manage.py show_issue
```

Output:

```
Using shuffled set of migration names.
Attempt 1 Failed
Attempt 2 Failed
Attempt 3 Failed
Attempt 4 Succeeded
...
Attempt 97 Failed
Attempt 98 Succeeded
Attempt 99 Failed
Attempt 100 Succeeded

Results:
    41 Succeeded
    59 Failed
    
Succeeding Attempts:
    {4, 7, 8, 10, 15, 18, 23, 27, 29, 32, 34, 35, 41, 42, 47, 48, 49, 50, 51, 53, 55, 59, 60, 66, 67, 68, 75, 76, 77, 78, 79, 81, 82, 86, 87, 88, 90, 93, 95, 98, 100}

CircularDependencyError Attempts:
    {1, 2, 3, 5, 6, 9, 11, 12, 13, 14, 16, 17, 19, 20, 21, 22, 24, 25, 26, 28, 30, 31, 33, 36, 37, 38, 39, 40, 43, 44, 45, 46, 52, 54, 56, 57, 58, 61, 62, 63, 64, 65, 69, 70, 71, 72, 73, 74, 80, 83, 84, 85, 89, 91, 92, 94, 96, 97, 99}
```

When creating this management command, it was discovered that iterating over the set would always occur in the same order, so to mimic the randomness that occurs when using `showmigrations`, the migration names are shuffled with each loop iteration.  You can always call `showmigrations` a number of times to verify that sometimes it fails and sometimes it passes.

By default, the management command uses the code that makes a set of migration names.  To use the migration names as a list, add `-f` or `--use-fixed` to the management command.

```shell
python manage.py show_issue --use-fixed
```

You can alter the number of attempts by adding `-a ATTEMPTS` or `--attempts ATTEMPTS`.

```shell
python manage.py show_issue --attempts 1000
```

## Logged Results

A number of files are created to log the results when the command is run.  Each are prefixed with `original` or `fixed`, depending on the use of (`-f` or `--use-fixed`) or not.  The results data is derived from `loader.graph.node_map`.  The log files will be truncated for the appropriate `original` or `fixed` versions with each run of the command.

The logged files are:

* `original_successes.txt` or `fixed_successes.txt` and `original_failures.txt` or `fixed_failures.txt` - Contains the Migration and Children information for each attempt.  Which file is used depends on if the attempt succeeds or causes a CircularDependencyError.

    Output:
    ```
    Attempt #3
        Migrations:
            app_eight.0001_squashed_initial
                No Children
            app_eighteen.0001_squashed_initial
                Children:
                    app_one.0001_squashed_initial
                    app_seventeen.0001_squashed_initial
                    app_thirteen.0002_squashed_initial
                    app_twelve.0001_squashed_initial
            ...
            users.0002_squashed_initial
                No Children
    ```

* `original_differences_between_successes.txt` or `fixed_differences_between_successes.txt` - compares the results of the first success to any subsequent successes.

    Output:
    ```
    Comparing Attempt #5 and #7
        No Differences
    
    Comparing Attempt #5 and #9
        Migrations:
            users.0001_squashed_initial
                Missing:
                    app_thirteen.0002_squashed_initial
    
            users.0002_squashed_initial
                Extra:
                    app_two.0001_squashed_initial
                    app_seventeen.0001_squashed_initial
                    app_thirteen.0001_squashed_initial
                    app_four.0001_squashed_initial
                    app_thirteen.0002_squashed_initial
                    app_one.0001_squashed_initial
                    app_six.0001_squashed_initial
                    app_eighteen.0001_squashed_initial
                    app_eleven.0001_squashed_initial
                    app_fifteen.0001_squashed_initial
                    app_nine.0001_squashed_initial
                    app_twelve.0001_squashed_initial
    ```

* `original_differences_between_failures.txt` or `fixed_differences_between_failures.txt` - compares the results of the first failure to any subsequent failure.  This has the same output as above.

* `original_differences_between_successes_and_failures.txt` or `fixed_differences_between_successes_and_failures.txt` - compares the results of the first success to any failures.  This has the same output as above.

* `original_unique_migrations_and_children_filename.txt` or `fixed_unique_migrations_and_children_filename.txt` - contains all the unique structures of the migrations and their children.

    Output:
    ```
    Unique Migrations and Children #1 - circular
        Migrations:
            app_eight.0001_squashed_initial
                No Children
            app_eighteen.0001_squashed_initial
                Children:
                    app_one.0001_squashed_initial
                    app_seventeen.0001_squashed_initial
                    app_thirteen.0002_squashed_initial
                    app_twelve.0001_squashed_initial
            ...
            users.0002_squashed_initial
                Children:
                    app_eighteen.0001_squashed_initial
                    app_eleven.0001_squashed_initial
                    app_fifteen.0001_squashed_initial
                    app_four.0001_squashed_initial
                    app_nine.0001_squashed_initial
                    app_one.0001_squashed_initial
                    app_seventeen.0001_squashed_initial
                    app_six.0001_squashed_initial
                    app_thirteen.0001_squashed_initial
                    app_thirteen.0002_squashed_initial
                    app_twelve.0001_squashed_initial
                    app_two.0001_squashed_initial
    ```

## Outcome

If you run the management command twice, as the following, you will end up with all the logged files.

```shell
python manage.py show_issue
python manage.py show_issue --use-fixed
```

You will see that the non-fixed version fails or succeeds randomly, and the fixed version always succeeds.

I'm hoping this shows that this proposed fix will help make squashing migrations easier to do, and circular dependency issues less likely to occur.
