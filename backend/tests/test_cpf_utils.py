from app.utils.cpf import is_valid_cpf, normalize_cpf, validate_and_normalize_cpf


def test_normalize_cpf_remove_pontuacao():
    assert normalize_cpf("529.982.247-25") == "52998224725"


def test_is_valid_cpf_true_for_valid_examples():
    assert is_valid_cpf("529.982.247-25") is True
    assert is_valid_cpf("11144477735") is True


def test_is_valid_cpf_false_for_wrong_check_digits():
    assert is_valid_cpf("52998224726") is False


def test_is_valid_cpf_false_for_repeated_digits():
    assert is_valid_cpf("000.000.000-00") is False


def test_is_valid_cpf_false_for_known_placeholder_sequence():
    assert is_valid_cpf("123.456.789-09") is False
    assert is_valid_cpf("12345678909") is False


def test_validate_and_normalize_cpf_returns_digits():
    assert validate_and_normalize_cpf("529.982.247-25") == "52998224725"

