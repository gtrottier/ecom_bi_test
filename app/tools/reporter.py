import os
from typing import Any

import matplotlib.pyplot as plt
from langchain_core.tools import tool

from app.schema import ToolResult


def _generate_distribution_chart(score: float) -> str:
    """
    Génère un graphique de sentiment avec matplotlib.
    """
    try:
        plt.figure(figsize=(6, 2))
        plt.barh(
            ["Sentiment"], [score], color="green" if score > 0 else "red", height=0.5
        )
        plt.xlim(-1, 1)
        plt.axvline(0, color="black", linewidth=1)
        plt.title(f"Polarité du Sentiment (Score: {score:+.2f})")
        plt.xlabel("Négatif <---> Positif")
        plt.grid(axis="x", linestyle="--", alpha=0.7)

        filename = "sentiment_distribution.png"
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
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

        # Section données produit (Scraper)
        if product_data:
            report_lines.append("## Aperçu du Marché")
            if isinstance(product_data, list):
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

        # Section analyse de sentiment (Sentiment Analyzer)
        if sentiment_data:
            report_lines.append("## Analyse de sentiment")

            score = sentiment_data.get("sentiment_score", 0)
            overall = sentiment_data.get("overall_sentiment", "N/A")

            report_lines.append(f"- **Sentiment Global**: {overall}")
            report_lines.append(f"- **Score**: {score}")

            # Visualisation jauge polarité
            width = 20
            pos = int((score + 1) / 2 * width)
            pos = max(0, min(width, pos))
            gauge_chars = list("-" * (width + 1))
            gauge_chars[width // 2] = "|"
            gauge_chars[pos] = "█"
            gauge = "".join(gauge_chars)
            report_lines.append(f"- **Indicateur**: `Neg [{gauge}] Pos` ({score:+.2f})")
            report_lines.append("")

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
