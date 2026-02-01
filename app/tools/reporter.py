import os
import random
from typing import Any

import matplotlib.pyplot as plt
from langchain_core.tools import tool

from app.schema import ToolResult


def _generate_distribution_chart(score: float) -> str:
    """
    Génère un graphique de distribution des notes avec matplotlib.

    Contenu entièrement arbitraire, pourrait prendre de vrai données, agréger les notes, etc.
    """
    try:
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        total_votes = 100
        for _ in range(total_votes):
            vote = int(random.gauss(score, 0.8))
            vote = max(1, min(5, vote))
            distribution[vote] += 1

        ratings = list(distribution.keys())
        counts = list(distribution.values())

        plt.figure(figsize=(6, 4))
        bars = plt.bar(ratings, counts, color="skyblue", edgecolor="black")
        plt.title(f"Distribution des Notes (Score: {score}/5)")
        plt.xlabel("Étoiles")
        plt.ylabel("Nombre de votes")
        plt.xticks(ratings)
        plt.grid(axis="y", linestyle="--", alpha=0.7)

        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{int(height)}%",
                ha="center",
                va="bottom",
            )
        filename = "sentiment_distribution.png"
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
        print(f"File saved to {os.path.abspath(filename)}")
        return filename
    except Exception:
        plt.close()
        return ""


@tool
def generate_report(
    product_name: str,
    product_data: list[dict[str, Any]] | None = None,
    sentiment_data: dict[str, Any] | None = None,
) -> ToolResult:
    """
    Génère un rapport d'analyse structuré en markdown incluant:
    - Une vue d'ensemble du produit (prix, disponibilité par plateforme).
    - Une analyse de sentiment avec score, étoiles, et graphique de distribution.

    """
    try:
        report_lines = []

        # Titre
        report_lines.append(f"# Rapport d'Analyse: {product_name}")
        report_lines.append("")

        # Section Données Produit (Scraper)
        if product_data:
            report_lines.append("## Aperçu du Marché")
            if isinstance(product_data, list):
                # Table header
                report_lines.append("| Plateforme | Prix | Disponibilité | Lien |")
                report_lines.append("|---|---|---|---|")
                for item in product_data:
                    platform = item.get("platform", "N/A")
                    price = item.get("price", "N/A")
                    availability = item.get("availability", "N/A")
                    url = item.get("url", "#")
                    report_lines.append(
                        f"| {platform} | {price} | {availability} | [Lien]({url}) |"
                    )
            else:
                report_lines.append("_Format de données produit non reconnu._")
            report_lines.append("")

        # Section Analyse de Sentiment (Sentiment Analyzer)
        if sentiment_data:
            report_lines.append("## Analyse de Sentiment")

            score = sentiment_data.get("sentiment_score", 0)
            overall = sentiment_data.get("overall_sentiment", "N/A")

            report_lines.append(f"- **Sentiment Global**: {overall}")
            report_lines.append(f"- **Score**: {score}/5")

            # Visualisation étoiles "dingbats"
            filled = int(max(0, min(5, score)))
            empty = 5 - filled
            bar = "★" * filled + "☆" * empty
            report_lines.append(f"- **Indicateur**: `{bar}` ({score})")
            report_lines.append("")

            # Visualisation Matplotlib (Image)
            chart_file = _generate_distribution_chart(score)
            if chart_file:
                abs_path = os.path.abspath(chart_file)
                report_lines.append(f"![Distribution]({abs_path})")
                report_lines.append("")

            if "total_mentions" in sentiment_data:
                report_lines.append(
                    f"- **Mentions Totales**: {sentiment_data['total_mentions']}"
                )

            if "key_positives" in sentiment_data:
                positives = ", ".join(sentiment_data["key_positives"])
                report_lines.append(f"- **Points Forts**: {positives}")

            if "key_negatives" in sentiment_data:
                negatives = ", ".join(sentiment_data["key_negatives"])
                report_lines.append(f"- **Points Faibles**: {negatives}")

            if "insights" in sentiment_data:
                report_lines.append(f"\n> **Insight**: {sentiment_data['insights']}")
            report_lines.append("")

        if not product_data and not sentiment_data:
            report_lines.append("_Aucune donnée détaillée fournie pour ce rapport._")

        final_report = "\n".join(report_lines)

    except Exception as e:
        return {
            "status": "error",
            "error_type": "generation_error",
            "message": str(e),
            "retryable": False,
        }

    return {"status": "ok", "data": {"report": final_report}}
