import json
import numpy as np
from groq import Groq
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document_chunk import DocumentChunk
from app.models.company import Company
from app.models.emission import Emission
from app.models.target import Target
from app.services.embedding_service import embed_text, embed_batch, chunk_text

groq_client = Groq(api_key=settings.GROQ_API_KEY)

SYSTEM_PROMPT = (
    "Tu es l'assistant ESG de Verdustry. Tu réponds en français, de façon claire et concise, "
    "en te basant UNIQUEMENT sur le contexte fourni (réglementation CSRD/CBAM/GRI et données de "
    "l'entreprise). Si le contexte ne permet pas de répondre, dis-le clairement plutôt que d'inventer. "
    "Cite la source de l'information quand c'est pertinent (ex: [Donnée entreprise] ou [CSRD])."
)


class RagService:
    def __init__(self, db: Session):
        self.db = db

    def ingest_regulatory_document(self, source_ref: str, text: str) -> int:
        chunks = chunk_text(text)
        if not chunks:
            return 0
        vectors = embed_batch(chunks)
        for content, vector in zip(chunks, vectors):
            self.db.add(DocumentChunk(
                source_type="regulatory",
                source_ref=source_ref,
                company_id=None,
                content=content,
                embedding=json.dumps(vector),
            ))
        self.db.commit()
        return len(chunks)

    def sync_company_data(self, company_id: int) -> int:
        self.db.query(DocumentChunk).filter(
            DocumentChunk.source_type == "company_data",
            DocumentChunk.company_id == company_id,
        ).delete()

        company = self.db.query(Company).filter(Company.id == company_id).first()
        if not company:
            self.db.commit()
            return 0

        emissions = self.db.query(Emission).filter(Emission.company_id == company_id).all()
        targets = self.db.query(Target).filter(Target.company_id == company_id).all()

        texts = []
        by_period: dict[str, dict[int, float]] = {}
        for e in emissions:
            by_period.setdefault(e.period, {}).setdefault(e.scope, 0.0)
            by_period[e.period][e.scope] += e.value

        for period, scopes in sorted(by_period.items()):
            s1, s2, s3 = scopes.get(1, 0), scopes.get(2, 0), scopes.get(3, 0)
            total = s1 + s2 + s3
            texts.append(
                f"Pour la période {period}, l'entreprise {company.name} (secteur {company.sector}) "
                f"a émis un total de {total:.2f} tCO2e, réparti en Scope 1: {s1:.2f} tCO2e, "
                f"Scope 2: {s2:.2f} tCO2e, Scope 3: {s3:.2f} tCO2e."
            )

        for t in targets:
            texts.append(
                f"L'entreprise {company.name} a fixé un objectif '{t.name}' sur l'indicateur "
                f"{t.metric}, avec une valeur cible de {t.target_value} pour l'année {t.target_year} "
                f"(référence: {t.baseline_value} en {t.baseline_year})."
            )

        if not texts:
            self.db.commit()
            return 0

        vectors = embed_batch(texts)
        for content, vector in zip(texts, vectors):
            self.db.add(DocumentChunk(
                source_type="company_data",
                source_ref=f"company_{company_id}_summary",
                company_id=company_id,
                content=content,
                embedding=json.dumps(vector),
            ))
        self.db.commit()
        return len(texts)

    def _retrieve(self, query: str, company_id: int, top_k: int = 6) -> list[DocumentChunk]:
        query_vector = np.array(embed_text(query))

        rows = (
            self.db.query(DocumentChunk)
            .filter(
                (DocumentChunk.source_type == "regulatory")
                | (
                    (DocumentChunk.source_type == "company_data")
                    & (DocumentChunk.company_id == company_id)
                )
            )
            .all()
        )

        def cos_sim(row):
            v = np.array(json.loads(row.embedding))
            denom = (np.linalg.norm(query_vector) * np.linalg.norm(v)) + 1e-9
            return float(np.dot(query_vector, v) / denom)

        rows.sort(key=cos_sim, reverse=True)
        return rows[:top_k]

    def chat(self, company_id: int, message: str, history: list[dict] | None = None) -> dict:
        chunks = self._retrieve(message, company_id)

        if not chunks:
            context = "Aucune donnée disponible pour cette entreprise ou cette question."
        else:
            context = "\n\n".join(
                f"[{c.source_type} - {c.source_ref}] {c.content}" for c in chunks
            )

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history:
            messages.extend(history[-6:])
        messages.append({
            "role": "user",
            "content": f"Contexte:\n{context}\n\nQuestion: {message}",
        })

        completion = groq_client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            temperature=0.2,
            max_tokens=800,
        )
        answer = completion.choices[0].message.content

        sources = [
            {"sourceType": c.source_type, "sourceRef": c.source_ref}
            for c in chunks
        ]
        return {"answer": answer, "sources": sources}