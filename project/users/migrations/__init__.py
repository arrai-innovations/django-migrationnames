def create_groups_up(apps, schema_editor, groups_to_create):
    db_alias = schema_editor.connection.alias
    groups = apps.get_model("auth", "Group").objects.using(db_alias)
    permissions = apps.get_model("auth", "Permission").objects.using(db_alias)
    content_types = apps.get_model("contenttypes", "ContentType").objects.using(
        db_alias
    )
    for group in groups_to_create:
        g = groups.create(name=group["name"])
        g_permissions = []
        for permission in group["permissions"]:
            ct, ct_created = content_types.get_or_create(**permission["content_type"])
            p, p_created = permissions.get_or_create(
                content_type=ct,
                **{k: v for k, v in permission.items() if k not in ["content_type"]},
            )
            g_permissions.append(p)
        g.permissions.set(g_permissions)


def create_groups_down(apps, schema_editor, groups_to_create):
    apps.get_model("auth", "Group").objects.using(
        schema_editor.connection.alias
    ).filter(name__in=[v["name"] for v in groups_to_create]).delete()


def update_groups_up(apps, schema_editor, groups_to_update):
    db_alias = schema_editor.connection.alias
    groups = apps.get_model("auth", "Group").objects.using(db_alias)
    permissions = apps.get_model("auth", "Permission").objects.using(db_alias)
    content_types = apps.get_model("contenttypes", "ContentType").objects.using(
        db_alias
    )
    for group in groups_to_update:
        g = groups.get(name=group["name"])
        for permission in group["permissions"]:
            ct, ct_created = content_types.get_or_create(**permission["content_type"])
            p, p_created = permissions.get_or_create(
                content_type=ct,
                **{k: v for k, v in permission.items() if k not in ["content_type"]},
            )
            g.permissions.add(p)


def update_groups_down(apps, schema_editor, groups_to_update):
    db_alias = schema_editor.connection.alias
    groups = apps.get_model("auth", "Group").objects.using(db_alias)
    permissions = apps.get_model("auth", "Permission").objects.using(db_alias)
    content_types = apps.get_model("contenttypes", "ContentType").objects.using(
        db_alias
    )
    for group in groups_to_update:
        g = groups.get(name=group["name"])
        for permission in group["permissions"]:
            ct = content_types.filter(**permission["content_type"]).first()
            if ct is not None:  # In case the content type doesn't exist.
                # In case the permission has already been removed from the group (manually), we need to not blowup.
                p = permissions.filter(
                    content_type=ct, codename=permission["codename"]
                ).first()
                if p is not None:
                    g.permissions.remove(p)


def delete_groups_up(apps, schema_editor, groups_to_delete):
    update_groups_down(apps, schema_editor, groups_to_delete)


def delete_groups_down(apps, schema_editor, groups_to_delete):
    update_groups_up(apps, schema_editor, groups_to_delete)
