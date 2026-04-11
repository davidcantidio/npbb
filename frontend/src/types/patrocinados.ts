/** Tipos provisórios do cadastro comercial de patrocinadores; alinhar com a API quando existir. */

export type ContratoStatus = "rascunho" | "ativo" | "encerrado";

export type Patrocinador = {
  id: string;
  nome_fantasia: string;
  razao_social: string;
  cnpj: string;
  email: string;
  telefone: string;
  site: string;
  observacoes: string;
  ativo: boolean;
  created_at: string;
  updated_at: string;
  contrapartidas: Contrapartida[];
  contratos: ContratoPatrocinio[];
};

export type Contrapartida = {
  id: string;
  patrocinador_id: string;
  titulo: string;
  descricao: string;
  categoria: string;
  quantidade: string;
  valor_estimado: string;
  prazo_ou_cumprimento: string;
  created_at: string;
  updated_at: string;
};

export type ContratoPatrocinio = {
  id: string;
  patrocinador_id: string;
  numero: string;
  titulo: string;
  data_inicio: string;
  data_fim: string;
  valor: string;
  status: ContratoStatus;
  observacoes: string;
  arquivo_nome: string;
  arquivo_url: string;
  created_at: string;
  updated_at: string;
};

export type PatrocinadorListItem = Pick<
  Patrocinador,
  | "id"
  | "nome_fantasia"
  | "razao_social"
  | "cnpj"
  | "email"
  | "ativo"
  | "created_at"
  | "updated_at"
> & {
  contrapartidas_count: number;
  contratos_count: number;
};

export type PatrocinadorInput = Omit<
  Patrocinador,
  "id" | "created_at" | "updated_at" | "contrapartidas" | "contratos"
>;

export type ContrapartidaInput = Omit<
  Contrapartida,
  "id" | "patrocinador_id" | "created_at" | "updated_at"
>;

export type ContratoPatrocinioInput = Omit<
  ContratoPatrocinio,
  "id" | "patrocinador_id" | "created_at" | "updated_at"
>;
