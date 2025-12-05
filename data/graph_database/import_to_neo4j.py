import csv
import os
import sys

from neo4j import GraphDatabase

# For data paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "processed_data")

# For imports (project root)
PROJECT_ROOT = os.path.dirname(BASE_DIR)
sys.path.append(PROJECT_ROOT)

from app.config import Config  # Import Config class


class Neo4jImporter:
    def __init__(self):
        """Initialize Neo4j driver using config settings"""
        self.driver = GraphDatabase.driver(
            Config.NEO4J_URI, auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD)
        )
        self.database = Config.NEO4J_DATABASE

    def close(self):
        """Close Neo4j connection"""
        self.driver.close()

    def clear_database(self):
        """Delete all existing nodes and relationships (use carefully)."""
        with self.driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("🗑️ Database cleared.")

    # ------------------ NODE IMPORTERS ------------------

    def import_symptoms(self, filepath):
        with self.driver.session(database=self.database) as session:
            with open(filepath, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    session.run(
                        """
                        MERGE (s:Symptom {id: $id})
                        SET s.name = $name,
                            s.description = $description,
                            s.body_site = $body_site,
                            s.commonness = $commonness
                        """,
                        id=row["symptom_id"],
                        name=row["name"],
                        description=row["description"],
                        body_site=row["body_site"],
                        commonness=row["commonness"],
                    )
        print("✅ Symptoms imported")

    def import_cures(self, filepath):
        with self.driver.session(database=self.database) as session:
            with open(filepath, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    session.run(
                        """
                        MERGE (c:Cure {id: $id})
                        SET c.name = $name,
                            c.description = $description,
                            c.type = $type
                        """,
                        id=row["cure_id"],
                        name=row["name"],
                        description=row["description"],
                        type=row["type"],
                    )
        print("✅ Cures imported")

    def import_medicines(self, filepath):
        with self.driver.session(database=self.database) as session:
            with open(filepath, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    session.run(
                        """
                        MERGE (m:Medicine {id: $id})
                        SET m.name = $name,
                            m.description = $description,
                            m.drug_class = $drug_class,
                            m.dosage_form = $dosage_form
                        """,
                        id=row["medicine_id"],
                        name=row["name"],
                        description=row["description"],
                        drug_class=row["drug_class"],
                        dosage_form=row["dosage_form"],
                    )
        print("✅ Medicines imported")

    def import_precautions(self, filepath):
        with self.driver.session(database=self.database) as session:
            with open(filepath, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    session.run(
                        """
                        MERGE (p:Precaution {id: $id})
                        SET p.name = $name,
                            p.description = $description
                        """,
                        id=row["precaution_id"],
                        name=row["name"],
                        description=row["description"],
                    )
        print("✅ Precautions imported")

    def import_diseases(self, filepath):
        with self.driver.session(database=self.database) as session:
            with open(filepath, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    session.run(
                        """
                        MERGE (d:Disease {id: $id})
                        SET d.name = $name,
                            d.canonical_id = $canonical_id,
                            d.description = $description,
                            d.prevalence = $prevalence,
                            d.risk_factors = $risk_factors
                        """,
                        id=row["disease_id"],
                        name=row["name"],
                        canonical_id=row["canonical_id"],
                        description=row["description"],
                        prevalence=row["prevalence"],
                        risk_factors=row["risk_factors"],
                    )
        print("✅ Diseases imported")

    # ------------------ RELATIONSHIP IMPORTERS ------------------

    def import_disease_symptom(self, filepath):
        with self.driver.session(database=self.database) as session:
            with open(filepath, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    session.run(
                        """
                        MATCH (d:Disease {id: $disease_id})
                        MATCH (s:Symptom {id: $symptom_id})
                        MERGE (d)-[r:HAS_SYMPTOM]->(s)
                        SET r.weight = toFloat($weight)
                        """,
                        disease_id=row["disease_id"],
                        symptom_id=row["symptom_id"],
                        weight=row["weight"],
                    )
        print("✅ Disease-Symptom relationships imported")

    def import_disease_cure(self, filepath):
        with self.driver.session(database=self.database) as session:
            with open(filepath, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    session.run(
                        """
                        MATCH (d:Disease {id: $disease_id})
                        MATCH (c:Cure {id: $cure_id})
                        MERGE (d)-[:CURED_BY]->(c)
                        """,
                        disease_id=row["disease_id"],
                        cure_id=row["cure_id"],
                    )
        print("✅ Disease-Cure relationships imported")

    def import_disease_medicine(self, filepath):
        with self.driver.session(database=self.database) as session:
            with open(filepath, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    session.run(
                        """
                        MATCH (d:Disease {id: $disease_id})
                        MATCH (m:Medicine {id: $medicine_id})
                        MERGE (d)-[:TREATED_WITH]->(m)
                        """,
                        disease_id=row["disease_id"],
                        medicine_id=row["medicine_id"],
                    )
        print("✅ Disease-Medicine relationships imported")

    def import_disease_precaution(self, filepath):
        with self.driver.session(database=self.database) as session:
            with open(filepath, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    session.run(
                        """
                        MATCH (d:Disease {id: $disease_id})
                        MATCH (p:Precaution {id: $precaution_id})
                        MERGE (d)-[:REQUIRES_PRECAUTION]->(p)
                        """,
                        disease_id=row["disease_id"],
                        precaution_id=row["precaution_id"],
                    )
        print("✅ Disease-Precaution relationships imported")


# ------------------ RUN SCRIPT ------------------

if __name__ == "__main__":
    importer = Neo4jImporter()

    importer.clear_database()

    # Import nodes
    importer.import_symptoms(os.path.join(PROCESSED_DIR, "symptoms.csv"))
    importer.import_cures(os.path.join(PROCESSED_DIR, "cures.csv"))
    importer.import_medicines(os.path.join(PROCESSED_DIR, "medicines.csv"))
    importer.import_precautions(os.path.join(PROCESSED_DIR, "precautions.csv"))
    importer.import_diseases(os.path.join(PROCESSED_DIR, "diseases.csv"))

    # Import relationships
    importer.import_disease_symptom(
        os.path.join(PROCESSED_DIR, "disease_has_symptom.csv")
    )
    importer.import_disease_cure(os.path.join(PROCESSED_DIR, "disease_has_cure.csv"))
    importer.import_disease_medicine(
        os.path.join(PROCESSED_DIR, "disease_has_medicine.csv")
    )
    importer.import_disease_precaution(
        os.path.join(PROCESSED_DIR, "disease_has_precaution.csv")
    )

    importer.close()
    print(f"🎉 All data imported into Neo4j database: {Config.NEO4J_DATABASE}")
