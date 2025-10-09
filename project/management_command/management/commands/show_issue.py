from importlib import import_module
from importlib import reload
import pkgutil
import random
import sys

from django.apps import apps
from django.core.management.commands.showmigrations import (
    Command as DjangoShowMigrationsCommand,
)
from django.db.migrations.exceptions import BadMigrationError
from django.db.migrations.exceptions import CircularDependencyError
from django.db.migrations.exceptions import NodeNotFoundError
from django.db.migrations.graph import MigrationGraph
from django.db.migrations.loader import MIGRATIONS_MODULE_NAME
from django.db.migrations.loader import MigrationLoader as DjangoMigrationLoader
from django.db.migrations.recorder import MigrationRecorder


attempts = {
    "success": set(),
    "circular": set(),
}
migrations_and_children = {
    "successes": {},
    "failures": {},
}
unique_migrations_and_children = []


class MigrationLoader(DjangoMigrationLoader):
    def __init__(self, *args, **kwargs):
        # Added code - start
        self.error = None
        self._attempt_number = kwargs["attempt_number"]
        kwargs.pop("attempt_number")

        self._use_fixed = kwargs["use_fixed"]
        kwargs.pop("use_fixed")

        try:
            super().__init__(*args, **kwargs)
            self.result = "success"
        except CircularDependencyError as e:
            self.result = "circular"
            self.error = str(e)
        # Added code - end

    def load_disk(self):
        """Load the migrations from all INSTALLED_APPS from disk."""
        self.disk_migrations = {}
        self.unmigrated_apps = set()
        self.migrated_apps = set()

        for app_config in apps.get_app_configs():
            # Get the migrations module directory
            module_name, explicit = self.migrations_module(app_config.label)
            if module_name is None:
                self.unmigrated_apps.add(app_config.label)
                continue
            was_loaded = module_name in sys.modules
            try:
                module = import_module(module_name)
            except ModuleNotFoundError as e:
                if (explicit and self.ignore_no_migrations) or (
                    not explicit and MIGRATIONS_MODULE_NAME in e.name.split(".")
                ):
                    self.unmigrated_apps.add(app_config.label)
                    continue
                raise
            else:
                # Module is not a package (e.g. migrations.py).
                if not hasattr(module, "__path__"):
                    self.unmigrated_apps.add(app_config.label)
                    continue
                # Empty directories are namespaces. Namespace packages have no
                # __file__ and don"t use a list for __path__. See
                # https://docs.python.org/3/reference/import.html#namespace-packages
                if getattr(module, "__file__", None) is None and not isinstance(
                    module.__path__, list
                ):
                    self.unmigrated_apps.add(app_config.label)
                    continue
                # Force a reload if it"s already loaded (tests need this)
                if was_loaded:
                    reload(module)
            self.migrated_apps.add(app_config.label)
            migration_names = {
                name
                for _, name, is_pkg in pkgutil.iter_modules(module.__path__)
                if not is_pkg and name[0] not in "_~"
            }

            # Added code - start
            # For some reason set appears to always be iterated in the same order during a
            # single process run. To mimic running show migrations each time, shuffle them.
            migration_names = list(migration_names)
            random.shuffle(migration_names)
            # Added code - end

            # Load migrations
            for migration_name in migration_names:
                migration_path = "%s.%s" % (module_name, migration_name)
                try:
                    migration_module = import_module(migration_path)
                except ImportError as e:
                    if "bad magic number" in str(e):
                        raise ImportError(
                            "Couldn't import %r as it appears to be a stale "
                            ".pyc file." % migration_path
                        ) from e
                    else:
                        raise
                if not hasattr(migration_module, "Migration"):
                    raise BadMigrationError(
                        "Migration %s in app %s has no Migration class"
                        % (migration_name, app_config.label)
                    )
                self.disk_migrations[app_config.label, migration_name] = (
                    migration_module.Migration(
                        migration_name,
                        app_config.label,
                    )
                )

            del migration_names

    def load_disk_fixed(self):
        """Load the migrations from all INSTALLED_APPS from disk."""
        self.disk_migrations = {}
        self.unmigrated_apps = set()
        self.migrated_apps = set()
        for app_config in apps.get_app_configs():
            # Get the migrations module directory
            module_name, explicit = self.migrations_module(app_config.label)
            if module_name is None:
                self.unmigrated_apps.add(app_config.label)
                continue
            was_loaded = module_name in sys.modules
            try:
                module = import_module(module_name)
            except ModuleNotFoundError as e:
                if (explicit and self.ignore_no_migrations) or (
                    not explicit and MIGRATIONS_MODULE_NAME in e.name.split(".")
                ):
                    self.unmigrated_apps.add(app_config.label)
                    continue
                raise
            else:
                # Module is not a package (e.g. migrations.py).
                if not hasattr(module, "__path__"):
                    self.unmigrated_apps.add(app_config.label)
                    continue
                # Empty directories are namespaces. Namespace packages have no
                # __file__ and don"t use a list for __path__. See
                # https://docs.python.org/3/reference/import.html#namespace-packages
                if getattr(module, "__file__", None) is None and not isinstance(
                    module.__path__, list
                ):
                    self.unmigrated_apps.add(app_config.label)
                    continue
                # Force a reload if it"s already loaded (tests need this)
                if was_loaded:
                    reload(module)
            self.migrated_apps.add(app_config.label)

            # Modified code - start
            migration_names = [
                name
                for _, name, is_pkg in pkgutil.iter_modules(module.__path__)
                if not is_pkg and name[0] not in "_~"
            ]
            # Modified code - end

            # Load migrations
            for migration_name in migration_names:
                migration_path = "%s.%s" % (module_name, migration_name)
                try:
                    migration_module = import_module(migration_path)
                except ImportError as e:
                    if "bad magic number" in str(e):
                        raise ImportError(
                            "Couldn't import %r as it appears to be a stale "
                            ".pyc file." % migration_path
                        ) from e
                    else:
                        raise
                if not hasattr(migration_module, "Migration"):
                    raise BadMigrationError(
                        "Migration %s in app %s has no Migration class"
                        % (migration_name, app_config.label)
                    )
                self.disk_migrations[app_config.label, migration_name] = (
                    migration_module.Migration(
                        migration_name,
                        app_config.label,
                    )
                )

    def build_graph(self):
        """
        Build a migration dependency graph using both the disk and database.
        You"ll need to rebuild the graph if you apply migrations. This isn"t
        usually a problem as generally migration stuff runs in a one-shot process.
        """
        # Modified code - start
        # Load disk data
        if self._use_fixed:
            self.load_disk_fixed()
        else:
            self.load_disk()
        # Modified code - end

        # Load database data
        if self.connection is None:
            self.applied_migrations = {}
        else:
            recorder = MigrationRecorder(self.connection)
            self.applied_migrations = recorder.applied_migrations()
        # To start, populate the migration graph with nodes for ALL migrations
        # and their dependencies. Also make note of replacing migrations at this step.
        self.graph = MigrationGraph()
        self.replacements = {}
        for key, migration in self.disk_migrations.items():
            self.graph.add_node(key, migration)
            # Replacing migrations.
            if migration.replaces:
                self.replacements[key] = migration
        for key, migration in self.disk_migrations.items():
            # Internal (same app) dependencies.
            self.add_internal_dependencies(key, migration)
        # Add external dependencies now that the internal ones have been resolved.
        for key, migration in self.disk_migrations.items():
            self.add_external_dependencies(key, migration)
        # Carry out replacements where possible and if enabled.
        if self.replace_migrations:
            for key, migration in self.replacements.items():
                # Get applied status of each of this migration"s replacement
                # targets.
                applied_statuses = [
                    (target in self.applied_migrations) for target in migration.replaces
                ]
                # The replacing migration is only marked as applied if all of
                # its replacement targets are.
                if all(applied_statuses):
                    self.applied_migrations[key] = migration
                else:
                    self.applied_migrations.pop(key, None)
                # A replacing migration can be used if either all or none of
                # its replacement targets have been applied.
                if all(applied_statuses) or (not any(applied_statuses)):
                    self.graph.remove_replaced_nodes(key, migration.replaces)
                else:
                    # This replacing migration cannot be used because it is
                    # partially applied. Remove it from the graph and remap
                    # dependencies to it (#25945).
                    self.graph.remove_replacement_node(key, migration.replaces)
        # Ensure the graph is consistent.
        try:
            self.graph.validate_consistency()
        except NodeNotFoundError as exc:
            # Check if the missing node could have been replaced by any squash
            # migration but wasn"t because the squash migration was partially
            # applied before. In that case raise a more understandable exception
            # (#23556).
            # Get reverse replacements.
            reverse_replacements = {}
            for key, migration in self.replacements.items():
                for replaced in migration.replaces:
                    reverse_replacements.setdefault(replaced, set()).add(key)
            # Try to reraise exception with more detail.
            if exc.node in reverse_replacements:
                candidates = reverse_replacements.get(exc.node, set())
                is_replaced = any(
                    candidate in self.graph.nodes for candidate in candidates
                )
                if not is_replaced:
                    tries = ", ".join("%s.%s" % c for c in candidates)
                    raise NodeNotFoundError(
                        "Migration {0} depends on nonexistent node ('{1}', '{2}'). "
                        "Django tried to replace migration {1}.{2} with any of [{3}] "
                        "but wasn't able to because some of the replaced migrations "
                        "are already applied.".format(
                            exc.origin, exc.node[0], exc.node[1], tries
                        ),
                        exc.node,
                    ) from exc
            raise
        self.graph.ensure_not_cyclic()


class Command(DjangoShowMigrationsCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-a",
            "--attempts",
            default=100,
            type=int,
            help="Number of times to attempt showing migrations. "
            "Will store the data in the migration graph node_map and "
            "the number of successes and failures with this data.",
        )
        parser.add_argument(
            "-f",
            "--use-fixed",
            action="store_true",
            help="Use the fixed load_disk function or not.",
        )
        super().add_arguments(parser)

    def handle(self, *args, **options):
        self.attempts = options["attempts"]
        self.use_fixed = options["use_fixed"]

        if self.use_fixed:
            self.stdout.write("Using ordered migration names.", self.style.HTTP_INFO)
        else:
            self.stdout.write(
                "Using shuffled set of migration names.", self.style.HTTP_INFO
            )

        super().handle(*args, **options)

    def show_list(self, connection, app_names=None):
        global attempts
        global migrations_and_children
        global unique_migrations_and_children

        if self.use_fixed:
            successes_filename = "fixed_successes.txt"
            failures_filename = "fixed_failures.txt"
            differences_between_successes_filename = (
                "fixed_differences_between_successes.txt"
            )
            differences_between_failures_filename = (
                "fixed_differences_between_failures.txt"
            )
            differences_between_successes_and_failures_filename = (
                "fixed_differences_between_successes_and_failures.txt"
            )
            unique_migrations_and_children_filename = (
                "fixed_unique_migrations_and_children_filename.txt"
            )
        else:
            successes_filename = "original_successes.txt"
            failures_filename = "original_failures.txt"
            differences_between_successes_filename = (
                "original_differences_between_successes.txt"
            )
            differences_between_failures_filename = (
                "original_differences_between_failures.txt"
            )
            differences_between_successes_and_failures_filename = (
                "original_differences_between_successes_and_failures.txt"
            )
            unique_migrations_and_children_filename = (
                "original_unique_migrations_and_children_filename.txt"
            )

        with (
            open(successes_filename, "w") as S,
            open(failures_filename, "w") as F,
            open(differences_between_successes_filename, "w") as DS,
            open(differences_between_failures_filename, "w") as DF,
            open(differences_between_successes_and_failures_filename, "w") as DSF,
            open(unique_migrations_and_children_filename, "w") as U,
        ):
            for attempt_number in range(1, self.attempts + 1):
                # Load migrations from disk/DB
                loader = MigrationLoader(
                    connection,
                    ignore_no_migrations=True,
                    use_fixed=self.use_fixed,
                    attempt_number=attempt_number,
                )
                graph = loader.graph

                # Store the migrations/children and result
                attempts[loader.result].add(attempt_number)

                match loader.result:
                    case "success":
                        self.stdout.write(
                            f"Attempt {attempt_number} Succeeded", self.style.SUCCESS
                        )
                        file = S
                        file.write(f"Attempt #{attempt_number}\n")
                        migrations_and_children["successes"][attempt_number] = {}
                        attempt_data = migrations_and_children["successes"][
                            attempt_number
                        ]

                    case "circular":
                        self.stdout.write(
                            f"Attempt {attempt_number} Failed", self.style.ERROR
                        )
                        file = F
                        file.write(f"Attempt #{attempt_number}\n")
                        file.write(f"    Cycle:\n        {loader.error}\n")
                        migrations_and_children["failures"][attempt_number] = {}
                        attempt_data = migrations_and_children["failures"][
                            attempt_number
                        ]

                file.write("    Migrations:\n")
                for migration_key, node in sorted(graph.node_map.items()):
                    migration_key = ".".join(migration_key)
                    attempt_data[migration_key] = set()
                    file.write(f"        {migration_key}\n")
                    if node.children:
                        file.write("            Children:\n")
                        for child_node in sorted(node.children):
                            child_key = ".".join(child_node.key)
                            attempt_data[migration_key].add(child_key)
                            file.write(f"                {child_key}\n")
                    else:
                        file.write("            No Children\n")
                file.write("\n")

                min_successes_attempt_number = min(
                    migrations_and_children["successes"], default=None
                )
                min_failures_attempt_number = min(
                    migrations_and_children["failures"], default=None
                )

                match loader.result:
                    case "success":
                        if (
                            min_successes_attempt_number
                            and min_successes_attempt_number != attempt_number
                        ):
                            original = migrations_and_children["successes"][
                                min_successes_attempt_number
                            ]
                            compare_to(
                                min_successes_attempt_number,
                                original,
                                attempt_number,
                                attempt_data,
                                DS,
                            )

                    case "circular":
                        if (
                            min_failures_attempt_number
                            and min_failures_attempt_number != attempt_number
                        ):
                            original = migrations_and_children["failures"][
                                min_failures_attempt_number
                            ]
                            compare_to(
                                min_failures_attempt_number,
                                original,
                                attempt_number,
                                attempt_data,
                                DF,
                            )

                        if (
                            min_successes_attempt_number
                            and min_successes_attempt_number != attempt_number
                        ):
                            original = migrations_and_children["successes"][
                                min_successes_attempt_number
                            ]
                            compare_to(
                                min_successes_attempt_number,
                                original,
                                attempt_number,
                                attempt_data,
                                DSF,
                            )

                attempt_data["result"] = loader.result
                if attempt_data not in unique_migrations_and_children:
                    unique_migrations_and_children.append(attempt_data)

            file = U
            for index, unique_data in enumerate(
                unique_migrations_and_children, start=1
            ):
                file.write(
                    f"Unique Migrations and Children #{index} - {unique_data['result']}\n"
                )
                del unique_data["result"]
                file.write("    Migrations:\n")
                for migration_key, child_data in sorted(unique_data.items()):
                    file.write(f"        {migration_key}\n")
                    if child_data:
                        file.write("            Children:\n")
                        for child_key in sorted(child_data):
                            file.write(f"                {child_key}\n")
                    else:
                        file.write("            No Children\n")

                file.write("\n")

            self.stdout.write("\nResults:\n", self.style.HTTP_INFO)

            self.stdout.write(
                f"    {len(attempts['success'])} Succeeded", self.style.SUCCESS
            )
            self.stdout.write(
                f"    {len(attempts['circular'])} Failed", self.style.ERROR
            )

            self.stdout.write(
                f"\nSucceeding Attempts:\n    {attempts['success']}", self.style.SUCCESS
            )
            self.stdout.write(
                f"\nCircularDependencyError Attempts:\n    {attempts['circular']}",
                self.style.ERROR,
            )


def compare_to(
    original_attempt_number, original, current_attempt_number, current, file
):
    header_written = False
    differences_found = False
    for migration, children in sorted(current.items()):
        extra = children - original[migration]
        missing = original[migration] - children
        if missing or extra:
            differences_found = True
            if not header_written:
                file.write(
                    f"Comparing Attempt #{original_attempt_number} and #{current_attempt_number}\n    Migrations:\n"
                )
                header_written = True
            file.write(f"        {migration}\n")
            if missing:
                file.write("            Missing:\n")
                for missing_child in missing:
                    file.write(f"                {missing_child}\n")
            if extra:
                file.write("            Extra:\n")
                for extra_child in extra:
                    file.write(f"                {extra_child}\n")
            file.write("\n")

    if not differences_found:
        file.write(
            f"Comparing Attempt #{original_attempt_number} and #{current_attempt_number}\n    No Differences\n\n"
        )
