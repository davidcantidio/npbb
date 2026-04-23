from datetime import date, datetime, timezone

from app.schemas.dashboard import (
    AgeAnalysisFilters,
    AgeAnalysisInsights,
    AgeAnalysisResponse,
    AgeBreakdown,
    CompletenessMetrics,
    ConfiancaConsolidado,
    ConsolidadoAgeAnalysis,
    EventoAgeAnalysis,
    FaixaEtariaMetrics,
    LineageMixRow,
    OrigemQualidadeRow,
    TopEventoAgeAnalysis,
)
from app.services.dashboard_service import calculate_age, classify_age_range


def test_calculate_age_and_classify_boundaries():
    reference_date = date(2026, 3, 6)

    scenarios = [
        (date(2008, 3, 6), 18, "faixa_18_25"),
        (date(2001, 3, 6), 25, "faixa_18_25"),
        (date(2000, 3, 6), 26, "faixa_26_40"),
        (date(1986, 3, 6), 40, "faixa_26_40"),
        (date(2009, 3, 6), 17, "fora_18_40"),
        (date(1985, 3, 6), 41, "fora_18_40"),
    ]

    for birth_date, expected_age, expected_range in scenarios:
        age = calculate_age(birth_date, reference_date=reference_date)
        assert age == expected_age
        assert classify_age_range(age) == expected_range


def test_calculate_age_handles_feb_29_birthdays():
    assert calculate_age(date(2008, 2, 29), reference_date=date(2026, 2, 28)) == 17
    assert calculate_age(date(2008, 2, 29), reference_date=date(2026, 3, 1)) == 18


def _sample_breakdown() -> AgeBreakdown:
    return AgeBreakdown(
        faixa_18_25=FaixaEtariaMetrics(volume=3, pct=30.0),
        faixa_26_40=FaixaEtariaMetrics(volume=5, pct=50.0),
        faixa_18_40=FaixaEtariaMetrics(volume=8, pct=80.0),
        fora_18_40=FaixaEtariaMetrics(volume=2, pct=20.0),
        sem_info_volume=1,
        sem_info_pct_da_base=10.0,
    )


def test_age_analysis_response_serialization():
    payload = AgeAnalysisResponse(
        generated_at=datetime(2026, 3, 6, 12, 0, tzinfo=timezone.utc),
        age_reference_date=date(2026, 3, 6),
        filters=AgeAnalysisFilters(
            data_inicio=date(2026, 1, 1),
            data_fim=date(2026, 1, 31),
            evento_id=10,
        ),
        por_evento=[
            EventoAgeAnalysis(
                evento_id=10,
                evento_nome="Evento Exemplo",
                cidade="Brasilia",
                estado="DF",
                base_leads=10,
                base_com_idade_volume=9,
                base_bb_coberta_volume=9,
                leads_proponente=4,
                leads_ativacao=6,
                leads_canal_desconhecido=0,
                clientes_bb_volume=6,
                clientes_bb_pct=60.0,
                nao_clientes_bb_volume=3,
                nao_clientes_bb_pct=30.0,
                bb_indefinido_volume=1,
                cobertura_bb_pct=90.0,
                faixa_dominante="faixa_26_40",
                faixa_dominante_status="resolved",
                faixas=_sample_breakdown(),
            )
        ],
        consolidado=ConsolidadoAgeAnalysis(
            base_total=10,
            base_com_idade_volume=9,
            base_bb_coberta_volume=9,
            leads_proponente=4,
            leads_ativacao=6,
            leads_canal_desconhecido=0,
            clientes_bb_volume=6,
            clientes_bb_pct=60.0,
            nao_clientes_bb_volume=3,
            nao_clientes_bb_pct=30.0,
            bb_indefinido_volume=1,
            cobertura_bb_pct=90.0,
            faixas=_sample_breakdown(),
            top_eventos=[
                TopEventoAgeAnalysis(
                    evento_id=10,
                    evento_nome="Evento Exemplo",
                    base_leads=10,
                    faixa_dominante="faixa_26_40",
                )
            ],
            media_por_evento=10.0,
            mediana_por_evento=10.0,
            concentracao_top3_pct=100.0,
            faixa_dominante_status="resolved",
        ),
        qualidade_consolidado=CompletenessMetrics(
            base_vinculos=10,
            sem_cpf_volume=0,
            sem_cpf_pct=0.0,
            sem_data_nascimento_volume=1,
            sem_data_nascimento_pct=10.0,
            sem_nome_completo_volume=0,
            sem_nome_completo_pct=0.0,
        ),
        qualidade_por_origem=[
            OrigemQualidadeRow(
                source_kind="ativacao",
                label="Ativacao (captacao)",
                base_vinculos=10,
                sem_cpf_volume=0,
                sem_cpf_pct=0.0,
                sem_data_nascimento_volume=1,
                sem_data_nascimento_pct=10.0,
                sem_nome_completo_volume=0,
                sem_nome_completo_pct=0.0,
            )
        ],
        confianca_consolidado=ConfiancaConsolidado(
            base_vinculos=10,
            base_com_idade_volume=9,
            base_bb_coberta_volume=9,
            dedupe_candidate_volume=11,
            dedupe_suppressed_volume=1,
            dedupe_suppressed_pct=9.09,
            event_name_candidate_volume=2,
            ambiguous_event_name_volume=1,
            ambiguous_event_name_pct=50.0,
            event_name_missing_volume=0,
            event_name_missing_pct=0.0,
            evento_nome_backfill_habilitado=True,
            lineage_mix=[
                LineageMixRow(
                    source_kind="ativacao",
                    label="Ativacao (captacao)",
                    volume=10,
                    pct=100.0,
                )
            ],
        ),
        insights=AgeAnalysisInsights(resumo=["Resumo de teste."], alertas=[], flags=["bb_coverage_low"]),
    )

    data = payload.model_dump(mode="json")

    assert data["version"] == 2
    assert data["age_reference_date"] == "2026-03-06"
    assert data["filters"]["evento_id"] == 10
    assert data["por_evento"][0]["faixas"]["faixa_26_40"]["volume"] == 5
    assert data["por_evento"][0]["faixas"]["faixa_18_40"]["volume"] == 8
    assert data["por_evento"][0]["base_com_idade_volume"] == 9
    assert data["consolidado"]["top_eventos"][0]["evento_nome"] == "Evento Exemplo"
    assert data["confianca_consolidado"]["dedupe_suppressed_volume"] == 1
    assert data["confianca_consolidado"]["lineage_mix"][0]["source_kind"] == "ativacao"
    assert data["insights"]["resumo"][0] == "Resumo de teste."
    assert data["insights"]["flags"] == ["bb_coverage_low"]
