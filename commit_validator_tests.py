import unittest
from commit_validator import (
    CommitTitleValidator, 
    ReferenceExtractor,
    validate_commit_title,
    extract_reference_data,
    ValidationResult,
    ReferenceData
)


class TestCommitTitleValidator(unittest.TestCase):
    """Test untuk validasi commit title"""
    
    def setUp(self):
        self.validator = CommitTitleValidator()
    
    def test_valid_title_feat(self):
        """Test title valid dengan tipe feat"""
        title = "feat: menambahkan fitur login user (Taiga #DATB-10353)"
        result = self.validator.validate_title(title)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        self.assertIsNotNone(result.parsed_data)
        self.assertEqual(result.parsed_data['type'], 'feat')
        self.assertEqual(result.parsed_data['project'], 'DATB')
        self.assertEqual(result.parsed_data['ticket_number'], '10353')
    
    def test_valid_title_fix(self):
        """Test title valid dengan tipe fix"""
        title = "fix: memperbaiki bug pada dashboard analytics (Taiga #PROJ-123)"
        result = self.validator.validate_title(title)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.parsed_data['type'], 'fix')
        self.assertEqual(result.parsed_data['summary'], 'memperbaiki bug pada dashboard analytics')
    
    def test_valid_title_refactor(self):
        """Test title valid dengan tipe refactor"""
        title = "refactor: restructure authentication module (Taiga #AUTH-456)"
        result = self.validator.validate_title(title)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.parsed_data['type'], 'refactor')
    
    def test_invalid_empty_title(self):
        """Test title kosong"""
        result = self.validator.validate_title("")
        
        self.assertFalse(result.is_valid)
        self.assertIn("tidak boleh kosong", result.errors[0].lower())
        self.assertGreater(len(result.suggestions), 0)
    
    def test_invalid_type(self):
        """Test tipe yang tidak valid"""
        title = "feature: menambahkan login (Taiga #DATB-10353)"
        result = self.validator.validate_title(title)
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any("tidak valid" in err for err in result.errors))
        # Harus ada saran perbaikan
        self.assertGreater(len(result.suggestions), 0)
    
    def test_invalid_no_colon(self):
        """Test title tanpa tanda titik dua"""
        title = "feat menambahkan fitur login (Taiga #DATB-10353)"
        result = self.validator.validate_title(title)
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any(":" in err for err in result.errors))
    
    def test_invalid_no_taiga_reference(self):
        """Test title tanpa referensi Taiga"""
        title = "feat: menambahkan fitur login"
        result = self.validator.validate_title(title)
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any("taiga" in err.lower() for err in result.errors))
    
    def test_invalid_taiga_format(self):
        """Test format Taiga yang salah"""
        title = "feat: menambahkan login (Taiga DATB-10353)"  # Missing #
        result = self.validator.validate_title(title)
        
        self.assertFalse(result.is_valid)
    
    def test_invalid_project_lowercase(self):
        """Test nama project dengan huruf kecil"""
        title = "feat: menambahkan login (Taiga #datb-10353)"
        result = self.validator.validate_title(title)
        
        self.assertFalse(result.is_valid)
        # Cek apakah ada error tentang project name
        self.assertTrue(any("project" in err.lower() for err in result.errors))
        # Atau cek apakah ada suggestion untuk uppercase
        self.assertTrue(any("#DATB" in sug for sug in result.suggestions))
        
    def test_invalid_summary_too_short(self):
        """Test ringkasan yang terlalu pendek"""
        title = "feat: add (Taiga #DATB-10353)"
        result = self.validator.validate_title(title)
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any("terlalu pendek" in err.lower() for err in result.errors))
    
    def test_invalid_no_space_after_colon(self):
        """Test tanpa spasi setelah titik dua"""
        title = "feat:menambahkan login (Taiga #DATB-10353)"
        result = self.validator.validate_title(title)
        
        self.assertFalse(result.is_valid)
    
    def test_suggestion_for_typo_type(self):
        """Test saran untuk typo pada tipe"""
        title = "bug: fix login issue (Taiga #DATB-10353)"
        result = self.validator.validate_title(title)
        
        self.assertFalse(result.is_valid)
        # Harus ada saran untuk menggunakan 'fix'
        self.assertGreater(len(result.suggestions), 0)
    
    def test_all_allowed_types(self):
        """Test semua tipe yang diperbolehkan"""
        allowed_types = ['feat', 'fix', 'refactor', 'docs', 'style', 
                        'test', 'chore', 'perf', 'ci', 'build', 'revert']
        
        for tipe in allowed_types:
            title = f"{tipe}: testing allowed type (Taiga #TEST-001)"
            result = self.validator.validate_title(title)
            self.assertTrue(result.is_valid, f"Type '{tipe}' should be valid")
    
    def test_whitespace_handling(self):
        """Test handling whitespace di awal/akhir"""
        title = "  feat: menambahkan login (Taiga #DATB-10353)  "
        result = self.validator.validate_title(title)
        
        self.assertTrue(result.is_valid)
    
    def test_complex_summary(self):
        """Test ringkasan yang kompleks dengan karakter khusus"""
        title = "feat: menambahkan API endpoint untuk user's profile & settings (Taiga #API-789)"
        result = self.validator.validate_title(title)
        
        self.assertTrue(result.is_valid)
    
    def test_wrapper_function(self):
        """Test convenience wrapper function"""
        title = "feat: test wrapper function (Taiga #TEST-999)"
        result = validate_commit_title(title)
        
        self.assertIsInstance(result, ValidationResult)
        self.assertTrue(result.is_valid)


class TestReferenceExtractor(unittest.TestCase):
    """Test untuk ekstraksi referensi"""
    
    def setUp(self):
        self.extractor = ReferenceExtractor()
    
    def test_extract_ticket_link(self):
        """Test ekstraksi ticket link"""
        description = """
        Ticket Link: [(Taiga #DATB-10353)] (https://projects.digitaltelkom.id/project/DATB/us/10353)
        """
        result = self.extractor.extract_references(description)
        
        self.assertIsNotNone(result.ticket_link)
        self.assertEqual(result.ticket_link['project'], 'DATB')
        self.assertEqual(result.ticket_link['ticket_number'], '10353')
        self.assertEqual(result.ticket_link['url'], 
                        'https://projects.digitaltelkom.id/project/DATB/us/10353')
        self.assertEqual(result.ticket_link['display'], 'Taiga #DATB-10353')
    
    def test_extract_documentation_link(self):
        """Test ekstraksi documentation link"""
        description = """
        Documentation Link: [Figma] (https://www.figma.com/design/abc123)
        """
        result = self.extractor.extract_references(description)
        
        self.assertIsNotNone(result.documentation_link)
        self.assertEqual(result.documentation_link['name'], 'Figma')
        self.assertEqual(result.documentation_link['url'], 
                        'https://www.figma.com/design/abc123')
    
    def test_extract_testing_link(self):
        """Test ekstraksi testing link"""
        description = """
        Testing Link: [test scenario link] (https://docs.google.com/test123)
        """
        result = self.extractor.extract_references(description)
        
        self.assertIsNotNone(result.testing_link)
        self.assertEqual(result.testing_link['name'], 'test scenario link')
        self.assertEqual(result.testing_link['url'], 
                        'https://docs.google.com/test123')
    
    def test_extract_all_references(self):
        """Test ekstraksi semua referensi sekaligus"""
        description = """
        Ticket Link: [(Taiga #DATB-10353)] (https://projects.digitaltelkom.id/project/DATB/us/10353)
        Documentation Link: [Figma] (https://www.figma.com/design/abc123)
        Testing Link: [test scenario link] (https://docs.google.com/test123)
        """
        result = self.extractor.extract_references(description)
        
        self.assertIsNotNone(result.ticket_link)
        self.assertIsNotNone(result.documentation_link)
        self.assertIsNotNone(result.testing_link)
    
    def test_empty_description(self):
        """Test dengan deskripsi kosong"""
        result = self.extractor.extract_references("")
        
        self.assertIsNone(result.ticket_link)
        self.assertIsNone(result.documentation_link)
        self.assertIsNone(result.testing_link)
    
    def test_none_description(self):
        """Test dengan deskripsi None"""
        result = self.extractor.extract_references(None)
        
        self.assertIsNone(result.ticket_link)
    
    def test_partial_references(self):
        """Test dengan hanya sebagian referensi"""
        description = """
        Ticket Link: [(Taiga #PROJ-456)] (https://example.com/ticket/456)
        Some other text here
        """
        result = self.extractor.extract_references(description)
        
        self.assertIsNotNone(result.ticket_link)
        self.assertIsNone(result.documentation_link)
        self.assertIsNone(result.testing_link)
    
    def test_case_insensitive_extraction(self):
        """Test ekstraksi case insensitive"""
        description = """
        ticket link: [(Taiga #TEST-111)] (https://test.com)
        DOCUMENTATION LINK: [Docs] (https://docs.com)
        Testing LINK: [Tests] (https://tests.com)
        """
        result = self.extractor.extract_references(description)
        
        self.assertIsNotNone(result.ticket_link)
        self.assertIsNotNone(result.documentation_link)
        self.assertIsNotNone(result.testing_link)
    
    def test_testing_link_without_parentheses(self):
        """Test testing link tanpa kurung"""
        description = """
        Testing Link: [https://docs.google.com/test123]
        """
        result = self.extractor.extract_references(description)
        
        self.assertIsNotNone(result.testing_link)
        self.assertEqual(result.testing_link['url'], 
                        'https://docs.google.com/test123')
    
    def test_multiple_tickets_extract_first(self):
        """Test dengan multiple ticket, harus ekstrak yang pertama"""
        description = """
        Ticket Link: [(Taiga #FIRST-001)] (https://first.com)
        Ticket Link: [(Taiga #SECOND-002)] (https://second.com)
        """
        result = self.extractor.extract_references(description)
        
        self.assertEqual(result.ticket_link['project'], 'FIRST')
    
    def test_wrapper_function(self):
        """Test convenience wrapper function"""
        description = "Ticket Link: [(Taiga #TEST-999)] (https://test.com)"
        result = extract_reference_data(description)
        
        self.assertIsInstance(result, ReferenceData)
        self.assertIsNotNone(result.ticket_link)


class TestIntegration(unittest.TestCase):
    """Integration test untuk scenario lengkap"""
    
    def test_complete_workflow(self):
        """Test workflow lengkap: validasi title + ekstrak referensi"""
        title = "feat: implementasi user authentication (Taiga #AUTH-555)"
        description = """
        Implementasi sistem autentikasi user dengan JWT token
        
        Ticket Link: [(Taiga #AUTH-555)] (https://projects.digitaltelkom.id/project/AUTH/us/555)
        Documentation Link: [Figma Design] (https://www.figma.com/auth-design)
        Testing Link: [Test Cases] (https://docs.google.com/spreadsheets/test-auth)
        """
        
        # Validasi title
        title_result = validate_commit_title(title)
        self.assertTrue(title_result.is_valid)
        self.assertEqual(title_result.parsed_data['type'], 'feat')
        self.assertEqual(title_result.parsed_data['project'], 'AUTH')
        
        # Ekstrak referensi
        ref_result = extract_reference_data(description)
        self.assertIsNotNone(ref_result.ticket_link)
        self.assertEqual(ref_result.ticket_link['project'], 'AUTH')
        self.assertIsNotNone(ref_result.documentation_link)
        self.assertIsNotNone(ref_result.testing_link)
    
    def test_invalid_title_with_valid_references(self):
        """Test title invalid tapi referensi valid"""
        title = "add user auth (Taiga #AUTH-555)"  # Format salah
        description = "Ticket Link: [(Taiga #AUTH-555)] (https://test.com)"
        
        title_result = validate_commit_title(title)
        self.assertFalse(title_result.is_valid)
        self.assertGreater(len(title_result.errors), 0)
        
        ref_result = extract_reference_data(description)
        self.assertIsNotNone(ref_result.ticket_link)


def run_tests():
    """Function untuk menjalankan semua test"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestCommitTitleValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestReferenceExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests dengan verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result


if __name__ == '__main__':
    run_tests()