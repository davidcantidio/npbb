from datetime import date, datetime, timezone

from app.schemas.dashboard import (
    AgeAnalysisFilters,
    AgeAnalysisResponse,
    AgeBreakdown,
    ConsolidadoAgeAnalysis,
    EventoAgeAnalysis,
    FaixaEtariaMetrics,
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


def test_age_analysis_response_serialization():
    payload = AgeAnalysisResponse(
        generated_at=datetime(2026, 3, 6, 12, 0, tzinfo=timezone.utc),
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
                clientes_bb_volume=6,
                clientes_bb_pct=60.0,
                cobertura_bb_pct=90.0,
                faixa_dominante="faixa_26_40",
                faixas=AgeBreakdown(
                    faixa_18_25=FaixaEtariaMetrics(volume=3, pct=30.0),
                    faixa_26_40=FaixaEtariaMetrics(volume=5, pct=50.0),
                    fora_18_40=FaixaEtariaMetrics(volume=2, pct=20.0),
                    sem_info_volume=1,
                    sem_info_pct_da_base=10.0,
                ),
            )
        ],
        consolidado=ConsolidadoAgeAnalysis(
            base_total=10,
            clientes_bb_volume=6,
            clientes_bb_pct=60.0,
            cobertura_bb_pct=90.0,
            faixas=AgeBreakdown(
                faixa_18_25=FaixaEtariaMetrics(volume=3, pct=30.0),
                faixa_26_40=FaixaEtariaMetrics(volume=5, pct=50.0),
                fora_18_40=FaixaEtariaMetrics(volume=2, pct=20.0),
                sem_info_volume=1,
                sem_info_pct_da_base=10.0,
            ),
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
        ),
    )

    data = payload.model_dump(mode="json")

    assert data["version"] == 1
    assert data["filters"]["evento_id"] == 10
    assert data["por_evento"][0]["faixas"]["faixa_26_40"]["volume"] == 5
    assert data["consolidado"]["top_eventos"][0]["evento_nome"] == "Evento Exemplo"
