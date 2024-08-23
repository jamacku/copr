"""
Change a storage for a project

Copr supports different storage solutions for repositories with the built RPM
packages (e.g. results directory on copr-backend or Pulp). This script allows to
configure the storage type for a given project and while doing so, it makes sure
DNF repositories for the project are created.

Existing builds are not migrated from one storage to another. This may be an
useful feature but it is not implemented yet.
"""

import sys
import click
from copr_common.enums import StorageEnum
from coprs import db
from coprs.logic.coprs_logic import CoprsLogic
from coprs.logic.actions_logic import ActionsLogic


@click.command()
@click.argument("fullname", required=True)
@click.argument(
    "storage",
    required=True,
    type=click.Choice(["backend", "pulp"])
)
def change_storage(fullname, storage):
    """
    Change a storage for a project
    """
    if "/" not in fullname:
        print("Must be a fullname, e.g. @copr/copr-dev")
        sys.exit(1)

    ownername, projectname = fullname.split("/", 1)
    copr = CoprsLogic.get_by_ownername_coprname(ownername, projectname)
    copr.storage = StorageEnum(storage)
    db.session.add(copr)

    action = ActionsLogic.send_createrepo(copr)
    db.session.add(action)

    db.session.commit()
    print("Configured storage for {0} to {1}".format(copr.full_name, storage))
    print("Submitted action to create repositories: {0}".format(action.id))
    print("Existing builds not migrated (not implemented yet).")
