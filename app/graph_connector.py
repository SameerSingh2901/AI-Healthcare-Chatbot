from neo4j import GraphDatabase
from config import Config 


class GraphConnector:
    def __init__(self):
        """Initialize Neo4j driver using config settings"""
        self.driver = GraphDatabase.driver(
            Config.NEO4J_URI,
            auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD)
        )
        self.database = Config.NEO4J_DATABASE  

    def close(self):
        """Close Neo4j driver."""
        self.driver.close()

    # =======================
    # Query Functions
    # =======================

    def get_disease_by_symptoms(self, symptoms):
        """
        Find diseases connected to ALL given symptoms, along with their details.
        """
        with self.driver.session(database=self.database) as session:
            query = """
            // Find diseases that match ALL provided symptoms
            MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)
            WHERE s.name IN $symptoms
            WITH d, COUNT(DISTINCT s) AS matched_symptoms
            WHERE matched_symptoms = SIZE($symptoms)

            // Collect details
            OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(s2:Symptom)
            OPTIONAL MATCH (d)-[:CURED_BY]->(c:Cure)
            OPTIONAL MATCH (d)-[:TREATED_WITH]->(m:Medicine)
            OPTIONAL MATCH (d)-[:REQUIRES_PRECAUTION]->(p:Precaution)

            RETURN d.id AS disease_id,
                d.name AS disease_name,
                d.description AS description,
                d.prevalence AS prevalence,
                COLLECT(DISTINCT {name:s2.name, commonness:s2.commonness}) AS symptoms,
                COLLECT(DISTINCT {name:c.name, description:c.description, type:c.type}) AS cures,
                COLLECT(DISTINCT {name:m.name, drug_class:m.drug_class, dosage_form:m.dosage_form}) AS medicines,
                COLLECT(DISTINCT {name:p.name, description:p.description}) AS precautions
            """
            return session.run(query, symptoms=symptoms).data()


    # =======================
    # Context Builders (for RAG)
    # =======================

    def build_context_from_symptoms(self, symptoms):
        """
        Build a rich context string from symptoms → multiple diseases with full details.
        """
        diseases = self.get_disease_by_symptoms(symptoms)
        if not diseases:
            return "No matching diseases found for given symptoms."

        context = f"User symptoms: {', '.join(symptoms)}\n\n"
        context += "Possible Diseases and Details:\n"

        for d in diseases:
            context += f"\n🩺 {d['disease_name']} (Prevalence: {d.get('prevalence','N/A')})\n"
            context += f"Description: {d.get('description','N/A')}\n"

            if d["symptoms"]:
                context += "🔹 Symptoms:\n"
                for s in d["symptoms"]:
                    if s["name"]:
                        context += f"- {s['name']} (commonness: {s.get('commonness','unknown')})\n"

            if d["cures"]:
                context += "\n💊 Cures:\n"
                for c in d["cures"]:
                    if c["name"]:
                        context += f"- {c['name']} ({c.get('type','N/A')}): {c.get('description','')}\n"

            if d["medicines"]:
                context += "\n💊 Medicines:\n"
                for m in d["medicines"]:
                    if m["name"]:
                        context += f"- {m['name']} (Class: {m.get('drug_class','N/A')}, Form: {m.get('dosage_form','N/A')})\n"

            if d["precautions"]:
                context += "\n⚠️ Precautions:\n"
                for p in d["precautions"]:
                    if p["name"]:
                        context += f"- {p['name']}: {p.get('description','')}\n"

            context += "\n" + "-"*40 + "\n"

        return context.strip()
    

# =======================
if __name__ == "__main__":
    connector = GraphConnector()

    context = connector.build_context_from_symptoms(["Sneezing", "Fever"])
    print("=== Context from Symptoms === \n")
    print(context)

    connector.close()
