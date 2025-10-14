# Project Testcase

## Overview

This project exists to provide a way to demonstrate an issue that can occur when squashing migrations in a project, and has in this project.

The issue occurs in django 4.2.24 (the original version) and django 5.2.7 (the version this is updated to use).

This project has its migrations set up in a way that if you call `showmigrations`, you could either have the command succeed, or you could get a CircularDependencyError.  Which occurs, depends on the way python iterates over the data of a set, which varies with each run.

Project code, app names, model names, and migrations have been changed to obscure what the project is and minimize things needed to test the issue.  These changes didn't affect the circular dependency issues that occur.

There are 2 distinct situations that can occur.  1 of them succeeds and 1 causes a CircularDependencyError.


The first step to help prevent circular dependency errors, was to comment out the dependencies to other apps in the older migrations.  This helps, but doesn't fix the issue.  The issue is related to this set containing migration names.  If this set is turned into a list, then the success rate jumps to 100%.

    https://github.com/django/django/blob/2d2e1a6a9dbfe0cba58a4d2486c51fccdb501d55/django/db/migrations/loader.py#L111-L115


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
Attempt 3 Succeeded
Attempt 4 Succeeded
...
Attempt 97 Failed
Attempt 98 Failed
Attempt 99 Succeeded
Attempt 100 Failed

Results:
    52 Succeeded
    48 Failed
    
Succeeding Attempts:
    {3, 4, 7, 8, 9, 11, 14, 15, 16, 17, 19, 21, 23, 24, 25, 26, 30, 32, 35, 38, 41, 43, 46, 48, 51, 53, 54, 55, 56, 58, 59, 60, 61, 62, 63, 65, 66, 67, 69, 71, 73, 77, 78, 80, 82, 83, 86, 87, 91, 95, 96, 99}

CircularDependencyError Attempts:
    {1, 2, 5, 6, 10, 12, 13, 18, 20, 22, 27, 28, 29, 31, 33, 34, 36, 37, 39, 40, 42, 44, 45, 47, 49, 50, 52, 57, 64, 68, 70, 72, 74, 75, 76, 79, 81, 84, 85, 88, 89, 90, 92, 93, 94, 97, 98, 100}
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
            app_one.0001_squashed_initial
                Children:
                    app_one.0002_squashed_initial
                    app_two.0001_squashed_initial
            app_one.0002_squashed_initial
                No Children
            app_two.0001_squashed_initial
                Children:
                    app_one.0002_squashed_initial
            ...
            users.0001_squashed_initial
                Children:
                    app_one.0001_squashed_initial
                    app_one.0002_squashed_initial
                    app_two.0001_squashed_initial
    ```

* `original_differences_between_successes_and_failures.txt` or `fixed_differences_between_successes_and_failures.txt` - compares the results of the first success to any failures.

    Output:
    ```
    Comparing Attempt #1 and #2
        Migrations:
            app_one.0002_squashed_initial
                Extra:
                    app_two.0001_squashed_initial
    ```


* `original_unique_migrations_and_children_filename.txt` or `fixed_unique_migrations_and_children_filename.txt` - contains all the unique structures of the migrations and their children.

    Output:
    ```
    Unique Migrations and Children #1 - success
        Migrations:
            app_one.0001_squashed_initial
                Children:
                    app_one.0002_squashed_initial
                    app_two.0001_squashed_initial
            app_one.0002_squashed_initial
                No Children
            app_two.0001_squashed_initial
                Children:
                    app_one.0002_squashed_initial
            ...
            users.0001_squashed_initial
                Children:
                    app_one.0001_squashed_initial
                    app_one.0002_squashed_initial
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
