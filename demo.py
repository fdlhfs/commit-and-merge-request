from commit_validator import validate_commit_title, extract_reference_data


def print_separator(title=""):
    """Print separator untuk output yang lebih rapi"""
    print("\n" + "="*80)
    if title:
        print(f"  {title}")
        print("="*80)


def demo_valid_titles():
    """Demo validasi title yang benar"""
    print_separator("DEMO 1: VALIDASI TITLE YANG BENAR")
    
    valid_titles = [
        "feat: menambahkan fitur login user (Taiga #DATB-10353)",
        "fix: memperbaiki bug pada dashboard (Taiga #PROJ-123)",
        "refactor: restructure authentication module (Taiga #AUTH-456)",
        "docs: update API documentation (Taiga #DOC-789)",
    ]
    
    for title in valid_titles:
        print(f"\n📝 Title: {title}")
        result = validate_commit_title(title)
        
        if result.is_valid:
            print("✅ VALID")
            print(f"   Tipe: {result.parsed_data['type']}")
            print(f"   Ringkasan: {result.parsed_data['summary']}")
            print(f"   Project: {result.parsed_data['project']}")
            print(f"   Ticket: #{result.parsed_data['ticket_number']}")
        else:
            print("❌ INVALID")


def demo_invalid_titles():
    """Demo validasi title yang salah"""
    print_separator("DEMO 2: VALIDASI TITLE YANG SALAH + AUTO SUGGESTION")
    
    invalid_titles = [
        "add user login (Taiga #DATB-10353)",  # Missing colon
        "feature: add login (Taiga #DATB-10353)",  # Wrong type
        "feat: add (Taiga #DATB-10353)",  # Summary too short
        "feat menambahkan login",  # Missing Taiga reference
        "feat: menambahkan login (Taiga #datb-10353)",  # Lowercase project
        "bug: fix issue (Taiga #PROJ-123)",  # Wrong type (bug instead of fix)
    ]
    
    for title in invalid_titles:
        print(f"\n📝 Title: {title}")
        result = validate_commit_title(title)
        
        print("❌ INVALID")
        print("\n⚠️  Error:")
        for i, error in enumerate(result.errors, 1):
            print(f"   {i}. {error}")
        
        if result.suggestions:
            print("\n💡 Saran Perbaikan:")
            for i, suggestion in enumerate(result.suggestions, 1):
                print(f"   {i}. {suggestion}")


def demo_reference_extraction():
    """Demo ekstraksi referensi"""
    print_separator("DEMO 3: EKSTRAKSI REFERENSI DARI DESKRIPSI")
    
    descriptions = [
        {
            "name": "Complete References",
            "content": """
Implementasi fitur user authentication dengan JWT

Ticket Link: [(Taiga #DATB-10353)] (https://projects.digitaltelkom.id/project/DATB/us/10353)
Documentation Link: [Figma] (https://www.figma.com/design/abc123)
Testing Link: [test scenario link] (https://docs.google.com/spreadsheets/test)
            """
        },
        {
            "name": "Partial References",
            "content": """
Bug fix untuk dashboard analytics

Ticket Link: [(Taiga #PROJ-456)] (https://projects.digitaltelkom.id/project/PROJ/issue/456)
Documentation Link: [Confluence] (https://confluence.company.com/page/123)
            """
        },
        {
            "name": "Testing Link Without Parentheses",
            "content": """
Ticket Link: [(Taiga #TEST-789)] (https://test.com/789)
Testing Link: [https://docs.google.com/spreadsheets/test-scenarios]
            """
        }
    ]
    
    for desc in descriptions:
        print(f"\n📋 Scenario: {desc['name']}")
        print(f"   Description:\n{desc['content'][:100]}...")
        
        result = extract_reference_data(desc['content'])
        
        if result.ticket_link:
            print("\n   🎫 Ticket Link:")
            print(f"      Display: {result.ticket_link['display']}")
            print(f"      URL: {result.ticket_link['url']}")
        
        if result.documentation_link:
            print("\n   📄 Documentation Link:")
            print(f"      Name: {result.documentation_link['name']}")
            print(f"      URL: {result.documentation_link['url']}")
        
        if result.testing_link:
            print("\n   🧪 Testing Link:")
            print(f"      Name: {result.testing_link['name']}")
            print(f"      URL: {result.testing_link['url']}")
        
        if not any([result.ticket_link, result.documentation_link, result.testing_link]):
            print("   ⚠️  Tidak ada referensi yang ditemukan")


def demo_complete_workflow():
    """Demo workflow lengkap"""
    print_separator("DEMO 4: WORKFLOW LENGKAP - VALIDASI + EKSTRAKSI")
    
    # Scenario 1: Valid commit
    print("\n🔍 Scenario 1: Valid Commit")
    title1 = "feat: implementasi JWT authentication (Taiga #AUTH-555)"
    desc1 = """
Menambahkan sistem autentikasi menggunakan JWT token dengan refresh token mechanism.

Ticket Link: [(Taiga #AUTH-555)] (https://projects.digitaltelkom.id/project/AUTH/us/555)
Documentation Link: [API Specs] (https://swagger.io/docs/auth-api)
Testing Link: [Test Cases] (https://docs.google.com/spreadsheets/auth-tests)
    """
    
    print(f"   Title: {title1}")
    title_result = validate_commit_title(title1)
    ref_result = extract_reference_data(desc1)
    
    if title_result.is_valid:
        print("   ✅ Title Valid")
        print(f"   📦 Project: {title_result.parsed_data['project']}")
        print(f"   🎫 Ticket: #{title_result.parsed_data['ticket_number']}")
    
    if ref_result.ticket_link:
        print(f"   🔗 Ticket URL: {ref_result.ticket_link['url']}")
    
    # Scenario 2: Invalid commit
    print("\n\n🔍 Scenario 2: Invalid Commit")
    title2 = "add authentication (Taiga #AUTH-555)"
    desc2 = """
Ticket Link: [(Taiga #AUTH-555)] (https://projects.digitaltelkom.id/project/AUTH/us/555)
    """
    
    print(f"   Title: {title2}")
    title_result2 = validate_commit_title(title2)
    ref_result2 = extract_reference_data(desc2)
    
    if not title_result2.is_valid:
        print("   ❌ Title Invalid")
        print("   ⚠️  Errors:")
        for error in title_result2.errors[:3]:  # Show first 3 errors
            print(f"      - {error}")
        
        if title_result2.suggestions:
            print("   💡 Suggestion:")
            print(f"      {title_result2.suggestions[0]}")
    
    if ref_result2.ticket_link:
        print(f"   🔗 Ticket URL: {ref_result2.ticket_link['url']}")


def demo_all_allowed_types():
    """Demo semua tipe yang diperbolehkan"""
    print_separator("DEMO 5: SEMUA TIPE YANG DIPERBOLEHKAN")
    
    allowed_types = [
        ('feat', 'menambahkan fitur baru'),
        ('fix', 'memperbaiki bug'),
        ('refactor', 'refactoring code'),
        ('docs', 'update dokumentasi'),
        ('style', 'formatting code style'),
        ('test', 'menambahkan unit test'),
        ('chore', 'maintenance task'),
        ('perf', 'performance improvement'),
        ('ci', 'update CI/CD pipeline'),
        ('build', 'update build configuration'),
        ('revert', 'revert previous commit'),
    ]
    
    print("\n✅ Daftar tipe yang diperbolehkan:\n")
    for tipe, description in allowed_types:
        title = f"{tipe}: {description} (Taiga #TEST-001)"
        result = validate_commit_title(title)
        status = "✅" if result.is_valid else "❌"
        print(f"   {status} {tipe:10s} - {description}")


def demo_interactive():
    """Demo interaktif untuk testing manual"""
    print_separator("DEMO 6: MODE INTERAKTIF")
    print("\nMasukkan commit title untuk divalidasi (ketik 'exit' untuk keluar)")
    print("Contoh: feat: menambahkan fitur login (Taiga #DATB-10353)\n")
    
    while True:
        try:
            title = input("📝 Title: ").strip()
            
            if title.lower() == 'exit':
                print("\n👋 Terima kasih!")
                break
            
            if not title:
                continue
            
            result = validate_commit_title(title)
            
            if result.is_valid:
                print("\n✅ VALID")
                print(f"   Tipe: {result.parsed_data['type']}")
                print(f"   Project: {result.parsed_data['project']}-{result.parsed_data['ticket_number']}")
            else:
                print("\n❌ INVALID")
                print("\n⚠️  Errors:")
                for i, error in enumerate(result.errors, 1):
                    print(f"   {i}. {error}")
                
                if result.suggestions:
                    print("\n💡 Suggestions:")
                    for i, suggestion in enumerate(result.suggestions, 1):
                        print(f"   {i}. {suggestion}")
            
            print()
        
        except KeyboardInterrupt:
            print("\n\n👋 Terima kasih!")
            break


def main():
    """Main function untuk menjalankan semua demo"""
    print("\n" + "="*80)
    print("  COMMIT TITLE VALIDATOR & REFERENCE EXTRACTOR - DEMO")
    print("="*80)
    print("\n📚 Demo ini menampilkan berbagai scenario penggunaan validator")
    
    try:
        demo_valid_titles()
        input("\n\n▶️  Tekan Enter untuk lanjut ke demo berikutnya...")
        
        demo_invalid_titles()
        input("\n\n▶️  Tekan Enter untuk lanjut ke demo berikutnya...")
        
        demo_reference_extraction()
        input("\n\n▶️  Tekan Enter untuk lanjut ke demo berikutnya...")
        
        demo_complete_workflow()
        input("\n\n▶️  Tekan Enter untuk lanjut ke demo berikutnya...")
        
        demo_all_allowed_types()
        input("\n\n▶️  Tekan Enter untuk mode interaktif...")
        
        demo_interactive()
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo dihentikan. Terima kasih!")
    
    print_separator()
    print("\n✨ Demo selesai!")
    print("📝 Untuk menjalankan unit tests, jalankan: python commit_validator_tests.py")
    print()


if __name__ == '__main__':
    main()