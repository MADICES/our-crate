# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["datalab-api", "rocrate", "networkx"]
# ///

from pathlib import Path
from rocrate.rocrate import ROCrate, Entity

MADICES_PROFILE_PID = "https://github.com/MADICES/MADICES-2025/discussions/25"


def pprint_crate(crate):
    from rich.console import Console
    from rich.table import Table
    from networkx import DiGraph, generate_network_text

    ro_crate_graph = DiGraph()

    console = Console()
    table = Table(
        "@id",
        "@type",
        title="Entities in RO-Crate",
    )
    edges = []
    known_relationships = ["conformsTo", "hasPart"]
    for entity in crate.get_entities():
        entity_label = f"{entity.type}: {entity.id}"
        ro_crate_graph.add_node(entity_label)
        table.add_row(entity.id, entity.type)

        for rel in known_relationships:
            if related_entity := entity.get(rel):
                if isinstance(related_entity, list):
                    for re in related_entity:
                        if isinstance(re, str):
                            edges.append((entity_label, re))
                        else:
                            edges.append((entity_label, f"{re.type}: {re.id}"))
                else:
                    if isinstance(related_entity, str):
                        edges.append((entity_label, related_entity))
                    else:
                        edges.append(
                            (
                                entity_label,
                                f"{related_entity.type}: {related_entity.id}",
                            )
                        )

    ro_crate_graph.add_edges_from(edges)

    console.print(table)
    for _ in generate_network_text(ro_crate_graph):
        console.print(_)


def _find_repository_objects(crate: ROCrate) -> tuple[Entity | None, Entity | None]:
    """For a given RO-Crate, find the parent/child repository object hierarchy.

    Parameters:
        crate (ROCrate): The RO-Crate to search.

    Returns:
        If no valid RepositoryObject is found, returns a tuple of (None, None).
        If a valid base RepositoryObject is found, but no child RepositoryObject, returns a tuple of (base_repo_object, None).
        If both base and child RepositoryObjects are found, returns a tuple of (base_repo_object, child_repo_object).

    """
    # We are looking for the RepositortyObject that hasPart of the dummy node (indicated by # @id prefix),
    # rather than the root dataset itself.
    child_repo_object = None
    base_repo_object = None
    for entity in crate.get_entities():
        if "RepositoryObject" in entity.type and not entity.id.startswith("#"):
            base_repo_object = entity
            parts = entity.get("hasPart")
            if not isinstance(parts, list):
                parts = [parts]
            for part in parts:
                if isinstance(part, str):
                    continue
                if part.id.startswith("#") and part.type == "RepositoryObject":
                    subparts = part.get("hasPart")
                    if not isinstance(subparts, list):
                        subparts = [subparts]
                    for subpart in subparts:
                        if isinstance(subpart, str):
                            continue
                        if subpart.id == "./" and subpart.type == "Dataset":
                            child_repo_object = part
                            break

    if not base_repo_object and not child_repo_object:
        raise RuntimeError("No valid RepositoryObject found")

    if not child_repo_object:
        print(f"Continuing to upload with base RepositoryObject {base_repo_object}")

    else:
        print(f"Continuing to upload with child RepositoryObject {child_repo_object}")

    return (base_repo_object, child_repo_object)


def consume_crate(crate_path: Path):
    crate = ROCrate(crate_path)
    pprint_crate(crate)

    # Extract contextual entities and check e.g., profile
    profile = crate.get("./").get("conformsTo")
    if profile.id != MADICES_PROFILE_PID:
        raise RuntimeError(
            f"Unexpected RO-Crate profile: {profile.id}. Only MADICES-2025 ({MADICES_PROFILE_PID}) profile is supported."
        )

    parent, child = _find_repository_objects(crate)

    return crate, (parent, child)


def upload_and_import_crate_as_entry(crate_path: Path, api_url: str):
    from datalab_api import DatalabClient

    crate, (parent, child) = consume_crate(crate_path)

    if not parent:
        raise RuntimeError(
            "No parent RepositoryObject specified; cannot proceed with upload."
        )

    with DatalabClient(api_url) as client:
        datalab_parent = client.get_item(refcode=parent.id)

        if not datalab_parent:
            raise RuntimeError(
                f"Parent RepositoryObject with ID {parent.id} not found in Datalab."
            )

        if child:
            constituent_link = {
                "synthesis_constituents": [
                    {
                        "item": {"refcode": datalab_parent["refcode"]},
                        "quantity": None,
                        "unit": None,
                    }
                ]
            }
            target = client.create_item(item_data=constituent_link)

        else:
            target = datalab_parent

        target_refcode = target["refcode"]
        target_item_id = target["item_id"]

        # Add data to target
        dataset = crate.get("./")
        # Loop over files and upload them to target

        for part in dataset.get("hasPart"):
            if isinstance(part, str):
                continue
            if part.type == "File":
                file_path = crate_path / part.id.lstrip("./")
                client.upload_file(target_item_id, file_path)

                print(f"Added file {file_path} to item {target_refcode}")

        print(f"Updated entry at {target_refcode}")


if __name__ == "__main__":
    from pathlib import Path
    import sys

    crate_path = Path(sys.argv[1])
    upload_and_import_crate_as_entry(crate_path, "https://datalab.concatlab.eu")
