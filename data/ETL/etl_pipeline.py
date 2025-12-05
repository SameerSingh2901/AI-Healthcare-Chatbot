import csv
import json
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "raw_data")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed_data")

os.makedirs(PROCESSED_DIR, exist_ok=True)


def load_json(file_name):
    """Load a JSON file from raw_data directory."""
    path = os.path.join(RAW_DIR, file_name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_csv(file_name, rows, header):
    """Save rows to CSV in processed_data directory."""
    path = os.path.join(PROCESSED_DIR, file_name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def process_symptoms(symptoms_raw):
    """Convert symptoms JSON into CSV-ready rows."""
    return [
        {
            "symptom_id": s["uid"],
            "name": s["name"],
            "description": s["description"],
            "body_site": s["body_site"],
            "commonness": s["commonness"],
        }
        for s in symptoms_raw
    ]


def process_cures(cures_raw):
    """Convert cures JSON into CSV-ready rows."""
    return [
        {
            "cure_id": c["uid"],
            "name": c["name"],
            "description": c["description"],
            "type": c["type"],
        }
        for c in cures_raw
    ]


def process_medicines(medicines_raw):
    """Convert medicines JSON into CSV-ready rows."""
    return [
        {
            "medicine_id": m["uid"],
            "name": m["name"],
            "description": m["description"],
            "drug_class": m["drug_class"],
            "dosage_form": m["dosage_form"],
        }
        for m in medicines_raw
    ]


def process_precautions(precautions_raw):
    """Convert precautions JSON into CSV-ready rows."""
    return [
        {
            "precaution_id": p["uid"],
            "name": p["name"],
            "description": p["description"],
        }
        for p in precautions_raw
    ]


def process_diseases(diseases_raw):
    """Split diseases into disease nodes and relationships."""
    diseases = []
    symptom_relations = []
    cure_relations = []
    medicine_relations = []
    precaution_relations = []

    for d in diseases_raw:
        diseases.append(
            {
                "disease_id": d["uid"],
                "name": d["name"],
                "canonical_id": d["canonical_id"],
                "description": d["description"],
                "prevalence": d["prevalence"],
                "risk_factors": ";".join(d.get("risk_factors", [])),
            }
        )

        for s in d.get("symptoms", []):
            symptom_relations.append(
                {
                    "disease_id": d["uid"],
                    "symptom_id": s["symptom_id"],
                    "weight": s["weight"],
                }
            )

        for c in d.get("cures", []):
            cure_relations.append({"disease_id": d["uid"], "cure_id": c})

        for m in d.get("medicines", []):
            medicine_relations.append({"disease_id": d["uid"], "medicine_id": m})

        for p in d.get("precautions", []):
            precaution_relations.append({"disease_id": d["uid"], "precaution_id": p})

    return (
        diseases,
        symptom_relations,
        cure_relations,
        medicine_relations,
        precaution_relations,
    )


def run_etl():
    """Main ETL pipeline."""
    print("🔄 Starting ETL...")

    # Load raw JSON
    symptoms_raw = load_json("symptoms_raw.json")
    diseases_raw = load_json("diseases_raw.json")
    medicines_raw = load_json("medicines_raw.json")
    precautions_raw = load_json("precautions_raw.json")
    cures_raw = load_json("cures_raw.json")

    # Process nodes
    symptoms = process_symptoms(symptoms_raw)
    cures = process_cures(cures_raw)
    medicines = process_medicines(medicines_raw)
    precautions = process_precautions(precautions_raw)

    # Save nodes
    save_csv(
        "symptoms.csv",
        symptoms,
        ["symptom_id", "name", "description", "body_site", "commonness"],
    )
    save_csv("cures.csv", cures, ["cure_id", "name", "description", "type"])
    save_csv(
        "medicines.csv",
        medicines,
        ["medicine_id", "name", "description", "drug_class", "dosage_form"],
    )
    save_csv("precautions.csv", precautions, ["precaution_id", "name", "description"])

    # Process diseases & relations
    (
        diseases,
        symptom_relations,
        cure_relations,
        medicine_relations,
        precaution_relations,
    ) = process_diseases(diseases_raw)

    # Save disease nodes
    save_csv(
        "diseases.csv",
        diseases,
        [
            "disease_id",
            "name",
            "canonical_id",
            "description",
            "prevalence",
            "risk_factors",
        ],
    )

    # Save relations
    save_csv(
        "disease_has_symptom.csv",
        symptom_relations,
        ["disease_id", "symptom_id", "weight"],
    )
    save_csv("disease_has_cure.csv", cure_relations, ["disease_id", "cure_id"])
    save_csv(
        "disease_has_medicine.csv", medicine_relations, ["disease_id", "medicine_id"]
    )
    save_csv(
        "disease_has_precaution.csv",
        precaution_relations,
        ["disease_id", "precaution_id"],
    )

    print("✅ ETL completed. CSV files are saved in processed_data/")


if __name__ == "__main__":
    run_etl()
