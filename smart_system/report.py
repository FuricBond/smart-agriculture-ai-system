"""
Report Generator — Smart Agriculture System v2.0
====================================================
Generates professionally formatted Smart Farm Reports
with system version, confidence analysis, soil score
explanations, overall health grade, and cross-module advisory.

Author  : Smart Agriculture AI Team
Version : 2.0.0
"""

from __future__ import annotations

import os
import datetime
from typing import Dict, List, Optional

from . import config


class ReportGenerator:
    """
    Professional Smart Farm Report generator.

    Produces a comprehensive, visually structured report
    combining all prediction results, risk analyses,
    recommendations, and cross-module intelligence.
    """

    @staticmethod
    def generate(
        disease_result: Dict,
        crop_result: Dict,
        yield_result: Dict,
        soil_quality: Dict,
        disease_risk: Dict,
        yield_classification: Dict,
        disease_treatments: List[str],
        crop_advice: List[str],
        yield_advice: List[str],
        overall_health: Optional[Dict] = None,
        combined_advisory: Optional[List[str]] = None,
    ) -> str:
        """
        Generate the complete Smart Farm Report.

        Parameters
        ----------
        disease_result       : dict - Disease prediction output
        crop_result          : dict - Crop recommendation output
        yield_result         : dict - Yield prediction output
        soil_quality         : dict - Soil quality analysis
        disease_risk         : dict - Disease risk assessment
        yield_classification : dict - Yield level classification
        disease_treatments   : list - Disease treatment recommendations
        crop_advice          : list - Crop growing recommendations
        yield_advice         : list - Yield improvement recommendations
        overall_health       : dict - Overall farm health (optional)
        combined_advisory    : list - Cross-module advisory (optional)

        Returns
        -------
        str
            Formatted report string for terminal display.
        """
        timestamp = datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p")
        W = 64  # Report width (inner content)

        def _line(content: str = "") -> str:
            """Create a bordered line."""
            return "║ " + content.ljust(W) + " ║"

        def _sep() -> str:
            """Section separator."""
            return "╟─" + "─" * W + "─╢"

        def _header(text: str) -> str:
            """Section header."""
            return "║ " + text.ljust(W) + " ║"

        lines: List[str] = []

        # ══════════════════════════════════════════════════════
        # REPORT HEADER
        # ══════════════════════════════════════════════════════
        lines.append("")
        lines.append("╔═" + "═" * W + "═╗")
        lines.append("║ " + "🌾  SMART FARM REPORT".center(W) + " ║")
        lines.append("║ " + timestamp.center(W) + " ║")
        lines.append("║ " + f"System v{config.SYSTEM_VERSION}".center(W) + " ║")
        lines.append("╠═" + "═" * W + "═╣")

        # ══════════════════════════════════════════════════════
        # SECTION 1: DISEASE DETECTION
        # ══════════════════════════════════════════════════════
        lines.append(_header("🔬  DISEASE DETECTION"))
        lines.append(_sep())

        if disease_result.get('success'):
            plant = disease_result.get('plant', 'Unknown')
            condition = disease_result.get('condition', 'Unknown')
            conf = disease_result.get('confidence', 0)

            lines.append(_line(f"Plant:         {plant}"))
            lines.append(_line(f"Disease:       {condition}"))
            lines.append(_line(f"Confidence:    {conf:.1f}%"))

            # Confidence classification
            if conf >= config.CONFIDENCE_HIGH:
                conf_label = config.CONFIDENCE_LABELS['HIGH']
            elif conf >= config.CONFIDENCE_MODERATE:
                conf_label = config.CONFIDENCE_LABELS['MODERATE']
            else:
                conf_label = config.CONFIDENCE_LABELS['LOW']
            lines.append(_line(f"Reliability:   {conf_label}"))

            # Confidence bar
            bar_len = int(conf / 100 * 35)
            bar = "█" * bar_len + "░" * (35 - bar_len)
            lines.append(_line(f"  [{bar}]"))

            # Top predictions
            top_preds = disease_result.get('top_predictions', [])
            if top_preds and len(top_preds) > 1:
                lines.append(_line())
                lines.append(_line("Top-5 Predictions:"))
                for rank, (name, prob) in enumerate(top_preds[:5], 1):
                    display = name.replace('___', ' — ').replace('_', ' ')
                    if len(display) > 32:
                        display = display[:29] + "..."
                    lines.append(_line(
                        f"  {rank}. {display:<34} {prob:5.1f}%"))
        else:
            error = disease_result.get('error', 'Not available')
            lines.append(_line(f"❌ {error}"))

        # ══════════════════════════════════════════════════════
        # SECTION 2: CROP RECOMMENDATION
        # ══════════════════════════════════════════════════════
        lines.append(_sep())
        lines.append(_header("🌱  CROP RECOMMENDATION"))
        lines.append(_sep())

        if crop_result.get('success'):
            crop_name = crop_result.get('crop_name', 'Unknown')
            conf = crop_result.get('confidence', 0)

            lines.append(_line(f"Recommended:   {crop_name}"))
            lines.append(_line(f"Confidence:    {conf:.1f}%"))

            # Top predictions
            top = crop_result.get('top_predictions', [])
            if top and len(top) > 1:
                lines.append(_line())
                lines.append(_line("Top-5 Crop Candidates:"))
                for rank, (name, prob) in enumerate(top[:5], 1):
                    bar_len = int(prob / 100 * 25)
                    bar = "█" * bar_len + "░" * (25 - bar_len)
                    lines.append(_line(
                        f"  {rank}. {name:<15} {prob:5.1f}%  {bar}"))

            # Input summary
            inp = crop_result.get('input_data', {})
            if inp:
                lines.append(_line())
                lines.append(_line("Input Parameters:"))
                lines.append(_line(
                    f"  N={inp.get('N',0):.0f}  "
                    f"P={inp.get('P',0):.0f}  "
                    f"K={inp.get('K',0):.0f}  "
                    f"Temp={inp.get('Temperature',0):.1f}°C"))
                lines.append(_line(
                    f"  Humidity={inp.get('Humidity',0):.0f}%  "
                    f"pH={inp.get('pH',0):.1f}  "
                    f"Rainfall={inp.get('Rainfall',0):.0f}mm"))
        else:
            error = crop_result.get('error', 'Not available')
            lines.append(_line(f"❌ {error}"))

        # ══════════════════════════════════════════════════════
        # SECTION 3: YIELD PREDICTION
        # ══════════════════════════════════════════════════════
        lines.append(_sep())
        lines.append(_header("📊  YIELD PREDICTION"))
        lines.append(_sep())

        if yield_result.get('success'):
            y_val = yield_result.get('predicted_yield', 0)
            y_area = yield_result.get('area', 'N/A')
            y_crop = yield_result.get('crop', 'N/A')
            y_year = yield_result.get('year', 'N/A')
            y_level_key = yield_classification.get('level', 'MEDIUM')
            y_level = config.YIELD_LEVELS.get(y_level_key, y_level_key)

            lines.append(_line(f"Area:          {y_area}"))
            lines.append(_line(f"Crop:          {y_crop}"))
            lines.append(_line(f"Year:          {y_year}"))
            lines.append(_line(f"Predicted:     {y_val:,.2f}"))
            lines.append(_line(f"Yield Level:   {y_level}"))
            if yield_classification.get('percentile'):
                lines.append(_line(
                    f"Position:      {yield_classification['percentile']}"))
        else:
            error = yield_result.get('error', 'Not available')
            lines.append(_line(f"❌ {error}"))
            suggestions = yield_result.get('suggestions', [])
            if suggestions:
                lines.append(_line("Did you mean:"))
                for s in suggestions[:5]:
                    lines.append(_line(f"  → {s}"))

        # ══════════════════════════════════════════════════════
        # SECTION 4: RISK ANALYSIS
        # ══════════════════════════════════════════════════════
        lines.append(_sep())
        lines.append(_header("⚠   RISK ANALYSIS"))
        lines.append(_sep())

        # Disease Risk
        d_risk_key = disease_risk.get('risk_level', 'MODERATE')
        d_risk = config.RISK_LEVELS.get(d_risk_key, d_risk_key)
        d_score = disease_risk.get('risk_score', 0)
        lines.append(_line(f"Disease Risk:    {d_risk} (score: {d_score}/100)"))
        desc = disease_risk.get('description', '')
        if desc:
            # Wrap long descriptions
            while len(desc) > W - 4:
                split_pos = desc[:W-4].rfind(' ')
                if split_pos == -1:
                    split_pos = W - 4
                lines.append(_line(f"  {desc[:split_pos]}"))
                desc = desc[split_pos:].strip()
            if desc:
                lines.append(_line(f"  {desc}"))

        # Yield Level
        lines.append(_line())
        y_level_key2 = yield_classification.get('level', 'MEDIUM')
        y_level2 = config.YIELD_LEVELS.get(y_level_key2, y_level_key2)
        lines.append(_line(f"Yield Level:     {y_level2}"))

        # Soil Quality
        lines.append(_line())
        sq_key = soil_quality.get('level', 'FAIR')
        sq_display = config.SOIL_QUALITY_LEVELS.get(sq_key, sq_key)
        sq_score = soil_quality.get('score', 0)
        lines.append(_line(
            f"Soil Quality:    {sq_display}    Score: {sq_score:.0f}/100"))

        # Score breakdown with progress bars
        breakdown = soil_quality.get('breakdown', {})
        if breakdown:
            lines.append(_line())
            lines.append(_line("Soil Score Breakdown:"))
            for factor, value in breakdown.items():
                if isinstance(value, tuple):
                    actual, maximum = value
                else:
                    actual, maximum = value, 25
                pct = (actual / maximum * 100) if maximum > 0 else 0
                bar_len = int(pct / 100 * 18)
                bar = "█" * bar_len + "░" * (18 - bar_len)
                lines.append(_line(
                    f"  {factor:<14} {actual:5.1f}/{maximum:<3}  "
                    f"{bar}  {pct:.0f}%"))

        # NPK Ratio info
        npk_info = soil_quality.get('npk_ratio', {})
        if npk_info:
            lines.append(_line())
            lines.append(_line("NPK Balance:"))
            for key, val in npk_info.items():
                if key != 'note':
                    lines.append(_line(f"  {key}: {val}"))
            if 'note' in npk_info:
                lines.append(_line(f"  Note: {npk_info['note']}"))

        # Soil issues
        issues = soil_quality.get('issues', [])
        if issues:
            lines.append(_line())
            lines.append(_line("Identified Issues:"))
            for issue in issues:
                # Wrap long issues
                if len(issue) > W - 6:
                    lines.append(_line(f"  ⚠ {issue[:W-6]}"))
                    lines.append(_line(f"    {issue[W-6:]}"))
                else:
                    lines.append(_line(f"  ⚠ {issue}"))

        # ══════════════════════════════════════════════════════
        # SECTION 5: OVERALL FARM HEALTH
        # ══════════════════════════════════════════════════════
        if overall_health:
            lines.append(_sep())
            lines.append(_header("🏥  OVERALL FARM HEALTH"))
            lines.append(_sep())

            grade = overall_health.get('overall_grade', '?')
            score = overall_health.get('overall_score', 0)
            summary = overall_health.get('summary', '')

            # Large grade display
            lines.append(_line())
            lines.append(_line(
                f"   Grade:  [ {grade} ]    Score: {score:.0f}/100"))
            lines.append(_line(f"   {summary}"))

            # Component scores
            components = overall_health.get('components', {})
            if components:
                lines.append(_line())
                lines.append(_line("Health Components:"))
                for comp, comp_score in components.items():
                    bar_len = int(comp_score / 100 * 20)
                    bar = "█" * bar_len + "░" * (20 - bar_len)
                    lines.append(_line(
                        f"  {comp:<17} {comp_score:5.1f}/100  {bar}"))

        # ══════════════════════════════════════════════════════
        # SECTION 6: RECOMMENDATIONS
        # ══════════════════════════════════════════════════════
        lines.append(_sep())
        lines.append(_header("💡  SMART RECOMMENDATIONS"))
        lines.append(_sep())

        # Cross-module advisory (new in v2.0)
        if combined_advisory:
            lines.append(_line())
            lines.append(_line("🧠 INTELLIGENT ADVISORY (Cross-Module):"))
            for adv in combined_advisory:
                # Wrap long lines
                while len(adv) > W - 6:
                    split_pos = adv[:W-6].rfind(' ')
                    if split_pos == -1:
                        split_pos = W - 6
                    lines.append(_line(f"  {adv[:split_pos]}"))
                    adv = adv[split_pos:].strip()
                if adv:
                    lines.append(_line(f"  {adv}"))
                lines.append(_line())

        # Disease Treatment
        lines.append(_line("🔬 Disease Treatment:"))
        for rec in disease_treatments[:6]:
            if len(rec) > W - 6:
                lines.append(_line(f"  • {rec[:W-6]}"))
                lines.append(_line(f"    {rec[W-6:]}"))
            else:
                lines.append(_line(f"  • {rec}"))

        # Crop Advice
        lines.append(_line())
        lines.append(_line("🌱 Crop Advice:"))
        for rec in crop_advice[:7]:
            if len(rec) > W - 6:
                lines.append(_line(f"  • {rec[:W-6]}"))
                lines.append(_line(f"    {rec[W-6:]}"))
            else:
                lines.append(_line(f"  • {rec}"))

        # Yield Advice
        lines.append(_line())
        lines.append(_line("📊 Yield Advice:"))
        for rec in yield_advice[:6]:
            if len(rec) > W - 6:
                lines.append(_line(f"  • {rec[:W-6]}"))
                lines.append(_line(f"    {rec[W-6:]}"))
            else:
                lines.append(_line(f"  • {rec}"))

        # ══════════════════════════════════════════════════════
        # FOOTER
        # ══════════════════════════════════════════════════════
        lines.append(_line())
        lines.append("╠═" + "═" * W + "═╣")
        lines.append("║ " + config.SYSTEM_NAME.center(W) + " ║")
        lines.append("║ " + (
            f"v{config.SYSTEM_VERSION} — Powered by "
            f"Deep Learning & Machine Learning").center(W) + " ║")
        lines.append("╚═" + "═" * W + "═╝")
        lines.append("")

        return "\n".join(lines)

    @staticmethod
    def save_to_file(
        report: str,
        filepath: Optional[str] = None
    ) -> str:
        """
        Save the report to a text file.

        Parameters
        ----------
        report : str
            Report content string.
        filepath : str, optional
            Output path. Defaults to ``reports/smart_farm_report_<ts>.txt``

        Returns
        -------
        str
            Path to the saved report file.
        """
        if filepath is None:
            os.makedirs(config.REPORT_DIR, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(
                config.REPORT_DIR,
                f"smart_farm_report_{timestamp}.txt"
            )

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)

        return filepath
