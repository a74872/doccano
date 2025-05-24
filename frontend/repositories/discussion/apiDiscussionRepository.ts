// frontend/repositories/discussion/apiDiscussionRepository.ts
import ApiService from '@/services/api.service'

export interface DiscussionDTO {
  id?: string
  title: string
  description?: string
  // … quaisquer outros campos que você tenha
}

export class APIDiscussionRepository {
  constructor(private readonly request = ApiService) {}

  // lista todos os tópicos de discussion para um dado project+example
  async list(projectId: string, exampleId: number): Promise<DiscussionDTO[]> {
    const url = `/projects/${projectId}/examples/${exampleId}/discussion/`
    const res = await this.request.get(url)
    // se paginado, res.data.results; senão res.data direto
    return Array.isArray(res.data)
      ? res.data
      : res.data.results
  }

  // criação
  async create(
    projectId: string,
    exampleId: number,
    payload: { title: string }    // só title
  ): Promise<DiscussionDTO> {
    // **IMPORTANTE**: a barra final é necessária
    const url = `/projects/${projectId}/examples/${exampleId}/discussion/`
    const res = await this.request.post(url, payload)
    return res.data
  }


  // apiDiscussionRepository.ts
  async remove (
    projectId: string,
    exampleId: number,
    discussionId: string
  ): Promise<void> {
    const url = `/projects/${projectId}` + `/examples/${exampleId}` + `/discussion/topics/${discussionId}/`

    await this.request.delete(url)
  }

  async patch(
    projectId: string,
    exampleId: number,
    discussionId: string,
    payload: object              // {archived:true}  ou  {is_resolved:true}
  ): Promise<void> {
    const url =
      `/projects/${projectId}` +
      `/examples/${exampleId}` +
      `/discussion/topics/${discussionId}/`
    await this.request.patch(url, payload)
  }


  // bulk archive
  async archive(projectId: string, ids: string[]): Promise<void> {
    const url = `/projects/${projectId}` + `/examples/${exampleId}` + `/discussion/topics/${discussionId}/`
    await this.request.post(url, { ids })
  }
}
