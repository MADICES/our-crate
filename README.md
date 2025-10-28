# our-crate

> [!WARNING] 
> :construction: Extremely WIP :construction:

Simple utility for consuming crates produced with the profile described in [this discussion](https://github.com/MADICES/MADICES-2025/discussions/25) and ingesting into a [*datalab*](https://github.com/datalab-org/datalab).

## Usage

```shell
uv run --script datalab-ro-create-importer.py <ro-crate-path> <datalab_api_url>
```

## Examples

### Writing a child of an existing entry and attaching new data to it

The example in `./examples/results.3.zip` has the following structure in the
`ro-crate-metadata.json`:

```json
{
    "@context": "https://w3id.org/ro/crate/1.1/context",
    "@graph": [
        {
            "@id": "./",
            "@type": "Dataset",
            "conformsTo": {
                "@id": "https://github.com/MADICES/MADICES-2025/discussions/25"
            },
            "datePublished": "2025-10-25T10:23:43+00:00",
            "hasPart": [
                {
                    "@id": "results.3.nc"
                }
            ]
        },
        {
            "@id": "ro-crate-metadata.json",
            "@type": "CreativeWork",
            "about": {
                "@id": "./"
            },
            "conformsTo": {
                "@id": "https://w3id.org/ro/crate/1.1"
            }
        },
        {
            "@id": "https://github.com/MADICES/MADICES-2025/discussions/25",
            "@type": "Profile",
            "version": "0.2"
        },
        {
            "@id": "https://orcid.org/0000-0002-4359-5003",
            "@type": "Person"
        },
        {
            "@id": "concat:WHDEPS",
            "@type": "RepositoryObject",
            "hasPart": {
                "@id": "#2859c8c6-ac8e-489b-96ff-82bfe66f49d8"
            }
        },
        {
            "@id": "#2859c8c6-ac8e-489b-96ff-82bfe66f49d8",
            "@type": "RepositoryObject",
            "hasPart": {
                "@id": "./"
            }
        },
        {
            "@id": "results.3.nc",
            "@type": "File",
            "author": {
                "@id": "https://orcid.org/0000-0002-4359-5003"
            },
            "encodingFormat": "application/netcdf"
        }
    ]
}
```

This should be interpreted as follows:

- Find the `RepositoryObject` with `@id` `concat:WHDEPS` and check that the entry exists.
- Find the dummy anchor `RepositoryObject` with `@id` `#2859c8c6-ac8e-489b-96ff-82bfe66f49d8` and create a child entry of the `concat:WHDEPS` entry with a randomly assigned ID.
- Upload any files to *datalab* and attach them to this new child entry. 

When running the script, you get the following output:

```
$ uv run --script datalab-ro-create-importer.py examples/results.3.zip https://datalab.concatlab.eu
                            Entities in RO-Crate
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ @id                                                    ┃ @type            ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ ./                                                     │ Dataset          │
│ ro-crate-metadata.json                                 │ CreativeWork     │
│ results.3.nc                                           │ File             │
│ https://github.com/MADICES/MADICES-2025/discussions/25 │ Profile          │
│ https://orcid.org/0000-0002-4359-5003                  │ Person           │
│ concat:WHDEPS                                          │ RepositoryObject │
│ #2859c8c6-ac8e-489b-96ff-82bfe66f49d8                  │ RepositoryObject │
└────────────────────────────────────────────────────────┴──────────────────┘
╟── CreativeWork: ro-crate-metadata.json
╎   └─╼ https://w3id.org/ro/crate/1.1
╟── Person: https://orcid.org/0000-0002-4359-5003
╙── RepositoryObject: concat:WHDEPS
    └─╼ RepositoryObject: #2859c8c6-ac8e-489b-96ff-82bfe66f49d8
        └─╼ Dataset: ./
            ├─╼ Profile: https://github.com/MADICES/MADICES-2025/discussions/25
            └─╼ File: results.3.nc
Continuing to upload with child RepositoryObject <#2859c8c6-ac8e-489b-96ff-82bfe66f49d8 RepositoryObject>
```

