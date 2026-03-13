from pathlib import Path

from app.db.metadata import SQLModel
from app.models.models import ConversaoAtivacao, LeadReconhecimentoToken


def test_lp_ativacao_metadata_expoe_tabelas_campos_e_indice_criticos() -> None:
    _ = ConversaoAtivacao
    _ = LeadReconhecimentoToken

    conversao_table = SQLModel.metadata.tables["conversao_ativacao"]
    assert {"id", "ativacao_id", "lead_id", "cpf", "created_at"} <= set(conversao_table.columns.keys())
    assert {index.name for index in conversao_table.indexes} >= {"ix_conversao_ativacao_ativacao_id_cpf"}

    reconhecimento_table = SQLModel.metadata.tables["lead_reconhecimento_token"]
    assert {"token_hash", "lead_id", "evento_id", "expires_at"} <= set(
        reconhecimento_table.columns.keys()
    )
    assert reconhecimento_table.primary_key.columns.keys() == ["token_hash"]


def test_lp_ativacao_revision_continua_rastreando_tabelas_e_indice_da_fundacao() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    revision_path = (
        backend_dir / "alembic" / "versions" / "c5a8d2e1f4b6_add_conversao_ativacao_and_reconhecimento_token.py"
    )

    contents = revision_path.read_text(encoding="utf-8")

    assert "conversao_ativacao" in contents
    assert "lead_reconhecimento_token" in contents
    assert "ix_conversao_ativacao_ativacao_id_cpf" in contents
