"""
Test tambahan buatan kelompok (Lexer & Parser).

Kategori:
1. Tes Regresi Bug (Perbaikan logika Lexer & Parser)
2. Fitur TODO Spesifikasi (INSERT ... SELECT)
3. Tes Kasus Tepi / Edge Cases (Berdasarkan SPESIFIKASI.md)
"""

import pytest
from crud import ast_nodes as ast
from crud.lexer import tokenize, LexError, TokenType as T
from crud.parser import parse_sql, ParseError


# ==============================================================================
# 1. TES REGRESI BUG & LOGIKA OPERATOR (P1, P2, T3)
# ==============================================================================

def test_regresi_parser_and_lebih_kuat_dari_or():
    """
    P1: AND harus memiliki presedensi lebih tinggi daripada OR.
    Query: a=1 OR b=2 AND c=3
    Ekspektasi AST: OR(a=1, AND(b=2, c=3))
    """
    script = parse_sql("SELECT a FROM t WHERE a=1 OR b=2 AND c=3")
    w = script.statements[0].where
    assert w.op == "OR", f"Akar klausa WHERE harus 'OR', ditemukan {w.op}"
    assert isinstance(w.right, ast.BinaryOp)
    assert w.right.op == "AND", f"Cabang kanan harus 'AND', ditemukan {w.right.op}"


def test_regresi_parser_between_dan_and_diperkuat():
    """
    Penguatan Tes BETWEEN: Memastikan 'AND' milik BETWEEN tidak memakan 'AND' logika.
    """
    sql = "SELECT * FROM produk WHERE harga BETWEEN 1000 AND 5000 AND status = 'aktif'"
    script = parse_sql(sql)
    w = script.statements[0].where
    assert w.op == "AND", "Operator utama WHERE harus AND logika"
    assert isinstance(w.left, ast.Between), "Sisi kiri AND harus berupa node Between"
    assert w.left.negated is False


def test_regresi_lexer_komentar_blok_dengan_bintang_dan_tak_tertutup():
    """
    T3: Cek komentar yang berisi '*' dan pastikan komentar tak tertutup melempar LexError.
    """
    # 1. Komentar berisi bintang di dalamnya
    toks = tokenize("SELECT /* komentar * bintang */ id FROM users")
    assert [t.value for t in toks if t.type != T.EOF] == ["SELECT", "id", "FROM", "users"]

    # 2. Komentar tidak tertutup wajib LexError
    with pytest.raises(LexError) as exc_info:
        tokenize("SELECT * FROM t /* komentar tidak ditutup")
    assert "tidak ditutup" in str(exc_info.value).lower() or "komentar" in str(exc_info.value).lower()


def test_regresi_lexer_posisi_error_baris_dan_kolom():
    """
    Cek penunjukan baris dan kolom yang tepat pada LexError.
    """
    sql = "SELECT id\n  @"  # Karakter @ ada di baris 2, kolom 3
    with pytest.raises(LexError) as exc:
        tokenize(sql)
    assert exc.value.line == 2, f"Harusnya baris 2, ditemukan {exc.value.line}"
    assert exc.value.col == 3, f"Harusnya kolom 3, ditemukan {exc.value.col}"


def test_regresi_parser_panic_mode_dua_statement_rusak():
    """
    P2: Dua statement rusak berturut-turut harus menghasilkan tepat 2 ParseError.
    """
    sql = "SELECT * FROM ; SELECT * FROM ; SELECT id FROM users;"
    script = parse_sql(sql)
    assert len(script.errors) == 2, f"Harus ada 2 error, ditemukan {len(script.errors)}"
    assert len(script.statements) == 1, "Statement valid terakhir harus tetap berhasil di-parse"


def test_regresi_parser_error_statement_terakhir_tanpa_semicolon():
    """
    P2: Error pada statement terakhir yang tidak diakhiri titik koma (';').
    """
    sql = "SELECT id FROM users; SELECT * FROM"
    script = parse_sql(sql)
    assert len(script.errors) == 1
    assert script.errors[0].line == 1 or script.errors[0].line == 2


# ==============================================================================
# 2. IMPLEMENTASI FITUR SPESIFIKASI (TODO T1)
# ==============================================================================

def test_fitur_insert_select_dukungan_spesifikasi():
    """
    TODO(T1): Sintaks INSERT INTO ... SELECT ... sesuai Spesifikasi Bab 3.
    """
    script = parse_sql("INSERT INTO arsip (id) SELECT id FROM pesanan WHERE total > 10")
    assert script.errors == []
    s = script.statements[0]
    assert isinstance(s, ast.Insert)
    assert s.columns == ["id"]
    assert isinstance(s.query, ast.Select)


# ==============================================================================
# 3. TES KASUS TEPI (EDGE CASES BERDASARKAN SPESIFIKASI)
# ==============================================================================

def test_edge_case_file_kosong():
    """Edge Case: Input file kosong atau hanya spasi."""
    script = parse_sql("   \n\t  ")
    assert script.statements == []
    assert script.errors == []


def test_edge_case_semicolon_ganda():
    """Edge Case: Titik koma beruntun (;;) tidak boleh dianggap statement kosong/error."""
    script = parse_sql(";; SELECT id FROM t ;;")
    assert len(script.statements) == 1
    assert script.errors == []


def test_edge_case_komentar_line_tanpa_newline():
    """Edge Case: Komentar satu baris '--' langsung di akhir file tanpa newline."""
    toks = tokenize("SELECT id FROM users -- komentar akhir file")
    assert [t.value for t in toks if t.type != T.EOF] == ["SELECT", "id", "FROM", "users"]


def test_edge_case_pengurangan_beruntun():
    """Edge Case: Operator pengurangan biner dan unar berurutan dengan spasi (a - -b)."""
    script = parse_sql("SELECT a - -b FROM t")
    assert script.errors == [], f"Parse error terdeteksi: {script.errors}"
    expr = script.statements[0].columns[0].expr
    assert isinstance(expr, ast.BinaryOp) and expr.op == "-"
    assert isinstance(expr.right, ast.UnaryOp) and expr.right.op == "-"


# ==============================================================================
# RUNNER SEMENTARA
# ==============================================================================

if __name__ == '__main__':
    tests = [
        test_regresi_parser_and_lebih_kuat_dari_or,
        test_regresi_parser_between_dan_and_diperkuat,
        test_regresi_lexer_komentar_blok_dengan_bintang_dan_tak_tertutup,
        test_regresi_lexer_posisi_error_baris_dan_kolom,
        test_regresi_parser_panic_mode_dua_statement_rusak,
        test_regresi_parser_error_statement_terakhir_tanpa_semicolon,
        test_fitur_insert_select_dukungan_spesifikasi,
        test_edge_case_file_kosong,
        test_edge_case_semicolon_ganda,
        test_edge_case_komentar_line_tanpa_newline,
        test_edge_case_pengurangan_beruntun,
    ]

    print("=" * 65)
    print("      MENJALANKAN TEST TAMBAHAN DIATUR ULANG")
    print("=" * 65)

    passed = 0
    failed = 0

    for test in tests:
        print(f"▶ Running: {test.__name__:<50} ...", end=" ")
        try:
            test()
            print("✅ [PASSED]")
            passed += 1
        except Exception as e:
            print("❌ [FAILED]")
            print(f"   Detail Error: {type(e).__name__} - {e}")
            failed += 1

    print("=" * 65)
    print(f"HASIL AKHIR: {passed} PASSED | {failed} FAILED")
    print("=" * 65)