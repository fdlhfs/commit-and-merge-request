import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Hasil validasi title"""
    is_valid: bool
    errors: List[str]
    suggestions: List[str]
    parsed_data: Optional[Dict[str, str]] = None


@dataclass
class ReferenceData:
    """Data referensi yang diekstrak"""
    ticket_link: Optional[Dict[str, str]] = None
    documentation_link: Optional[Dict[str, str]] = None
    testing_link: Optional[Dict[str, str]] = None


class CommitTitleValidator:
    """Validator untuk commit title sesuai standar perusahaan"""
    
    ALLOWED_TYPES = [
        'feat', 'fix', 'refactor', 'docs', 'style', 
        'test', 'chore', 'perf', 'ci', 'build', 'revert'
    ]
    
    # Pattern: <tipe>: <ringkasan singkat> (Taiga #<NamaProject>-<Nomor Ticket>)
    TITLE_PATTERN = r'^([a-z]+):\s+(.+?)\s+\(Taiga\s+#([A-Z]+)-(\d+)\)$'
    
    def validate_title(self, title: str) -> ValidationResult:
        """
        Validasi commit/merge request title
        
        Args:
            title: Title yang akan divalidasi
            
        Returns:
            ValidationResult dengan status validasi dan saran perbaikan
        """
        errors = []
        suggestions = []
        parsed_data = None
        
        if not title or not title.strip():
            errors.append("Title tidak boleh kosong")
            suggestions.append("Format yang benar: <tipe>: <ringkasan singkat> (Taiga #<NamaProject>-<NomorTicket>)")
            return ValidationResult(False, errors, suggestions)
        
        title = title.strip()
        
        # Cek format dasar dengan regex
        match = re.match(self.TITLE_PATTERN, title)
        
        if not match:
            errors.extend(self._analyze_format_errors(title))
            suggestions.extend(self._generate_suggestions(title))
            return ValidationResult(False, errors, suggestions)
        
        # Ekstrak komponen
        tipe, ringkasan, project_name, ticket_number = match.groups()
        
        # Validasi tipe
        if tipe not in self.ALLOWED_TYPES:
            errors.append(f"Tipe '{tipe}' tidak valid")
            closest_type = self._find_closest_type(tipe)
            if closest_type:
                suggestions.append(f"Mungkin maksud Anda: '{closest_type}'?")
            suggestions.append(f"Tipe yang diperbolehkan: {', '.join(self.ALLOWED_TYPES)}")
        
        # Validasi ringkasan
        if len(ringkasan.strip()) < 5:
            errors.append("Ringkasan terlalu pendek (minimal 5 karakter)")
            suggestions.append("Berikan deskripsi yang lebih jelas tentang perubahan yang dilakukan")
        
        # Validasi project name (harus uppercase/huruf besar)
        if not project_name.isupper():
            errors.append(f"Nama project harus huruf besar (uppercase): '{project_name}' tidak valid")
            suggestions.append(f"Gunakan: (Taiga #{project_name.upper()}-{ticket_number})")

        # Jika ada error, tidak valid
        if errors:
            return ValidationResult(False, errors, suggestions)
        
        # Semua validasi lolos
        parsed_data = {
            'type': tipe,
            'summary': ringkasan.strip(),
            'project': project_name,
            'ticket_number': ticket_number
        }
        
        return ValidationResult(True, [], [], parsed_data)
    
    def _analyze_format_errors(self, title: str) -> List[str]:
        """Analisa kesalahan format pada title"""
        errors = []
        
        # Cek apakah ada tipe
        if ':' not in title:
            errors.append("Format salah: Tidak ditemukan tanda ':' setelah tipe")
            errors.append("Format yang benar: <tipe>: <ringkasan singkat> (Taiga #<NamaProject>-<NomorTicket>)")
            return errors
        
        parts = title.split(':', 1)
        potential_type = parts[0].strip().lower()
        
        # Validasi tipe
        if not potential_type:
            errors.append("Tipe commit tidak ditemukan sebelum tanda ':'")
        elif potential_type not in self.ALLOWED_TYPES:
            errors.append(f"Tipe '{potential_type}' tidak valid")
            errors.append(f"Tipe yang diperbolehkan: {', '.join(self.ALLOWED_TYPES)}")
        elif potential_type != parts[0].strip():
            errors.append("Tipe harus menggunakan huruf kecil")
        
        # Cek apakah ada referensi Taiga
        if 'Taiga' not in title and 'taiga' not in title.lower():
            errors.append("Referensi Taiga tidak ditemukan")
            errors.append("Tambahkan: (Taiga #<NamaProject>-<NomorTicket>)")
        elif not re.search(r'\(Taiga\s+#[A-Z]+-\d+\)', title):
            if '(' not in title or ')' not in title:
                errors.append("Format referensi Taiga salah: kurung buka/tutup tidak lengkap")
            elif '#' not in title:
                errors.append("Format referensi Taiga salah: simbol '#' tidak ditemukan")
            elif not re.search(r'#[A-Z]+-\d+', title):
                errors.append("Format referensi Taiga salah: format harus #<NamaProject>-<NomorTicket>")
                errors.append("Contoh: (Taiga #DATB-10353)")
            else:
                errors.append("Format referensi Taiga tidak sesuai standar")
        
        # Cek spasi setelah tipe
        if len(parts) > 1 and parts[1] and parts[1][0] != ' ':
            errors.append("Harus ada spasi setelah tanda ':'")
        
        return errors
    
    def _generate_suggestions(self, title: str) -> List[str]:
        """Generate saran perbaikan otomatis"""
        suggestions = []
        
        # Coba perbaiki format
        # Ekstrak komponen yang mungkin ada
        type_match = re.match(r'^([a-z]+)', title.lower())
        taiga_match = re.search(r'#?([A-Z]+)-?(\d+)', title)
        
        if type_match and taiga_match:
            tipe = type_match.group(1)
            if tipe not in self.ALLOWED_TYPES:
                tipe = self._find_closest_type(tipe) or 'feat'
            
            project = taiga_match.group(1)
            ticket = taiga_match.group(2)
            
            # Ekstrak ringkasan (ambil bagian tengah)
            summary = re.sub(r'^[a-z]+:?\s*', '', title, flags=re.IGNORECASE)
            summary = re.sub(r'\(.*?\)$', '', summary).strip()
            summary = re.sub(r'#?[A-Z]+-?\d+', '', summary).strip()
            
            if not summary:
                summary = "tambahkan deskripsi perubahan"
            
            suggested_title = f"{tipe}: {summary} (Taiga #{project}-{ticket})"
            suggestions.append(f"Saran perbaikan: {suggested_title}")
        else:
            suggestions.append("Contoh format yang benar:")
            suggestions.append("feat: menambahkan fitur login user (Taiga #DATB-10353)")
            suggestions.append("fix: memperbaiki bug pada dashboard (Taiga #PROJ-123)")
        
        return suggestions
    
    def _find_closest_type(self, tipe: str) -> Optional[str]:
        """Cari tipe terdekat menggunakan similarity sederhana"""
        tipe = tipe.lower()
        
        # Exact match
        if tipe in self.ALLOWED_TYPES:
            return tipe
        
        # Cek prefix match
        for allowed in self.ALLOWED_TYPES:
            if allowed.startswith(tipe) or tipe.startswith(allowed):
                return allowed
        
        # Simple similarity (common typos)
        typo_map = {
            'feature': 'feat',
            'bugfix': 'fix',
            'bug': 'fix',
            'document': 'docs',
            'testing': 'test',
            'tests': 'test',
            'performance': 'perf',
        }
        
        return typo_map.get(tipe)


class ReferenceExtractor:
    """Ekstraksi data referensi dari deskripsi"""
    
    def extract_references(self, description: str) -> ReferenceData:
        """
        Ekstrak referensi link dari deskripsi
        
        Args:
            description: Deskripsi yang berisi referensi
            
        Returns:
            ReferenceData dengan link yang diekstrak
        """
        if not description:
            return ReferenceData()
        
        ticket_link = self._extract_ticket_link(description)
        doc_link = self._extract_documentation_link(description)
        test_link = self._extract_testing_link(description)
        
        return ReferenceData(
            ticket_link=ticket_link,
            documentation_link=doc_link,
            testing_link=test_link
        )
    
    def _extract_ticket_link(self, text: str) -> Optional[Dict[str, str]]:
        """Ekstrak Ticket Link"""
        # Pattern: Ticket Link: [(Taiga #<Project>-<Number>)] (https://...)
        pattern = r'Ticket\s+Link:\s*\[\(Taiga\s+#([A-Z]+)-(\d+)\)\]\s*\((https?://[^\)]+)\)'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            return {
                'project': match.group(1),
                'ticket_number': match.group(2),
                'url': match.group(3),
                'display': f"Taiga #{match.group(1)}-{match.group(2)}"
            }
        return None
    
    def _extract_documentation_link(self, text: str) -> Optional[Dict[str, str]]:
        """Ekstrak Documentation Link"""
        # Pattern: Documentation Link: [<name>] (https://...)
        pattern = r'Documentation\s+Link:\s*\[([^\]]+)\]\s*\(([^\)]+)\)'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            return {
                'name': match.group(1),
                'url': match.group(2)
            }
        return None
    
    def _extract_testing_link(self, text: str) -> Optional[Dict[str, str]]:
        """Ekstrak Testing Link"""
        # Pattern: Testing Link: [<name>] (https://...) atau [...link]
        pattern = r'Testing\s+Link:\s*\[([^\]]+)\](?:\s*\(([^\)]+)\))?'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            name = match.group(1)
            url = match.group(2) if match.group(2) else name
            return {
                'name': name,
                'url': url
            }
        return None


# Convenience functions
def validate_commit_title(title: str) -> ValidationResult:
    """Function wrapper untuk validasi title"""
    validator = CommitTitleValidator()
    return validator.validate_title(title)


def extract_reference_data(description: str) -> ReferenceData:
    """Function wrapper untuk ekstraksi referensi"""
    extractor = ReferenceExtractor()
    return extractor.extract_references(description)