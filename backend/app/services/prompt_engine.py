"""Prompt Engine: Menyusun dan memformat template prompt untuk LLM AI."""
from typing import Dict, Optional


class PromptEngine:
    @staticmethod
    def build_lab_generation_prompt(
        teacher_prompt: str,
        material_title: Optional[str] = None,
        material_content: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Menyusun instruksi system dan user prompt agar LLM menghasilkan konfigurasi JSON virtual lab.
        """
        system_instruction = (
            "Anda adalah KimiFun AI, asisten spesialis kurikulum kimia dan perancang simulasi laboratorium virtual. "
            "Tugas Anda adalah membaca permintaan guru kimia dan menghasilkan konfigurasi parameter simulasi eksperimen "
            "dalam format JSON murni TANPA markdown triple backtick (```json). "
            "Struktur JSON WAJIB memiliki keys berikut:\n"
            "{\n"
            '  "lab_title": "Judul Eksperimen (string)",\n'
            '  "lab_type": "titration" ATAU "stoichiometry" ATAU "reaction",\n'
            '  "solution_name": "Nama Larutan/Analit (string, sertakan rumus kimia)",\n'
            '  "solution_molarity": 0.1 (float, konsentrasi),\n'
            '  "titrant_name": "Nama Titran/Reaktan Kedua (string)",\n'
            '  "titrant_molarity": 0.1 (float),\n'
            '  "indicator_type": "Nama Indikator (string, cth: Phenolphthalein / Metil Merah / Tanpa Indikator)",\n'
            '  "color_start": "#HEXCOLOR (warna awal larutan)",\n'
            '  "color_end": "#HEXCOLOR (warna setelah bereaksi/titik akhir)",\n'
            '  "max_volume_ml": 50 (integer),\n'
            '  "instructions": "Petunjuk praktikum ringkas untuk siswa (string)"\n'
            "}"
        )

        user_content = f"Permintaan Guru: {teacher_prompt}\n"
        if material_title:
            user_content += f"Topik Materi Terkait: {material_title}\n"
        if material_content:
            user_content += f"Rangkuman Teori Materi:\n{material_content[:500]}\n"

        return {
            "system_instruction": system_instruction,
            "user_prompt": user_content,
        }

    @staticmethod
    def build_material_generation_prompt(
        topic: str,
        module_title: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Menyusun prompt untuk auto-generate materi pembelajaran kimia terstruktur.
        """
        system_instruction = (
            "Anda adalah KimiFun AI, spesialis kurikulum kimia interaktif SMA/dasar perguruan tinggi. "
            "Tugas Anda membuat teks materi pembelajaran kimia yang jelas, sistematis, dan terstruktur "
            "dalam format JSON murni TANPA markdown triple backtick (```json). "
            "Format JSON:\n"
            "{\n"
            '  "title": "Judul Sub-Materi yang Menarik (string)",\n'
            '  "content_html": "<p>Penjelasan konsep utama...</p><h4>1. Konsep & Rumus</h4><p>Penjelasan rumus...</p><h4>2. Contoh Reaksi</h4><p>Reaksi kimia...</p><h4>3. Aplikasi Nyata</h4><p>Penerapan di kehidupan/industri...</p>"\n'
            "}"
        )
        user_prompt = f"Topik Materi: {topic}\n"
        if module_title:
            user_prompt += f"Modul Pembelajaran Induk: {module_title}\n"
        user_prompt += "Buatkan materi penjelasan kimia lengkap dengan penjelasan konsep, reaksi, rumus jika ada, dan contoh."

        return {
            "system_instruction": system_instruction,
            "user_prompt": user_prompt,
        }

    @staticmethod
    def build_quiz_generation_prompt(
        topic: str,
        num_questions: int = 3,
    ) -> Dict[str, str]:
        """
        Menyusun prompt untuk auto-generate soal kuis kimia terstruktur.
        """
        system_instruction = (
            "Anda adalah AI perancang asesmen kuis kimia KimiFun. "
            "Hasilkan soal kuis pilihan ganda terstruktur dalam format JSON murni TANPA markdown backticks. "
            "Format JSON:\n"
            "{\n"
            '  "title": "Judul Kuis",\n'
            '  "time_limit_minutes": 15,\n'
            '  "questions": [\n'
            "    {\n"
            '      "metric_name": "Kategori Konsep (cth: Stoikiometri / Konsep Mol)",\n'
            '      "question_text": "Pertanyaan soal...",\n'
            '      "options": ["Pilihan A", "Pilihan B", "Pilihan C", "Pilihan D"],\n'
            '      "correct_answer": "A",\n'
            '      "weight_score": 10\n'
            "    }\n"
            "  ]\n"
            "}"
        )
        user_prompt = f"Buatkan {num_questions} soal kuis kimia pilihan ganda dengan topik: {topic}."
        return {
            "system_instruction": system_instruction,
            "user_prompt": user_prompt,
        }

    @staticmethod
    def build_tutor_prompt(student_question: str) -> Dict[str, str]:
        """
        Prompt untuk Kimi AI Tutor yang membimbing siswa secara ramah dan saintifik.
        """
        system_instruction = (
            "Anda adalah Kimi, asisten tutor kimia virtual platform KimiFun. "
            "Jawab pertanyaan siswa seputar kimia dengan jelas, ramah, dan mendidik. "
            "Jangan langsung memberikan jawaban akhir jika berbentuk hitungan; berikan rumus dasar dan pandu langkah demi langkah."
        )
        return {
            "system_instruction": system_instruction,
            "user_prompt": student_question,
        }
