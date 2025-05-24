// frontend/repositories/rule/apiRuleRepository.ts
import ApiService from '@/services/api.service'

export interface RuleDTO {
  id: string
  discussion: string
  title: string
  active: boolean
  created_at: string
}

export class APIRuleRepository {
  constructor(private readonly request = ApiService) {}

  async create(
      projectId: string,
      exampleId: number,
      discussionId: string,
      payload: { title: string }): Promise<RuleDTO> {
    const url = `/projects/${projectId}` + `/discussion/examples/${exampleId}` + `/${discussionId}/rules/`
    const res = await this.request.post(url, payload)
    return res.data
  }

  /** opcional – listar todas as regras de uma discussão */
  async list(discussionId: string): Promise<RuleDTO[]> {
    const url = `/projects/${projectId}` + `/discussion/examples/${exampleId}` + `/${discussionId}/rules/`
    const res = await this.request.get(url)
    return Array.isArray(res.data) ? res.data : res.data.results
  }
}
