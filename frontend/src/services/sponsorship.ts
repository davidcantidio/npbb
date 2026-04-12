/**
 * Cliente HTTP do modulo de patrocinados (`/sponsorship`).
 * Em dev, use o proxy Vite (`VITE_API_BASE_URL=/api`) para chegar ao FastAPI.
 */
import { fetchWithAuth, handleApiResponse } from "./http";
import type {
  ContractClauseCreate,
  ContractClauseRead,
  ContractClauseUpdate,
  CounterpartRequirementCreate,
  CounterpartRequirementRead,
  CounterpartRequirementUpdate,
  DeliveryCreate,
  DeliveryEvidenceCreate,
  DeliveryEvidenceRead,
  DeliveryRead,
  DeliveryUpdate,
  GroupMemberCreate,
  GroupMemberRead,
  GroupMemberUpdate,
  OccurrenceResponsibleCreate,
  OccurrenceResponsibleRead,
  OwnerLinkedGroupCreate,
  OwnerType,
  RequirementOccurrenceCreate,
  RequirementOccurrenceRead,
  RequirementOccurrenceUpdate,
  SocialProfileCreate,
  SocialProfileRead,
  SocialProfileUpdate,
  SponsoredInstitutionCreate,
  SponsoredInstitutionRead,
  SponsoredInstitutionUpdate,
  SponsoredPersonCreate,
  SponsoredPersonRead,
  SponsoredPersonUpdate,
  SponsorshipContractCreate,
  SponsorshipContractRead,
  SponsorshipContractUpdate,
  SponsorshipGroupCreate,
  SponsorshipGroupRead,
  SponsorshipGroupUpdate,
} from "../types/sponsorship";

function jsonOptions(token: string, method: string, body?: unknown) {
  return {
    token,
    method,
    headers: { "Content-Type": "application/json" },
    body: body == null ? undefined : JSON.stringify(body),
  } as const;
}

function request<T>(token: string, path: string, method = "GET", body?: unknown): Promise<T> {
  return fetchWithAuth(path, body === undefined ? { token, method } : jsonOptions(token, method, body)).then(
    (res) => handleApiResponse<T>(res),
  );
}

export function listSponsoredPersons(token: string): Promise<SponsoredPersonRead[]> {
  return request(token, "sponsorship/persons");
}

export function getSponsoredPerson(token: string, personId: number): Promise<SponsoredPersonRead> {
  return request(token, `sponsorship/persons/${personId}`);
}

export function createSponsoredPerson(
  token: string,
  body: SponsoredPersonCreate,
): Promise<SponsoredPersonRead> {
  return request(token, "sponsorship/persons", "POST", body);
}

export function updateSponsoredPerson(
  token: string,
  personId: number,
  body: SponsoredPersonUpdate,
): Promise<SponsoredPersonRead> {
  return request(token, `sponsorship/persons/${personId}`, "PATCH", body);
}

export function listPersonGroups(token: string, personId: number): Promise<SponsorshipGroupRead[]> {
  return request(token, `sponsorship/persons/${personId}/groups`);
}

export function createPersonGroup(
  token: string,
  personId: number,
  body: OwnerLinkedGroupCreate,
): Promise<SponsorshipGroupRead> {
  return request(token, `sponsorship/persons/${personId}/groups`, "POST", body);
}

export function listSponsoredInstitutions(token: string): Promise<SponsoredInstitutionRead[]> {
  return request(token, "sponsorship/institutions");
}

export function getSponsoredInstitution(
  token: string,
  institutionId: number,
): Promise<SponsoredInstitutionRead> {
  return request(token, `sponsorship/institutions/${institutionId}`);
}

export function createSponsoredInstitution(
  token: string,
  body: SponsoredInstitutionCreate,
): Promise<SponsoredInstitutionRead> {
  return request(token, "sponsorship/institutions", "POST", body);
}

export function updateSponsoredInstitution(
  token: string,
  institutionId: number,
  body: SponsoredInstitutionUpdate,
): Promise<SponsoredInstitutionRead> {
  return request(token, `sponsorship/institutions/${institutionId}`, "PATCH", body);
}

export function listInstitutionGroups(
  token: string,
  institutionId: number,
): Promise<SponsorshipGroupRead[]> {
  return request(token, `sponsorship/institutions/${institutionId}/groups`);
}

export function createInstitutionGroup(
  token: string,
  institutionId: number,
  body: OwnerLinkedGroupCreate,
): Promise<SponsorshipGroupRead> {
  return request(token, `sponsorship/institutions/${institutionId}/groups`, "POST", body);
}

export function listSocialProfiles(
  token: string,
  ownerType: OwnerType,
  ownerId: number,
): Promise<SocialProfileRead[]> {
  return request(
    token,
    `sponsorship/social_profiles?owner_type=${encodeURIComponent(ownerType)}&owner_id=${ownerId}`,
  );
}

export function createSocialProfile(
  token: string,
  body: SocialProfileCreate,
): Promise<SocialProfileRead> {
  return request(token, "sponsorship/social_profiles", "POST", body);
}

export function updateSocialProfile(
  token: string,
  profileId: number,
  body: SocialProfileUpdate,
): Promise<SocialProfileRead> {
  return request(token, `sponsorship/social_profiles/${profileId}`, "PATCH", body);
}

export function deleteSocialProfile(token: string, profileId: number): Promise<void> {
  return request(token, `sponsorship/social_profiles/${profileId}`, "DELETE");
}

export function listSponsorshipGroups(token: string): Promise<SponsorshipGroupRead[]> {
  return request(token, "sponsorship/groups");
}

export function getSponsorshipGroup(token: string, groupId: number): Promise<SponsorshipGroupRead> {
  return request(token, `sponsorship/groups/${groupId}`);
}

export function createSponsorshipGroup(
  token: string,
  body: SponsorshipGroupCreate,
): Promise<SponsorshipGroupRead> {
  return request(token, "sponsorship/groups", "POST", body);
}

export function updateSponsorshipGroup(
  token: string,
  groupId: number,
  body: SponsorshipGroupUpdate,
): Promise<SponsorshipGroupRead> {
  return request(token, `sponsorship/groups/${groupId}`, "PATCH", body);
}

export function deleteSponsorshipGroup(token: string, groupId: number): Promise<void> {
  return request(token, `sponsorship/groups/${groupId}`, "DELETE");
}

export function listGroupMembers(token: string, groupId: number): Promise<GroupMemberRead[]> {
  return request(token, `sponsorship/groups/${groupId}/members`);
}

export function createGroupMember(
  token: string,
  groupId: number,
  body: GroupMemberCreate,
): Promise<GroupMemberRead> {
  return request(token, `sponsorship/groups/${groupId}/members`, "POST", body);
}

export function updateGroupMember(
  token: string,
  groupId: number,
  memberId: number,
  body: GroupMemberUpdate,
): Promise<GroupMemberRead> {
  return request(token, `sponsorship/groups/${groupId}/members/${memberId}`, "PATCH", body);
}

export function deleteGroupMember(token: string, groupId: number, memberId: number): Promise<void> {
  return request(token, `sponsorship/groups/${groupId}/members/${memberId}`, "DELETE");
}

export function listGroupContracts(
  token: string,
  groupId: number,
): Promise<SponsorshipContractRead[]> {
  return request(token, `sponsorship/groups/${groupId}/contracts`);
}

export function createGroupContract(
  token: string,
  groupId: number,
  body: SponsorshipContractCreate,
): Promise<SponsorshipContractRead> {
  return request(token, `sponsorship/groups/${groupId}/contracts`, "POST", body);
}

export function updateGroupContract(
  token: string,
  groupId: number,
  contractId: number,
  body: SponsorshipContractUpdate,
): Promise<SponsorshipContractRead> {
  return request(token, `sponsorship/groups/${groupId}/contracts/${contractId}`, "PATCH", body);
}

export function listContractClauses(token: string, contractId: number): Promise<ContractClauseRead[]> {
  return request(token, `sponsorship/contracts/${contractId}/clauses`);
}

export function createContractClause(
  token: string,
  contractId: number,
  body: ContractClauseCreate,
): Promise<ContractClauseRead> {
  return request(token, `sponsorship/contracts/${contractId}/clauses`, "POST", body);
}

export function updateContractClause(
  token: string,
  contractId: number,
  clauseId: number,
  body: ContractClauseUpdate,
): Promise<ContractClauseRead> {
  return request(token, `sponsorship/contracts/${contractId}/clauses/${clauseId}`, "PATCH", body);
}

export function deleteContractClause(
  token: string,
  contractId: number,
  clauseId: number,
): Promise<void> {
  return request(token, `sponsorship/contracts/${contractId}/clauses/${clauseId}`, "DELETE");
}

export function listContractRequirements(
  token: string,
  contractId: number,
): Promise<CounterpartRequirementRead[]> {
  return request(token, `sponsorship/contracts/${contractId}/requirements`);
}

export function createContractRequirement(
  token: string,
  contractId: number,
  body: CounterpartRequirementCreate,
): Promise<CounterpartRequirementRead> {
  return request(token, `sponsorship/contracts/${contractId}/requirements`, "POST", body);
}

export function updateContractRequirement(
  token: string,
  contractId: number,
  requirementId: number,
  body: CounterpartRequirementUpdate,
): Promise<CounterpartRequirementRead> {
  return request(
    token,
    `sponsorship/contracts/${contractId}/requirements/${requirementId}`,
    "PATCH",
    body,
  );
}

export function deleteContractRequirement(
  token: string,
  contractId: number,
  requirementId: number,
): Promise<void> {
  return request(token, `sponsorship/contracts/${contractId}/requirements/${requirementId}`, "DELETE");
}

export function listRequirementOccurrences(
  token: string,
  requirementId: number,
): Promise<RequirementOccurrenceRead[]> {
  return request(token, `sponsorship/requirements/${requirementId}/occurrences`);
}

export function createRequirementOccurrence(
  token: string,
  requirementId: number,
  body: RequirementOccurrenceCreate,
): Promise<RequirementOccurrenceRead> {
  return request(token, `sponsorship/requirements/${requirementId}/occurrences`, "POST", body);
}

export function updateRequirementOccurrence(
  token: string,
  requirementId: number,
  occurrenceId: number,
  body: RequirementOccurrenceUpdate,
): Promise<RequirementOccurrenceRead> {
  return request(
    token,
    `sponsorship/requirements/${requirementId}/occurrences/${occurrenceId}`,
    "PATCH",
    body,
  );
}

export function deleteRequirementOccurrence(
  token: string,
  requirementId: number,
  occurrenceId: number,
): Promise<void> {
  return request(token, `sponsorship/requirements/${requirementId}/occurrences/${occurrenceId}`, "DELETE");
}

export function createOccurrenceResponsible(
  token: string,
  occurrenceId: number,
  body: OccurrenceResponsibleCreate,
): Promise<OccurrenceResponsibleRead> {
  return request(token, `sponsorship/occurrences/${occurrenceId}/responsibles`, "POST", body);
}

export function listOccurrenceResponsibles(
  token: string,
  occurrenceId: number,
): Promise<OccurrenceResponsibleRead[]> {
  return request(token, `sponsorship/occurrences/${occurrenceId}/responsibles`);
}

export function deleteOccurrenceResponsible(
  token: string,
  occurrenceId: number,
  responsibleId: number,
): Promise<void> {
  return request(token, `sponsorship/occurrences/${occurrenceId}/responsibles/${responsibleId}`, "DELETE");
}

export function listOccurrenceDeliveries(
  token: string,
  occurrenceId: number,
): Promise<DeliveryRead[]> {
  return request(token, `sponsorship/occurrences/${occurrenceId}/deliveries`);
}

export function createOccurrenceDelivery(
  token: string,
  occurrenceId: number,
  body: DeliveryCreate,
): Promise<DeliveryRead> {
  return request(token, `sponsorship/occurrences/${occurrenceId}/deliveries`, "POST", body);
}

export function updateOccurrenceDelivery(
  token: string,
  occurrenceId: number,
  deliveryId: number,
  body: DeliveryUpdate,
): Promise<DeliveryRead> {
  return request(
    token,
    `sponsorship/occurrences/${occurrenceId}/deliveries/${deliveryId}`,
    "PATCH",
    body,
  );
}

export function deleteOccurrenceDelivery(
  token: string,
  occurrenceId: number,
  deliveryId: number,
): Promise<void> {
  return request(token, `sponsorship/occurrences/${occurrenceId}/deliveries/${deliveryId}`, "DELETE");
}

export function listDeliveryEvidences(
  token: string,
  deliveryId: number,
): Promise<DeliveryEvidenceRead[]> {
  return request(token, `sponsorship/deliveries/${deliveryId}/evidences`);
}

export function createDeliveryEvidence(
  token: string,
  deliveryId: number,
  body: DeliveryEvidenceCreate,
): Promise<DeliveryEvidenceRead> {
  return request(token, `sponsorship/deliveries/${deliveryId}/evidences`, "POST", body);
}
