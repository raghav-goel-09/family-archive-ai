from typing import List, Dict, Any


def process_retrieved_data(
    records: List[Dict[str, Any]],
    audience: str = "younger_members"
) -> Dict[str, Any]:

    if not records:
        return {
            "records": [],
            "conflicts": [],
            "context": "No relevant archive records were retrieved."
        }

    allowed_records = []

    for record in records:
        if (
            audience == "younger_members"
            and record.get("sensitivity", "public") != "public"
        ):
            continue

        allowed_records.append(record)

    groups = {}

    for record in allowed_records:
        canonical_id = record.get("duplicate_of") or record.get("asset_id")
        groups.setdefault(canonical_id, []).append(record)

    conflicts = []

    for canonical_id, group in groups.items():
        people_claims = {}

        for record in group:
            people = record.get("people", "").strip()

            if people:
                people_claims.setdefault(
                    people,
                    []
                ).append(record.get("source", "Unknown source"))

        if len(people_claims) > 1:
            conflicts.append({
                "asset_id": canonical_id,
                "type": "different_people_identifications",
                "claims": people_claims
            })

    context_parts = []

    for canonical_id, group in groups.items():

        context_parts.append(
            f"CANONICAL ASSET: {canonical_id}\n"
            f"TYPE: {group[0].get('item_type', 'Unknown')}"
        )

        for record in group:
            context_parts.append(
                f"Source: {record.get('source', 'Unknown')}\n"
                f"Content: {record.get('content', '')}\n"
                f"Location: {record.get('location') or 'Unknown'}\n"
                f"Year: {record.get('estimated_year') or 'Unknown'}\n"
                f"People mentioned: {record.get('people') or 'None'}\n"
                f"Similarity score: "
                f"{record.get('similarity_score', 'N/A')}\n---"
            )

    if conflicts:
        context_parts.append("\nCONFLICTS DETECTED:")

        for conflict in conflicts:
            context_parts.append(
                f"Asset {conflict['asset_id']} has different identifications:"
            )

            for people, sources in conflict["claims"].items():
                context_parts.append(
                    f"- {people}: {', '.join(sources)}"
                )

    return {
        "records": allowed_records,
        "conflicts": conflicts,
        "context": "\n".join(context_parts)
    }


if __name__ == "__main__":
    print("This module processes records supplied by the RAG retrieval module.")
