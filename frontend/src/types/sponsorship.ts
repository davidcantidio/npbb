/** Tipos alinhados a API `/sponsorship`. */

export type OwnerType = "person" | "institution";

export type ContractStatus = "active" | "inactive" | "archived";
export type PeriodType = "week" | "month" | "year" | "contract_term" | "custom";
export type ResponsibilityType = "individual" | "collective";
export type RequirementStatus = "planned" | "in_progress" | "fulfilled" | "expired";
export type OccurrenceStatus = "pending" | "in_review" | "delivered" | "validated" | "rejected";
export type EvidenceType = "link" | "file" | "text" | "social_post" | "image" | "other";

export type OwnershipCounters = {
  groups_count: number;
  contracts_count: number;
  social_profiles_count: number;
};

export type SponsoredPersonRoleRead = {
  id: number;
  code: string;
  label: string;
  sort_order: number;
};

export type SponsoredPersonRead = OwnershipCounters & {
  id: number;
  full_name: string;
  cpf: string | null;
  email: string | null;
  phone: string | null;
  role_id: number;
  role: SponsoredPersonRoleRead;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
};

export type SponsoredPersonCreate = {
  full_name: string;
  cpf?: string | null;
  email?: string | null;
  phone?: string | null;
  role_id: number;
  notes?: string | null;
};

export type SponsoredPersonUpdate = Partial<SponsoredPersonCreate>;

export type SponsoredInstitutionRead = OwnershipCounters & {
  id: number;
  name: string;
  cnpj: string | null;
  email: string | null;
  phone: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
};

export type SponsoredInstitutionCreate = {
  name: string;
  cnpj?: string | null;
  email?: string | null;
  phone?: string | null;
  notes?: string | null;
};

export type SponsoredInstitutionUpdate = Partial<SponsoredInstitutionCreate>;

export type SocialProfileRead = {
  id: number;
  owner_type: OwnerType;
  owner_id: number;
  platform: string;
  handle: string;
  url: string | null;
  is_primary: boolean;
  created_at: string;
};

export type SocialProfileCreate = {
  owner_type: OwnerType;
  owner_id: number;
  platform: string;
  handle: string;
  url?: string | null;
  is_primary?: boolean;
};

export type SocialProfileUpdate = {
  platform?: string;
  handle?: string;
  url?: string | null;
  is_primary?: boolean;
};

export type SponsorshipGroupRead = {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string | null;
  members_count: number;
  contracts_count: number;
};

export type SponsorshipGroupCreate = {
  name: string;
  description?: string | null;
};

export type SponsorshipGroupUpdate = Partial<SponsorshipGroupCreate>;

export type OwnerLinkedGroupCreate = SponsorshipGroupCreate & {
  role_in_group?: string | null;
};

export type GroupMemberRead = {
  id: number;
  group_id: number;
  person_id: number | null;
  institution_id: number | null;
  role_in_group: string | null;
  joined_at: string;
  left_at: string | null;
};

export type GroupMemberCreate = {
  group_id?: number;
  person_id?: number | null;
  institution_id?: number | null;
  role_in_group?: string | null;
};

export type GroupMemberUpdate = {
  person_id?: number | null;
  institution_id?: number | null;
  role_in_group?: string | null;
};

export type SponsorshipContractRead = {
  id: number;
  contract_number: string;
  group_id: number;
  start_date: string;
  end_date: string;
  status: ContractStatus;
  file_storage_key: string | null;
  original_filename: string | null;
  file_checksum: string | null;
  uploaded_at: string | null;
  replaced_by_contract_id: number | null;
  created_by_user_id: number | null;
  created_at: string;
  updated_at: string | null;
  clauses_count: number;
  requirements_count: number;
};

export type SponsorshipContractCreate = {
  group_id?: number;
  contract_number: string;
  start_date: string;
  end_date: string;
  status?: ContractStatus;
  file_storage_key?: string | null;
  original_filename?: string | null;
  file_checksum?: string | null;
  uploaded_at?: string | null;
  replaced_by_contract_id?: number | null;
};

export type SponsorshipContractUpdate = {
  end_date?: string;
  status?: ContractStatus;
  file_storage_key?: string | null;
  original_filename?: string | null;
  file_checksum?: string | null;
  uploaded_at?: string | null;
  replaced_by_contract_id?: number | null;
};

export type ContractClauseRead = {
  id: number;
  contract_id: number;
  clause_identifier: string;
  title: string | null;
  clause_text: string | null;
  display_order: number;
  page_reference: string | null;
  created_at: string;
};

export type ContractClauseCreate = {
  contract_id?: number;
  clause_identifier: string;
  title?: string | null;
  clause_text?: string | null;
  display_order?: number;
  page_reference?: string | null;
};

export type ContractClauseUpdate = Partial<Omit<ContractClauseCreate, "contract_id">>;

export type CounterpartRequirementRead = {
  id: number;
  contract_id: number;
  clause_id: number;
  requirement_type: string;
  description: string;
  is_recurring: boolean;
  period_type: PeriodType | null;
  period_rule_description: string | null;
  expected_occurrences: number | null;
  recurrence_start_date: string | null;
  recurrence_end_date: string | null;
  responsibility_type: ResponsibilityType;
  status: RequirementStatus;
  created_at: string;
  updated_at: string | null;
  occurrences_count: number;
};

export type CounterpartRequirementCreate = {
  contract_id?: number;
  clause_id: number;
  requirement_type: string;
  description: string;
  is_recurring?: boolean;
  period_type?: PeriodType | null;
  period_rule_description?: string | null;
  expected_occurrences?: number | null;
  recurrence_start_date?: string | null;
  recurrence_end_date?: string | null;
  responsibility_type?: ResponsibilityType;
  status?: RequirementStatus;
};

export type CounterpartRequirementUpdate = Partial<Omit<CounterpartRequirementCreate, "contract_id">>;

export type RequirementOccurrenceRead = {
  id: number;
  requirement_id: number;
  period_label: string | null;
  due_date: string | null;
  responsibility_type: ResponsibilityType;
  status: OccurrenceStatus;
  validated_by_user_id: number | null;
  validated_at: string | null;
  rejection_reason: string | null;
  internal_notes: string | null;
  created_at: string;
  updated_at: string | null;
};

export type RequirementOccurrenceCreate = {
  requirement_id?: number;
  period_label?: string | null;
  due_date?: string | null;
  responsibility_type?: ResponsibilityType;
  status?: OccurrenceStatus;
  internal_notes?: string | null;
};

export type RequirementOccurrenceUpdate = {
  period_label?: string | null;
  due_date?: string | null;
  responsibility_type?: ResponsibilityType;
  status?: OccurrenceStatus;
  internal_notes?: string | null;
  rejection_reason?: string | null;
};

export type OccurrenceResponsibleRead = {
  id: number;
  occurrence_id: number;
  member_id: number;
  is_primary: boolean;
  role_description: string | null;
};

export type OccurrenceResponsibleCreate = {
  occurrence_id?: number;
  member_id: number;
  is_primary?: boolean;
  role_description?: string | null;
};

export type DeliveryRead = {
  id: number;
  occurrence_id: number;
  description: string;
  observations: string | null;
  delivered_at: string | null;
  created_by_user_id: number | null;
  created_at: string;
  updated_at: string | null;
};

export type DeliveryCreate = {
  occurrence_id?: number;
  description: string;
  observations?: string | null;
};

export type DeliveryUpdate = {
  description?: string;
  observations?: string | null;
};

export type DeliveryEvidenceRead = {
  id: number;
  delivery_id: number;
  evidence_type: EvidenceType;
  url: string | null;
  file_storage_key: string | null;
  description: string | null;
  platform: string | null;
  external_id: string | null;
  posted_at: string | null;
  created_at: string;
};

export type DeliveryEvidenceCreate = {
  delivery_id?: number;
  evidence_type: EvidenceType;
  url?: string | null;
  file_storage_key?: string | null;
  description?: string | null;
  platform?: string | null;
  external_id?: string | null;
  posted_at?: string | null;
};
