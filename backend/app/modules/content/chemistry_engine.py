"""Service engine perhitungan dan verifikasi kimia untuk virtual lab."""
from typing import Any, Dict, Tuple


class ChemistryEngine:
    @staticmethod
    def verify_stoichiometry_inquiry(
        stage: int, user_answer: Any, inputs: Dict[str, Any]
    ) -> Tuple[bool, Any, str]:
        """
        Memvalidasi jawaban inquiry E-LKPD berdasarkan tahapan pembelajaran.
        Return: (is_correct, correct_value, explanation)
        """
        try:
            if stage == 1:
                # Konsep Mol: n = m / Ar (Fe: Ar = 56)
                mass = float(inputs.get("mass", 56))
                ar = float(inputs.get("ar", 56))
                expected = round(mass / ar, 3)
                ans = float(user_answer)
                is_correct = abs(ans - expected) < 0.05
                explanation = (
                    f"Benar! Mol (n) = Massa / Ar = {mass} / {ar} = {expected} mol."
                    if is_correct
                    else f"Kurang tepat. Perhitungan benar: {mass} / {ar} = {expected} mol."
                )
                return is_correct, expected, explanation

            elif stage == 2:
                # Hukum Lavoisier: Wadah Terbuka vs Tertutup
                ans_str = str(user_answer).lower().strip()
                # Pada wadah terbuka, gas CO2 keluar sehingga massa tampak tidak kekal
                is_correct = ans_str in ["false", "tidak terbukti", "tidak"]
                expected = "false"
                explanation = (
                    "Tepat! Pada wadah terbuka, gas CO₂ lepas ke udara sehingga massa terukur berkurang. "
                    "Hukum Lavoisier berlaku pada sistem tertutup."
                    if is_correct
                    else "Pilihan keliru. Gas CO₂ yang lepas ke atmosfer menyebabkan penurunan massa terukur."
                )
                return is_correct, expected, explanation

            elif stage == 3:
                # Penyetaraan Reaksi: aN2 + bH2 -> cNH3 (1, 3, 2)
                # user_answer bisa berupa string "1,3,2" atau dict {a: 1, b: 3, c: 2}
                if isinstance(user_answer, dict):
                    a = int(user_answer.get("a", 0))
                    b = int(user_answer.get("b", 0))
                    c = int(user_answer.get("c", 0))
                else:
                    parts = [int(p.strip()) for p in str(user_answer).split(",") if p.strip()]
                    a, b, c = (parts[0], parts[1], parts[2]) if len(parts) >= 3 else (0, 0, 0)

                is_correct = (a == 1 and b == 3 and c == 2)
                expected = {"a": 1, "b": 3, "c": 2}
                explanation = (
                    "REAKSI SETARA! 1 N₂ + 3 H₂ → 2 NH₃ (2 atom N dan 6 atom H di kedua ruas)."
                    if is_correct
                    else "Belum setara. Koefisien setara terbulat adalah a=1, b=3, c=2."
                )
                return is_correct, expected, explanation

            elif stage == 4:
                # Pereaksi Pembatas 2H2 + O2 -> 2H2O
                h2 = float(inputs.get("h2", 4))
                o2 = float(inputs.get("o2", 2))

                ratio_h2 = h2 / 2.0
                ratio_o2 = o2 / 1.0
                ans_str = str(user_answer).strip().lower()

                if abs(ratio_h2 - ratio_o2) < 1e-6:
                    limiting = "Keduanya habis (ekuivalen)"
                    is_correct = any(term in ans_str for term in ["habis", "ekuivalen", "tidak ada", "setara", "keduanya"])
                    expected = limiting
                    explanation = (
                        f"Tepat! Rasio mol/koefisien kedua pereaksi sama (H₂: {h2}/2 = {ratio_h2}, O₂: {o2}/1 = {ratio_o2}). "
                        "Kedua pereaksi habis bereaksi bersamaan (tidak ada pereaksi pembatas)."
                        if is_correct
                        else f"Belum tepat. Rasio mol/koefisien sama (H₂: {h2}/2 = {ratio_h2}, O₂: {o2}/1 = {ratio_o2}). "
                        "Maka kedua pereaksi habis bereaksi bersamaan tanpa pembatas."
                    )
                elif ratio_h2 < ratio_o2:
                    limiting = "Gas H₂"
                    is_correct = "h2" in ans_str
                    expected = limiting
                    explanation = (
                        f"Tepat! Pereaksi pembatas adalah {limiting} karena rasio mol terhadap koefisiennya paling kecil ({ratio_h2} < {ratio_o2})."
                        if is_correct
                        else f"Belum tepat. Bandingkan n/koefisien: H₂ ({h2}/2 = {ratio_h2}) vs O₂ ({o2}/1 = {ratio_o2}). Pembatasnya adalah {limiting}."
                    )
                else:
                    limiting = "Gas O₂"
                    is_correct = "o2" in ans_str
                    expected = limiting
                    explanation = (
                        f"Tepat! Pereaksi pembatas adalah {limiting} karena rasio mol terhadap koefisiennya paling kecil ({ratio_o2} < {ratio_h2})."
                        if is_correct
                        else f"Belum tepat. Bandingkan n/koefisien: H₂ ({h2}/2 = {ratio_h2}) vs O₂ ({o2}/1 = {ratio_o2}). Pembatasnya adalah {limiting}."
                    )
                return is_correct, expected, explanation

            elif stage == 5:
                # Stoikiometri Larutan: Pb(NO3)2 + 2KI -> PbI2 (s) + 2KNO3
                # Endapan: mol PbI2 = 0.5 * mol KI. Massa = mol * Mr(461)
                vol_ml = float(inputs.get("vol_ml", 20))
                molarity = float(inputs.get("molarity", 0.1))
                mr = float(inputs.get("mr", 461))

                mol_ki = (vol_ml / 1000.0) * molarity
                mol_pbi2 = mol_ki * 0.5
                expected_mass = round(mol_pbi2 * mr, 3)

                ans = float(user_answer)
                is_correct = abs(ans - expected_mass) < 0.05
                explanation = (
                    f"Benar! Mol KI = {mol_ki:.4f} mol, mol PbI₂ = {mol_pbi2:.4f} mol. "
                    f"Massa endapan PbI₂ = {expected_mass} gram."
                    if is_correct
                    else f"Belum tepat. Hasil perhitungan: (V/1000) × M × 0.5 × Mr = {expected_mass} gram."
                )
                return is_correct, expected_mass, explanation

            return False, None, "Tahap tidak valid"
        except Exception as e:
            return False, None, f"Kesalahan format input: {str(e)}"
