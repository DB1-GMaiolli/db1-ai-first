#!/usr/bin/env python3
"""
RAG Pipeline - NovaTech Documentation
Ingestao, busca semantica e avaliacao automatica de retrieval.
"""

import sys
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions

DOCS_PATH = Path("./docs")
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "novatech_docs"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
REPORT_PATH = Path("../1.3.md")
N_RESULTS = 5


def ingest():
    # Separadores hierarquicos respeitam limites semanticos naturais do texto,
    # o overlap de 200 chars evita cortar conceitos que cruzam chunks,
    # e 1200 chars e suficiente para contexto sem degradar a qualidade do embedding.
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". "],
        chunk_size=1200,
        chunk_overlap=200,
    )

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        client.delete_collection(COLLECTION_NAME)
        print("Colecao anterior removida.")
    except Exception:
        pass

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    collection = client.create_collection(COLLECTION_NAME, embedding_function=ef)

    all_docs, all_ids, all_metas = [], [], []
    for txt_file in sorted(DOCS_PATH.glob("*.txt")):
        text = txt_file.read_text(encoding="utf-8")
        chunks = splitter.split_text(text)
        for i, chunk in enumerate(chunks):
            all_docs.append(chunk)
            all_ids.append(f"{txt_file.stem}_{i}")
            all_metas.append({"source": txt_file.name, "chunk_index": i})
        print(f"  {txt_file.name}: {len(chunks)} chunks")

    collection.add(documents=all_docs, ids=all_ids, metadatas=all_metas)
    return len(all_docs)


def search(query, n=N_RESULTS):
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    collection = client.get_collection(COLLECTION_NAME, embedding_function=ef)
    results = collection.query(query_texts=[query], n_results=n)
    return [
        {
            "chunk_id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "score": results["distances"][0][i],
        }
        for i in range(len(results["ids"][0]))
    ]


def build_prompt(chunks, question):
    context = "\n\n".join(
        f"[{i + 1}] Fonte: {c['source']} | Score: {c['score']:.4f}\n{c['text']}"
        for i, c in enumerate(chunks)
    )
    return (
        "SYSTEM:\n"
        "Voce e um assistente especializado na documentacao operacional da NovaTech (logistica e transporte).\n"
        "Responda apenas com base nos trechos fornecidos abaixo.\n"
        'Se a informacao nao estiver presente nos trechos, diga exatamente: "Nao encontrado nos documentos".\n'
        "Cite a fonte entre colchetes ao final de cada afirmacao relevante.\n"
        "\n"
        "CONTEXTO:\n"
        f"{context}\n"
        "\n"
        f"PERGUNTA:\n{question}\n"
        "\n"
        "RESPOSTA:"
    )


TESTS = [
    {
        "question": "Qual o prazo de devolucao de mercadorias?",
        "keywords": ["7 (sete) dias uteis", "7 dias uteis", "sete dias", "dias uteis"],
    },
    {
        "question": "Posso devolver carga perigosa?",
        "keywords": [
            "NAO sao elegiveis",
            "Gestao de Riscos",
            "ramal 4500",
            "perigosas",
            "tratamento especial",
            "nao pode pelo processo padrao",
        ],
    },
    {
        "question": "Qual o SLA do cliente Gold?",
        "keywords": ["2h uteis", "24h uteis", "30min", "4h", "Gold"],
    },
    {
        "question": "Existe o tier Platinum na NovaTech?",
        "keywords": [
            "Nao existe",
            "nao existem",
            "Gold, Silver e Standard",
            "tres tiers",
            "3 (tres) tiers",
            "Platinum",
        ],
    },
    {
        "question": "Qual o multiplicador regional para o Norte no frete especial?",
        "keywords": ["Norte", "1.8", "1.6", "multiplicador"],
    },
    {
        "question": "O que acontece com uma carga danificada em transito?",
        "keywords": ["danificada", "48h", "sinistros@novatech.com.br", "Juridico", "laudo"],
    },
    {
        "question": "Quais sao as penalidades por descumprimento de SLA?",
        "keywords": ["credito de 5%", "credito de 10%", "violacao", "penalidades", "descumprimento"],
    },
]


def evaluate_chunk(text, keywords):
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


def run_tests():
    results = []
    for test in TESTS:
        chunks = search(test["question"])
        prompt = build_prompt(chunks, test["question"])
        evaluations = [
            {"chunk": c, "correct": evaluate_chunk(c["text"], test["keywords"])}
            for c in chunks
        ]
        hit_rate = sum(1 for e in evaluations if e["correct"]) / len(evaluations) if evaluations else 0
        results.append(
            {
                "question": test["question"],
                "keywords": test["keywords"],
                "evaluations": evaluations,
                "hit_rate": hit_rate,
                "prompt": prompt,
            }
        )
    return results


def format_report(results, total_chunks):
    lines = []
    lines.append("## Configuracao\n")
    lines.append(f"- **Modelo de embedding:** `{MODEL_NAME}`")
    lines.append(f"- **Estrategia de chunking:** RecursiveCharacterTextSplitter")
    lines.append(f"- **Separadores:** `[\"\\\\n\\\\n\", \"\\\\n\", \". \"]`")
    lines.append(f"- **Tamanho do chunk:** 1200 caracteres")
    lines.append(f"- **Overlap:** 200 caracteres")
    lines.append(f"- **Chunks recuperados por busca:** {N_RESULTS}")
    lines.append(f"- **Total de chunks indexados:** {total_chunks}")
    lines.append("")

    for idx, result in enumerate(results, 1):
        n_correct = sum(1 for e in result["evaluations"] if e["correct"])
        n_total = len(result["evaluations"])
        lines.append("---\n")
        lines.append(f"## Teste {idx}: {result['question']}\n")
        lines.append("| # | Fonte | Score | Preview (80 chars) | Correto |")
        lines.append("|---|-------|-------|-------------------|---------|")
        for j, ev in enumerate(result["evaluations"], 1):
            c = ev["chunk"]
            preview = c["text"][:80].replace("\n", " ")
            correct_icon = "Sim" if ev["correct"] else "Nao"
            lines.append(f"| {j} | {c['source']} | {c['score']:.4f} | {preview} | {correct_icon} |")
        lines.append("")
        lines.append(
            f"**Taxa de acerto:** {result['hit_rate']:.0%} "
            f"({n_correct}/{n_total} chunks com keyword do gabarito)\n"
        )
        lines.append("**Prompt completo (build_prompt):**\n")
        lines.append("```")
        lines.append(result["prompt"])
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


def main():
    print("=" * 60)
    print("RAG Pipeline - NovaTech")
    print("=" * 60)

    print("\n[1/3] Ingerindo documentos...")
    total_chunks = ingest()
    print(f"Total: {total_chunks} chunks indexados no ChromaDB.")

    print("\n[2/3] Executando testes de retrieval...")
    results = run_tests()
    for r in results:
        n_correct = sum(1 for e in r["evaluations"] if e["correct"])
        print(f"  [{n_correct}/{len(r['evaluations'])}] {r['question'][:60]}")

    print("\n[3/3] Gerando relatorio em 1.3.md...")
    report = format_report(results, total_chunks)

    original = REPORT_PATH.read_text(encoding="utf-8")
    marker = "Resposta:"
    idx = original.find(marker)
    if idx == -1:
        print("ERRO: marcador 'Resposta:' nao encontrado em 1.3.md")
        sys.exit(1)

    updated = original[: idx + len(marker)] + "\n\n" + report
    REPORT_PATH.write_text(updated, encoding="utf-8")

    print("\n" + "=" * 60)
    print("Relatorio gerado com sucesso em 1.3.md")
    print("=" * 60)


if __name__ == "__main__":
    main()
