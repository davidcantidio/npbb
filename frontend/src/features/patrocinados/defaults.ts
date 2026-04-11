import type { ContratoPatrocinioInput, ContrapartidaInput, PatrocinadorInput } from "../../types/patrocinados";

export function emptyPatrocinadorInput(): PatrocinadorInput {
  return {
    nome_fantasia: "",
    razao_social: "",
    cnpj: "",
    email: "",
    telefone: "",
    site: "",
    observacoes: "",
    ativo: true,
  };
}

export function emptyContrapartidaInput(): ContrapartidaInput {
  return {
    titulo: "",
    descricao: "",
    categoria: "",
    quantidade: "",
    valor_estimado: "",
    prazo_ou_cumprimento: "",
  };
}

export function emptyContratoInput(): ContratoPatrocinioInput {
  return {
    numero: "",
    titulo: "",
    data_inicio: "",
    data_fim: "",
    valor: "",
    status: "rascunho",
    observacoes: "",
    arquivo_nome: "",
    arquivo_url: "",
  };
}
