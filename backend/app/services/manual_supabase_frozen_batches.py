"""Frozen batch specs for manual Supabase lead export (no `lead_pipeline` dependency)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FrozenBatchSpec:
    """Immutable mapping between a user-provided file hash and a batch."""

    file_name: str
    arquivo_sha256: str
    batch_id: int


FROZEN_BATCH_SPECS: tuple[FrozenBatchSpec, ...] = (
    FrozenBatchSpec(
        file_name="1ª Etapa Circuito Brasileiro de Vôlei de Praia - CBVP Adulto.xlsx",
        arquivo_sha256="01f97edac26f2d5f932fc720f16760984ffca0b9f1a00393f292f8cd91e4966f",
        batch_id=188,
    ),
    FrozenBatchSpec(
        file_name="Circuito Banco do Brasil de Surf - CBBS WSL (2).xlsx",
        arquivo_sha256="cc295232c6b9d5fb46822b3943b0aaa798a86e77e7b2a69dc1dd89f8ec788b1b",
        batch_id=187,
    ),
    FrozenBatchSpec(
        file_name="Circuito Banco do Brasil de Surf - CBBS WSL.xlsx",
        arquivo_sha256="ebd69f17ed9343ab891fb252712248439e8be8b5081493a2eb3c5b535ec7c682",
        batch_id=250,
    ),
    FrozenBatchSpec(
        file_name="Copa Brasil.xlsx",
        arquivo_sha256="66ef60f67f35e27351289ff068b841fa151a4d60229883ee70a36121374e8cf6",
        batch_id=115,
    ),
    FrozenBatchSpec(
        file_name="Festival de Verão (2).xlsx",
        arquivo_sha256="7fe278d62a302b0169ef453007bf37d235ddc6002cd402a1c9ccb93fc14b1365",
        batch_id=117,
    ),
    FrozenBatchSpec(
        file_name="Festival de Verão.xlsx",
        arquivo_sha256="ff9ee62d8c72e9fec92a1db99c68b3f6e9ba8ecbf750635fbcadf408d4b5a43e",
        batch_id=118,
    ),
    FrozenBatchSpec(
        file_name="Leads 1ª Etapa BPT João Pessoa.xlsx",
        arquivo_sha256="785bac8c363b13fc3bc0548a895e64469d54e28894ef0b9187150d368d920848",
        batch_id=193,
    ),
    FrozenBatchSpec(
        file_name="Leads 2ª Etapa CBVP João Pessoa.xlsx",
        arquivo_sha256="c35c1e079130397c40b54f6aa35daf79a7b9b739f8faa965f13542939f6f7b46",
        batch_id=252,
    ),
    FrozenBatchSpec(
        file_name="Leads Base expodireto Cotrijal - Diária.xlsx",
        arquivo_sha256="9c25bce675dcd24783cb8fe979ffa3d383cd6e6abc060d536969f10206fe4c8a",
        batch_id=253,
    ),
    FrozenBatchSpec(
        file_name="Opt-in Gilberto Gil - PA.xlsx",
        arquivo_sha256="3d331a50aa336c71a01d426eec31b41b1cad08e66cdb748c52663ab5697f4479",
        batch_id=247,
    ),
    FrozenBatchSpec(
        file_name="Opt-in Gilberto Gil - SP.xlsx",
        arquivo_sha256="c42e72038c3a527d627b0ae21bcb39e66c5b5dea4039c6c4b4ed387a1aa77104",
        batch_id=244,
    ),
    FrozenBatchSpec(
        file_name="Opt-in Gilberto Gil - SSA.xlsx",
        arquivo_sha256="ee4bcbeb873ee05ee43572eb95ff588400a5b2b91ee9eaa6006fd8db8ceafbd5",
        batch_id=248,
    ),
    FrozenBatchSpec(
        file_name="Show Rural Coopavel.xlsx",
        arquivo_sha256="5a89d59605685eb31e2099d57b99024981118f6f0d74958b34e0e42583c2883f",
        batch_id=199,
    ),
    FrozenBatchSpec(
        file_name="Turnê Alceu Valença - RJ - 14-03.xlsx",
        arquivo_sha256="8c014db779bd869c18262ddac577e1d5add5c535606b34b1e34fed7e6f37e986",
        batch_id=245,
    ),
    FrozenBatchSpec(
        file_name="Turnê Alceu Valença - SP - 28-03.xlsx",
        arquivo_sha256="2ddbb81df5fa10a45b822091d07d5e354f47659f021b53b117755f9573f503d1",
        batch_id=246,
    ),
)
