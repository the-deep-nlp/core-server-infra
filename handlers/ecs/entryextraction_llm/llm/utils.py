import os
import re

import psycopg2
from llm.prompt_utils import (
    MULTI_DESCRIPTION
)

af_widget_by_id = (
    "SELECT * from analysis_framework_widget ll WHERE ll.analysis_framework_id={}"
)


def manage_description(name, description):

    m_desc, s_desc = description
    _, s_name = name
    if s_desc:
        return s_desc
    elif m_desc:
        return f"{m_desc}. Subcategory: {s_name}"


def _sanitize_keys_with_uniqueness(key, max_length: int = 64):

    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", key)
    sanitized = re.sub(r"^_+", "", sanitized)  # pydantic model keys can't start with _
    sanitized = sanitized[:max_length]

    return sanitized


def add_element(name, description, alias, main_class=None):

    element = {
        "alias": alias,
        "type": "boolean",
        "default": False,
    }
    if main_class:
        element["main_class"] = main_class
    if (isinstance(description, str) and description) or (
        isinstance(description, list) and any(c != "" for c in description)
    ):
        element.update(
            {
                "description": (
                    description
                    if isinstance(description, str)
                    else manage_description(name, description)
                )
            }
        )
    else:
        element.update(
            {"description": name if isinstance(name, str) else f"{name[0]}, {name[1]}"}
        )
    element.update(
        {
            "plain_description": (
                name if isinstance(name, str) else f"{name[0]}, {name[1]}"
            )
        }
    )
    return {
        (
            _sanitize_keys_with_uniqueness(name.replace(" ", "_").lower())
            if isinstance(name, str)
            else _sanitize_keys_with_uniqueness(
                [el.replace(" ", "_").lower() for el in name][1]
            )
        ): element
    }


def process_primary_tags(ex: list, order="columns", type_="2d", max_length: int = 50):

    def get_tooltip(el):
        if el.get("tooltip"):
            return el.get("tooltip")
        else:
            return ""

    properties = {}
    id_to_info = {}
    for c in ex[order]:

        name_main = c["label"].strip()
        description_main = get_tooltip(c)
        alias_main = c["key"]
        id_to_info.update({c["key"]: {"label": c["label"], "order": c["order"]}})

        if type_ == "1d":
            for cc in c["cells"]:
                name = cc["label"].strip()
                description = get_tooltip(cc)
                alias = cc["key"]
                id_to_info.update(
                    {cc["key"]: {"label": cc["label"], "order": cc["order"]}}
                )
                prop = add_element(
                    name=[name_main, name],
                    description=[description_main, description],
                    alias="->".join([alias_main, alias]),
                )
                properties.update(prop)

        elif (
            type_ == "2d" and
            f"sub{order.title()}" in c.keys() and
            c.get(f"sub{order.title()}")
        ):
            for cc in c[f"sub{order.title()}"]:

                name = cc["label"].strip()
                description = get_tooltip(cc)
                alias = cc["key"]
                id_to_info.update(
                    {cc["key"]: {"label": cc["label"], "order": cc["order"]}}
                )
                prop = add_element(
                    name=[name_main, name],
                    description=[description_main, description],
                    alias="->".join([alias_main, alias]),
                    main_class=name_main,
                )
                properties.update(prop)
        else:
            properties.update(
                add_element(name_main, description_main, alias_main, name_main)
            )

    if len(properties) >= max_length:
        for k, v in properties.items():
            # change description to the short one in case of a big framework
            properties[k]["description"] = properties[k]["plain_description"]

    return properties, id_to_info


def combine_properties(
    properties_row: dict,
    properties_columns: dict,
    max_length: int = 50,
    reduce_on_length: bool = True,
):

    schema = {}
    for i, col in properties_columns.items():
        for j, row in properties_row.items():

            name = _sanitize_keys_with_uniqueness(f"{i}_{j}")
            alias = f"{col['alias']}->{row['alias']}"
            description = MULTI_DESCRIPTION.format(
                col["description"], row["description"]
            )
            plain_description = MULTI_DESCRIPTION.format(
                col["plain_description"], row["plain_description"]
            )

            schema.update(
                {
                    name: {
                        "alias": alias,
                        "type": "boolean",
                        "default": False,
                        "description": description,
                        "plain_description": plain_description,
                    }
                }
            )

            if len(schema) >= max_length and reduce_on_length:
                # if the schema is big let's not consider the full description (if present)
                # because this will cause a big slow down of the classification process
                # and conrresponding losing of context by the llm
                for k, v in schema.items():
                    schema[k]["description"] = schema[k]["plain_description"]
    return schema


class CursorWrapper:
    """
    This is just a wrapper over psycopg2 cursor. This exists because we use
    named cursor which needs to be closed after each call to execute. Named
    cursor is used to prevent fetching of all rows. This also contains the
    original connection.

    The idea is to initialize with a cursor and a connection and override the
    execute function(which closes existing cursor and re-creates) and rest of
    the attributes are just the attributes of the cursor object. See
    `__getattr__` method below.
    """

    def __init__(self, cursor, connection):
        self.connection = connection
        self.cursor = cursor
        # TODO: find ways to close connection

    def __getattr__(self, name):
        if name == "description":
            return self.cursor.description
        if name == "execute":
            try:
                self.cursor.close()
            except Exception:
                pass
            else:
                self.cursor = self.connection.cursor(name="deepl_cursor")
            finally:
                return self.cursor.execute
        return getattr(self.cursor, name)


def connect_db():

    params = {
        "host": os.environ.get("DEEP_DB_HOST"),
        "port": os.environ.get("DEEP_DB_PORT"),
        "dbname": os.environ.get("DEEP_DB_NAME"),
        "user": os.environ.get("DEEP_DB_USER"),
        "password": os.environ.get("DEEP_DB_PASSWORD"),
        "sslmode": "require",
    }
    connection = psycopg2.connect(**params)
    # Use named cursor to make it server side which allows for controlling the
    # fetch sizes
    cursor: psycopg2.cursor = connection.cursor(name="deepl_cursor")
    return CursorWrapper(cursor, connection)


def get_words_count(text):
    """
    Counts the words in the text
    """
    if text:
        w = re.sub(r"[^\w\s]", "", text)
        w = re.sub(r"_", "", w)
        return len(w.split())
    return 0


def reformat_old_output(output: list):

    # in order to avoid the problem i noticed on the webpages extractions.
    # TODO: re-shape the text extraction component to be more useful and in line with the extraction
    if isinstance(output[0], str):
        output = [output]

    reformat = {
        "metadata": {
            "total_pages": len(output),
            "total_words_count": get_words_count(
                " ".join([s for page in output for s in page])
            ),
        },
        "blocks": [],
    }

    for i, page in enumerate(output):
        for j, sentence in enumerate(page):
            reformat["blocks"].append(
                {"type": "text", "page": i, "text": sentence, "textOrder": j}
            )
    return reformat
