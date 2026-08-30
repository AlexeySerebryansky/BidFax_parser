from sqlalchemy import inspect

from database.connection import engine
from database.models import Car


def normalize_type(column_type):

    type_name = column_type.__class__.__name__.upper()

    mapping = {
        "BIGINTEGER": "BIGINT",
        "INTEGER": "INTEGER",
        "SMALLINTEGER": "SMALLINT",
        "STRING": "VARCHAR",
        "TEXT": "TEXT",
        "DATE": "DATE",
        "DATETIME": "TIMESTAMP",
        "ARRAY": "ARRAY",
    }

    return mapping.get(type_name, type_name)


def types_match(db_type, model_type):

    db_type = db_type.upper()
    model_type = normalize_type(model_type)

    # TIMESTAMP / DATETIME
    if db_type == "TIMESTAMP" and model_type == "TIMESTAMP":
        return True

    # VARCHAR(n) / String(n)
    if db_type.startswith("VARCHAR") and model_type == "VARCHAR":
        return True

    return db_type == model_type


def check_database():

    inspector = inspect(engine)

    table_name = Car.__tablename__

    print("=" * 70)
    print("FINAL DATABASE / MODEL CHECK")
    print("=" * 70)

    # --------------------------------------------------
    # TABLE
    # --------------------------------------------------

    tables = inspector.get_table_names()

    if table_name not in tables:
        print(f"[ERROR] Table '{table_name}' does not exist")
        return False

    print(f"[OK] Table '{table_name}' exists")

    # --------------------------------------------------
    # DATABASE STRUCTURE
    # --------------------------------------------------

    db_columns = inspector.get_columns(table_name)

    db_structure = {
        column["name"]: {
            "type": str(column["type"]).upper(),
            "nullable": column["nullable"],
        }
        for column in db_columns
    }

    # --------------------------------------------------
    # MODEL STRUCTURE
    # --------------------------------------------------

    model_structure = {
        column.name: {
            "type": column.type,
            "nullable": column.nullable,
        }
        for column in Car.__table__.columns
    }

    # --------------------------------------------------
    # COLUMN NAMES
    # --------------------------------------------------

    db_names = set(db_structure)
    model_names = set(model_structure)

    missing_in_model = db_names - model_names
    missing_in_db = model_names - db_names

    errors = False

    if missing_in_model:

        errors = True

        print(
            "\n[ERROR] Columns exist in DB "
            "but missing in model:"
        )

        for name in sorted(missing_in_model):
            print(f"    - {name}")

    if missing_in_db:

        errors = True

        print(
            "\n[ERROR] Columns exist in model "
            "but missing in DB:"
        )

        for name in sorted(missing_in_db):
            print(f"    - {name}")

    if not missing_in_model and not missing_in_db:

        print(
            "\n[OK] Column names match"
        )

    # --------------------------------------------------
    # TYPE / NULLABLE
    # --------------------------------------------------

    print("\nTYPE / NULLABLE CHECK:")

    common_columns = db_names & model_names

    for name in sorted(common_columns):

        db_column = db_structure[name]
        model_column = model_structure[name]

        db_type = db_column["type"]
        model_type = model_column["type"]

        db_nullable = db_column["nullable"]
        model_nullable = model_column["nullable"]

        # TYPE

        if not types_match(
            db_type,
            model_type,
        ):

            print(
                f"[ERROR] {name}: type mismatch"
            )

            print(
                f"        DB:    {db_type}"
            )

            print(
                f"        Model: {model_type}"
            )

            errors = True

        # NULLABLE

        elif db_nullable != model_nullable:

            print(
                f"[ERROR] {name}: nullable mismatch"
            )

            print(
                f"        DB:    nullable={db_nullable}"
            )

            print(
                f"        Model: nullable={model_nullable}"
            )

            errors = True

        else:

            print(
                f"[OK] {name}: "
                f"{db_type}, "
                f"nullable={db_nullable}"
            )

    # --------------------------------------------------
    # PRIMARY KEY
    # --------------------------------------------------

    print("\nPRIMARY KEY CHECK:")

    pk = inspector.get_pk_constraint(table_name)

    db_pk_columns = pk.get("constrained_columns", [])

    model_pk_columns = [
        column.name
        for column in Car.__table__.columns
        if column.primary_key
    ]

    if db_pk_columns == model_pk_columns:

        print(
            f"[OK] Primary key: {db_pk_columns}"
        )

    else:

        print("[ERROR] Primary key mismatch")

        print(
            f"        DB:    {db_pk_columns}"
        )

        print(
            f"        Model: {model_pk_columns}"
        )

        errors = True

    # --------------------------------------------------
    # INDEXES
    # --------------------------------------------------

    print("\nDATABASE INDEXES:")

    indexes = inspector.get_indexes(table_name)

    for index in indexes:

        print(
            f"    {index['name']} -> "
            f"{index['column_names']}"
        )

    # --------------------------------------------------
    # RESULT
    # --------------------------------------------------

    print("\n" + "=" * 70)

    if not errors:

        print(
            "DATABASE AND MODEL MATCH"
        )

        print(
            "Everything looks good."
        )

    else:

        print(
            "DATABASE AND MODEL DO NOT MATCH"
        )

    print("=" * 70)

    return not errors



check_database()