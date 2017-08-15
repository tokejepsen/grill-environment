import hiero.core

import ftrack_api


def get_grill_bin():

    project_bin = hiero.core.project("Tag Presets").tagsBin()
    grill_bin = None
    for tag_bin in project_bin.items():
        if tag_bin.name() == "pyblish-grill":
            grill_bin = tag_bin

    if not grill_bin:
        grill_bin = hiero.core.Bin("pyblish-grill")
        project_bin.addItem(grill_bin)

    return grill_bin


def task_tags_init(*args):

    session = ftrack_api.Session()
    entities = session.query("select name from Type")

    grill_bin = get_grill_bin()
    entity_bin = hiero.core.Bin("ftrack.task")
    grill_bin.addItem(entity_bin)

    tags = []
    for entity in entities:
        tag = hiero.core.Tag(entity["name"])

        meta = tag.metadata()
        meta.setValue("tag.task_name", entity["name"].lower())
        meta.setValue("tag.type", entity["name"])
        meta.setValue("tag.ftrack", "task")

        tags.append((entity["name"], tag))

    tags = sorted(
        tags, key=lambda tag_tuple: tag_tuple[0].lower()
    )

    for _, tag in tags:
        entity_bin.addItem(tag)


def project_tags_init(*args):

    session = ftrack_api.Session()
    entities = session.query(
        "select name, full_name, project_schema_id, root, disk_id from "
        "Project where status is active"
    )

    grill_bin = get_grill_bin()
    entity_bin = hiero.core.Bin("ftrack.project")
    grill_bin.addItem(entity_bin)

    tags = []
    for entity in entities:
        tag = hiero.core.Tag(entity["full_name"])

        meta = tag.metadata()
        meta.setValue("tag.name", entity["name"])
        meta.setValue("tag.full_name", entity["full_name"])
        meta.setValue("tag.project_schema_id", entity["project_schema_id"])
        meta.setValue("tag.root", entity["root"])
        meta.setValue("tag.disk_id", entity["disk_id"])
        meta.setValue("tag.ftrack", "project")

        tags.append((entity["name"], tag))

    tags = sorted(
        tags, key=lambda tag_tuple: tag_tuple[0].lower()
    )

    for _, tag in tags:
        entity_bin.addItem(tag)


def init():

    hiero.core.events.registerInterest("kStartup", task_tags_init)
    hiero.core.events.registerInterest("kStartup", project_tags_init)
